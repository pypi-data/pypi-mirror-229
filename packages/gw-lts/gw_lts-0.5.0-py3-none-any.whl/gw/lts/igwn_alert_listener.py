#!/usr/bin/env python3

import json
import logging
import io

from igwn_alert.client import client as IGWNAlertClient

from ligo.lw import ligolw
from ligo.lw import lsctables
from ligo.lw import utils as ligolw_utils
from ligo.lw.ligolw import ElementError

from collections import OrderedDict, deque

from ligo.scald.io import kafka

from lal import GPSTimeNow

from gw.lts import utils
from gw.lts.utils.gracedb_helper import GraceDbHelper


class LIGOLWContentHandler(ligolw.LIGOLWContentHandler):
    pass


lsctables.use_in(LIGOLWContentHandler)


def parse_command_line():
    parser = utils.add_general_opts()
    parser.add_option(
        "--gracedb-topics",
        metavar="string",
        action="append",
        help="GraceDb topics to subscribe to. Can be given multiple times.",
    )
    parser.add_option(
        "--gracedb-submitter",
        metavar="string",
        help=(
            "GraceDb submitter to filter events by. "
            "Events submitted by another user are ignored."
        ),
    )
    parser.add_option(
        "--gracedb-search",
        metavar="string",
        help=(
            "Search to get gracedb events from, eg AllSky or EarlyWarning"
        ),
    )
    parser.add_option(
        "--injection-channel",
        metavar="channel",
        action="append",
        help=(
            "Name of strain channels to process injections from. "
            "Can be given multiple times."
        ),
    )
    parser.add_option(
        "--max-wait-time",
        metavar="float",
        default=3600.0,
        help=(
            "Max amount of time to keep events before removing them, "
            "whether or not a message has been sent"
        ),
    )
    opts, args = parser.parse_args()
    return opts, args


def main():
    # parse command line
    opts, args = parse_command_line()

    # set up logging
    utils.set_up_logger(opts.verbose)

    # set up listener
    listener = on_alert(opts.tag, opts.kafka_server,
                        opts.gracedb_server, opts.gracedb_search,
                        opts.gracedb_submitter, opts.max_wait_time,
                        opts.injection_channel)

    # initialize a client and listener
    client = IGWNAlertClient(group=opts.gracedb_server)

    client.listen(listener.process_alert, opts.gracedb_topics)


