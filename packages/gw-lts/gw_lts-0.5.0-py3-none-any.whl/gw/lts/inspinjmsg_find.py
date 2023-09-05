#!/usr/bin/env python3

import os
import io
import json
import copy
import logging

from collections import defaultdict, deque

from cronut import App

from ligo.lw import ligolw
from ligo.lw import lsctables
from ligo.lw import utils as ligolw_utils

from lal import GPSTimeNow

from ligo.scald.io import kafka

from gw.lts import utils


def parse_command_line():
    parser = utils.add_general_opts()
    parser.add_option(
        "--preferred-param",
        default="ifar",
        help=(
            "Parameter to use to determine preferred events in the case "
            "that multiple event messages are found for a single injection. "
            "Supported options are ifar (default) or snr"
        ),
    )
    opts, args = parser.parse_args()

    return opts, args


class InspInjMsgFind(object):
    """
    Job service for ingesting event and injection
    messages from Kafka. Incoming messages are
    paired by event time and then bundled into
    an output message sent to Kafka.

    Parameters
    ----------
    tag (str)
        unique identifier to be used in the Kafka
        broker name and output topic names.
    kafka_server (str)
        server url that Kafka is hosted on.
    input_topic (str)
        Kafka topics to subscribe to.
    preferred_param (str)
        ifar (default) or snr. Parameter used to
        choose one event when multiple are received
        for a given injection.
    verbose (bool)
        be verbose.

    """
    def __init__(self, tag, kafka_server, input_topic,
                 preferred_param="ifar", verbose=False):
        self.tag = tag
        self.kafka_server = kafka_server
        self.topics = input_topic
        self.preferred_param = preferred_param
        self.verbose = verbose

        # initialize data deques
        # if injections come every ~20 seconds this should correspond
        # to keeping messages for about 3-4 minutes.
        self.maxlen = 10
        self.event_msgs = defaultdict(lambda: deque(maxlen=self.maxlen))
        self.inj_msgs = defaultdict(lambda: deque(maxlen=self.maxlen))

        # set up producer
        self.client = kafka.Client(f"kafka://{self.tag}@{self.kafka_server}")

        # create a job service using cronut
        self.app = App(
            "inspinjmsg_find",
            broker=f"kafka://{self.tag}_inspinjmsg_find@{self.kafka_server}",
        )

        @self.app.process(self.topics)
        def process(message):
            """
            Process incoming messages.

            Parameters
            ----------
            message (str)
                message payload
            """
            mdatasource, mtag, mtopic = utils.parse_msg_topic(message)

            # unpack data from the message
            if mtopic == "inj_events":
                # parse event info
                event = json.loads(message.value())

                # load the coinc table and
                # get event coalescence time
                coinc_file = utils.load_xml(event["coinc"])
                coinctable = lsctables.CoincInspiralTable.get_table(coinc_file)
                coincrow = coinctable[0]
                coinctime = (coincrow.end_time +
                             coincrow.end_time_ns * 10.0**-9.0)

                # keep track of the preferred parameter
                # for this event
                val = self.get_preferred_param(coinctable)

                dict = {
                    "time": coinctime,
                    "coinc": coinc_file,
                    "msg_time": int(GPSTimeNow()),
                    "preferred_param": val,
                }

                logging.info(
                    f"received {mdatasource} event with coalescence time: " +
                    f"{coinctime} and {self.preferred_param} = {val}"
                )

                # if there is already an event at the same time
                # check if this one is preferred, and only keep
                # the best event in the deque to process
                nearest_event = utils.find_nearest_msg(
                    self.event_msgs[mdatasource], coinctime
                )
                if nearest_event:
                    logging.info("Found previous event within " +
                                 "1 sec of this event.")
                    if val > nearest_event["preferred_param"]:
                        logging.info(
                            "New event is preferred, removing previous."
                        )
                        self.event_msgs[mdatasource].remove(nearest_event)
                    else:
                        logging.info(
                            "Previous event is preferred, skipping."
                        )
                        return
                else:
                    logging.info(
                        "No previous event within 1 sec of this event.")

                # add optional keys - these may or may not
                # already be present depending on the data
                # source configuration
                for key in ("latency", "p_astro", "uid", "pipeline"):
                    try:
                        dict.update({key: event[key]})
                    except KeyError:
                        dict.update({key: None})
                # add far class
                far_string = utils.far_string(float(coincrow.combined_far))
                dict.update({"farstring": far_string})
                logging.debug(
                    f"combined far: {coincrow.combined_far} | " +
                    f"far string: {far_string}"
                )

                # store event data in the deque
                self.event_msgs[mdatasource].append(dict)

                # process the events in the deque
                self.process_events(mdatasource)

            elif mtopic == "inj_stream":
                # parse inj info
                injection = json.loads(message.value())
                ifos = injection["onIFOs"]

                # load the sim table
                simfile = utils.load_xml(injection["sim"])
                simrow = lsctables.SimInspiralTable.get_table(simfile)[0]

                # get injection coalescence time
                simtime = (simrow.geocent_end_time +
                           simrow.geocent_end_time_ns * 10.0**-9)
                logging.info(
                    f"received {mdatasource} injection " +
                    f"with coalescence time: {simtime}"
                )

                # store inj data
                self.inj_msgs[mdatasource].append(
                    {
                        "time": simtime,
                        "sim": simfile,
                        "ifos": ifos,
                        "preferred_event": None,
                    }
                )

                # process the events in the deque and then
                # check for stale msgs
                self.process_events(mdatasource)
                self.process_stale_msgs(mdatasource)

            else:
                raise ValueError(
                    "Found unexpected message from topic {mtopic}."
                )

    def start(self):
        """
        Start job service.
        """
        # start up
        logging.info("Starting up...")
        self.app.start()

    def append_sim_table(self, coinc_file, sim_file):
        """
        Append injection SimInspiral Table to the event
        coinc file object.
        """
        # init a new sim inspiral table
        this_sim_table = lsctables.SimInspiralTable.get_table(sim_file)
        coinc_file.childNodes[-1].appendChild(this_sim_table)

        return coinc_file

    def write_sim_file(self, sim, xmldoc):
        """
        Write a ligolw file object including the
        injection SimInspiral Table
        """
        # open a new xml doc
        sim_msg = io.BytesIO()
        ligolw_elem = xmldoc.appendChild(ligolw.LIGO_LW())

        output_simtable = ligolw_elem.appendChild(
            lsctables.New(lsctables.SimInspiralTable)
        )
        this_sim_table = lsctables.SimInspiralTable.get_table(sim)
        output_simtable.extend(this_sim_table)
        ligolw_utils.write_fileobj(xmldoc, sim_msg)

        return sim_msg

    def construct_event_ouput(self, xmldoc, event, injection, key=None):
        """
        Construct output message payload to be sent
        to Kafka.

        Parameters
        ----------
        xmldoc (ligolw document)
            event coinc file object
        event (dict)
            event json packet
        injection (dict)
            injection json packet
        key (str)
            optional tag used in writing files
            to disk, default is None.
        """
        filename = (
            f'coinc-{int(event["time"])}.xml'
            if not key
            else f'{key}-coinc-{int(event["time"])}.xml'
        )

        coinc = event["coinc"]
        coincrow = lsctables.CoincInspiralTable.get_table(coinc)[0]
        simrow = lsctables.SimInspiralTable.get_table(coinc)[0]

        ligolw_utils.write_filename(
            xmldoc, os.path.join("coincs", filename), verbose=self.verbose
        )
        coinc_msg = io.BytesIO()
        ligolw_utils.write_fileobj(xmldoc, coinc_msg)

        output = {
            "time": simrow.geocent_end_time,
            "time_ns": simrow.geocent_end_time_ns,
            "snr": coincrow.snr,
            "far": coincrow.combined_far,
            "p_astro": event["p_astro"],
            "coinc": coinc_msg.getvalue().decode(),
            "latency": event["latency"],
            "uid": event["uid"],
            "onIFOs": injection["ifos"],
            "pipeline": event["pipeline"],
        }

        return output

    def process_events(self, datasource):
        """
        For each event in the event_msgs deque, find the nearest injection
        in inj_msgs within +/- delta_t (1 second) of the event coalescence
        time. When an association is made, check to see if its better than
        any previous event found. If so, add the sim inspiral table from
        injection to the event's coinc xml and send a message to the
        testsuite.events topic and remove the processed event from the
        deque.
        """
        events_copy = copy.copy(self.event_msgs[datasource])
        injections = self.inj_msgs[datasource]

        for event in events_copy:
            event_time = event["time"]
            nearest_inj = utils.find_nearest_msg(injections, event_time)

            # if no associated injection was found, continue
            if not nearest_inj:
                logging.info(f"No injection found for event at {event_time}")
                continue

            inj_idx = self.inj_msgs[datasource].index(nearest_inj)
            inj_time = nearest_inj["time"]
            sim_file = nearest_inj["sim"]
            prev_preferred_event = nearest_inj["preferred_event"]
            coinc_file = event["coinc"]
            this_coinc = lsctables.CoincInspiralTable.get_table(coinc_file)
            val = self.get_preferred_param(this_coinc)

            # if this is the first event found or
            # this event is better than the previous,
            # send update event.
            # Note: this requires that aggregate by
            # "latest" works the way we would hope
            if not prev_preferred_event or val > prev_preferred_event:
                # update preferred event for this injection
                injections[inj_idx].update({"preferred_event": val})

                # proceed with sending event
                # add sim table to coinc file and write to disk
                logging.info(
                    f"Sending event with {self.preferred_param} = {val} " +
                    f"for injection at time {inj_time}"
                )
                newxmldoc = self.append_sim_table(coinc_file, sim_file)
                output = self.construct_event_ouput(
                                                    newxmldoc,
                                                    event, nearest_inj
                )

                topic = f"{datasource}.{self.tag}.testsuite.events"
                self.client.write(topic, output, tags=event["farstring"])
                logging.info(f'Sent msg to: {topic} | ' +
                             f'far string: {event["farstring"]}')

                # finally remove event from the deque
                self.event_msgs[datasource].remove(event)

    def process_stale_msgs(self, datasource):
        """
        process old messages (either messages that are about to be
        removed from the left of the deque, or have been in the deque
        for 2 hours) and send a message with the necessary info
        this is necessary in the case that:
            * we receive an event from the search which is not
            associated with an injection, ie a glitch or real gw
            candidate.
            * there is an injection for which we never receive
            an associated event from the search. ie the injection
            was not recovered at even the GDB far threshold.
        """
        stale_inj = self.stale_msgs(self.inj_msgs[datasource])
        if stale_inj:
            if not stale_inj["preferred_event"]:
                sim_inspiral = stale_inj["sim"]
                logging.info(
                    f'Sending {datasource} missed injection msg ' +
                    f'for injection {stale_inj["time"]}'
                )
                simrow = lsctables.SimInspiralTable.get_table(sim_inspiral)[0]
                newxmldoc = ligolw.Document()
                sim_msg = self.write_sim_file(sim_inspiral, newxmldoc)

                output = {
                    "time": simrow.geocent_end_time,
                    "time_ns": simrow.geocent_end_time_ns,
                    "sim": sim_msg.getvalue().decode(),
                    "onIFOs": stale_inj["ifos"],
                }

                farstring = "None"

                topic = f"{datasource}.{self.tag}.testsuite.missed_inj"
                self.client.write(topic, output, tags=farstring)
                logging.info(f"Sent msg to: {topic}")
                newxmldoc.unlink()
            else:
                logging.debug(
                    f'Injection at time {stale_inj["time"]} ' +
                    'to be removed from the deque.'
                )

        stale_event = self.stale_msgs(self.event_msgs[datasource])
        if stale_event:
            logging.info(
                f'{datasource} event from time {stale_event["time"]} ' +
                'to be removed from the queue - no associated injection found'
            )

    def stale_msgs(self, deque):
        """
        Determine if there are stale messages
        in the queue to be removed.
        """
        # FIXME dont hardcode wait time
        if deque and (len(deque) == self.maxlen
                      or float(GPSTimeNow()) - deque[0]["time"] >= 7200.0):
            return deque[0]

    def get_preferred_param(self, coinc):
        """
        Parse coinc file object for the preferred
        parameter (either ifar or snr).
        """
        # get preferred param value for this event
        if self.preferred_param == "ifar":
            # IFAR
            val = 1.0 / coinc.getColumnByName("combined_far")[0]
        elif self.preferred_param == "snr":
            val = coinc.getColumnByName(self.preferred_param)[0]
        else:
            raise NotImplementedError

        return val


def main():
    # parse options from command line
    opts, args = parse_command_line()

    # set up logging
    utils.set_up_logger(opts.verbose)

    # set up dir for output coincs
    try:
        os.mkdir("coincs")
    except OSError:
        pass

    # initialize the processor
    processor = InspInjMsgFind(opts.tag, opts.kafka_server, opts.input_topic,
                               opts.preferred_param, opts.verbose)
    processor.start()


if __name__ == "__main__":
    main()