class on_alert(object):
    """
    Listener to receive igwn-alerts and produce output
    messages to Kafka.

    Parameters
    ----------
    tag (str)
        unique identifier to be used in the Kafka
        broker name and output topic names.
    kafka_server (str)
        server url that Kafka is hosted on.
    gracedb_server (str)
        name of the GraceDB client to receive igwn-alerts
        from. gracedb, gracedb-playground, or gracedb-test.
    gracedb_search (str)
        tag to identify which search activity to process
        events from. eg AllSky, EarlyWarning, etc.
    gracedb_submitter (str)
        GraceDb submitter to process events from.
    max_wait_time (float)
        maximum amount of time to keep events in memory
        before dropping them.
    injection_channel (str)
        Name of the strain channels from which to
        process injections.
    """
    def __init__(self, tag, kafka_server,
                 gracedb_server, gracedb_search, gracedb_submitter,
                 max_wait_time, injection_channel):
        self.tag = tag
        self.kafka_server = kafka_server
        self.gracedb_client = GraceDbHelper(gracedb_server)
        self.search = gracedb_search
        self.submitter = gracedb_submitter
        self.max_wait_time = max_wait_time
        self.inj_channels = set(list(injection_channel))

        # set up producer
        self.client = kafka.Client(f"kafka://{self.tag}@{self.kafka_server}")

        self.events = OrderedDict()
        self.events_sent = deque(maxlen=300)

        logging.info("Initialized on_alert class.")

    def process_alert(self, topic=None, payload=None):
        """
        Processes alerts received from igwn-alert.

        Parse the alert payload and process alerts
        associated with new or updated events only
        from the channel names, submitter, and search
        specified.

        Parameters
        ----------
        topic (str)
            topic from which alert was received
        payload (str)
            alert payload
        """
        # unpack alert payload
        payload = json.loads(payload)
        id = payload["uid"]
        alert_type = payload["alert_type"]
        data = payload["data"]

        # only need to process new or update type alerts
        if alert_type not in ("new", "update"):
            logging.info(f"Received {alert_type}, skipping")
            return

        # first get the event uid and event level data
        # we have to do this slightly differently for
        # superevent alerts vs event alerts
        if id.startswith("S"):
            uid = data["preferred_event"]
            event_data = data["preferred_event_data"]
            datasource = "superevents"

            logging.info(
                f"Received {alert_type} alert for {id} " +
                f"from {datasource}, preferred event: {uid}"
            )
        else:
            uid = id
            event_data = data
            datasource = data["pipeline"]

            logging.info(f"Received {alert_type} alert for {uid}" +
                         f"from {datasource}")

        # now that we have the uid for a specific event,
        # check the channels this event comes from. skip
        # if not from injection channels
        channels = self.get_channels(uid)
        if not channels or not channels.issubset(self.inj_channels):
            logging.debug(f"{uid} not from injection channels, skipping.")
            return

        # filter events by search
        search = event_data["search"]
        if not event_data["search"] == self.search:
            logging.info(f"Skipping {search} event...")

        # filter events by submitter if provided
        submitter = event_data["submitter"]
        if self.submitter and not submitter == self.submitter:
            logging.info(f"skipping event {uid} submitted by {submitter}")
            return

        # get event object, this has some info not
        # included in the alert payload
        event = self.gracedb_client.get_event(uid=uid)

        # construct event data to be sent in kafka messages
        if uid in self.events.keys():
            self.events[uid] = (self.process_event(
                uid, event, output=self.events[uid])
            )
        else:
            self.events[uid] = self.process_event(uid, event)

        # check if all elements present, then send msg
        # only send msg once per event
        topic = f"{datasource}.{self.tag}.testsuite.inj_events"
        for uid, data in self.events.items():
            if all(data.values()) and uid not in self.events_sent:
                logging.info(
                    f'sending a message for {uid} (coa time: {data["time"]}).'
                )
                self.client.write(topic, data)
                self.events_sent.append(uid)

        # clean out old events that already had a msg sent
        time_now = float(GPSTimeNow())
        for key, value in list(self.events.items()):
            if time_now - value["time_added"] >= self.max_wait_time:
                logging.debug(f"Removing old event: {key}")
                self.events.pop(key)

    def process_event(self, uid, event, output={}):
        """
        Parameters
        ----------
        uid (str)
            event grace id to process
        event (json)
            gracedb event object
        output (dict)
            event data to update. Optional,
            default is an empty dict.

        Returns
        ----------
            dict, output data to send to Kafka
            output = {
                "time": coinc end time,
                "time_ns": coinc end time ns,
                "snr": network snr,
                "far": coinc combined far,
                "coinc": coinc file object,
                "latency": gracedb upload latency,
                "pipeline": event pipeline,
                "uid": event grace id,
                "time_added": time event processed,
            }
        """
        required_params = (
            "time", "time_ns", "snr", "far",
            "coinc", "latency", "pipeline")
        if not output:
            # initialize all the items we need in order to send a message
            for k in required_params:
                output.update({k: None})
            output.update({"time_added": float(GPSTimeNow())})

        output.update(
            {
                "uid": uid,
                "latency": event["reporting_latency"],
                "pipeline": event["pipeline"],
            }
        )
        output.update(self.add_coinc(uid))

        return output

    def add_coinc(self, uid, output={}):
        """
        Download coinc file object from GraceDB,
        parse the file for relevant info, and add
        data to the output dict.

        Parameters
        ----------
        uid (str)
            event grace id to process
        output (dict)
            event data to update. Optional,
            default is an empty dict.

        Returns
        ----------
            dict, output data to send to Kafka
        """
        coinc = self.get_filename(uid, "coinc.xml")
        if coinc:
            try:
                xmldoc = utils.load_xml(coinc)
                coinctable = lsctables.CoincInspiralTable.get_table(xmldoc)
            except ElementError as error:
                logging.warning(
                    f"Failed to parse coinc file from {uid}. Error: {error}"
                )
            else:
                coinc_msg = io.BytesIO()
                ligolw_utils.write_fileobj(xmldoc, coinc_msg)

                output.update(
                    {
                        "time": coinctable[0].end_time,
                        "time_ns": coinctable[0].end_time_ns,
                        "snr": coinctable[0].snr,
                        "far": coinctable[0].combined_far,
                        "coinc": coinc_msg.getvalue().decode(),
                    }
                )
                logging.debug(f"Added coinc.xml to {uid}")
        return output

    def get_channels(self, uid):
        """
        Download coinc file object from a gracedb
        event and parse it for the strain channel
        name(s).

        Parameters
        ----------
        uid (str)
            event grace id to process

        Returns
        ----------
        channels (set)
            set of channel names, or None
        """
        channels = None
        coinc = self.get_filename(uid, "coinc.xml")
        if coinc:
            try:
                xmldoc = utils.load_xml(coinc)
                sngltable = lsctables.SnglInspiralTable.get_table(xmldoc)
                channels = set(list(sngltable.getColumnByName("channel")))
            except ElementError as error:
                logging.warning(
                    f"Failed to parse coinc file from {uid}. Error: {error}"
                )
            return channels
        return None

    def get_filename(self, uid, filename, retries=10):
        """
        Download file from Gracedb.

        Parameters
        ----------
        uid (str)
            event grace id to process
        filename (str)
            name of file to download
        retries (int)
            number of times to attempt
            download, default is 10.

        Returns
        ----------
        file (requests.models.Response)
            requests.models.Response object or None
        """
        this_try = 0
        while this_try < retries:
            file = self.gracedb_client.query_file(uid, filename)
            if file:
                return file
            else:
                this_try += 1
        logging.debug(f"Failed to download {filename} from {uid}.")
        return None


if __name__ == "__main__":
    main()
