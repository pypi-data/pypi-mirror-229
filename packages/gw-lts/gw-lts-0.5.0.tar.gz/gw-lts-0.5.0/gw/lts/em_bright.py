#!/usr/bin/env python3

import json
import logging
import copy

from collections import deque

from cronut import App

from gw.lts import utils
from gw.lts.utils import influx_helper
from gw.lts.utils.gracedb_helper import GraceDbHelper

from ligo.scald.io import kafka

from ligo.lw import lsctables

from ligo.em_bright import computeDiskMass


def parse_command_line():
    parser = utils.add_general_opts()
    opts, args = parser.parse_args()

    return opts, args


class EMBright(object):
    def __init__(self, options):
        self.tag = options.tag
        self.kafka_server = options.kafka_server

        # set up producer
        self.client = kafka.Client(f"kafka://{self.tag}@{self.kafka_server}")

        self.gracedb_helper = GraceDbHelper(options.gracedb_server)

        # initialize output dict
        self.events = deque(maxlen=50)

        # initialize influx helper to write out trigger data
        self.influx_helper = influx_helper.InfluxHelper(
            config_path=options.scald_config,
            routes={
                "embright": {"aggregate": "min"},
            },
        )

        # create a job service using cronut
        self.app = App(
            "em_bright",
            broker=f"kafka://{self.tag}_em_bright@{self.kafka_server}"
        )

        # subscribes to a topic
        @self.app.process(options.input_topic)
        def process(message):
            mdatasource, mtag, mtopic = utils.parse_msg_topic(message)
            farstring = utils.parse_msg_key(message)
            logging.info(f"Read message from {mdatasource} {mtopic}.")

            # parse message value
            event = json.loads(message.value())
            event.update(
                {
                    "datasource": mdatasource,
                    "farstring": farstring,
                }
            )

            response = self.process_event(event)
            if not response:
                # keep track of events that failed
                # to get a em_bright on the first try
                # this can happen if the embright isnt
                # uploaded immediately
                times = [e["time"] for e in self.events]
                if not event["time"] in times:
                    self.events.append(event)

            # iterate over events and try again to grab a
            # em_bright for each one. On success, remove
            # the event from the deque
            for e in copy.deepcopy(self.events):
                response = self.process_event(e)
                if response:
                    self.events.remove(e)

    def start(self):
        # start up
        logging.info("Starting up...")
        self.app.start()

    def process_event(self, event):
        uid = event["uid"]
        if uid:
            file = self.gracedb_helper.query_file(uid,
                                                  filename="em_bright.json")
        else:
            logging.warning("Received event with unknown Grace ID, skipping.")
            return

        if file:
            em_bright_dict = json.loads(file.read())
            logging.info(f'Received em_bright.json from event {uid}')
        else:
            logging.info(f'Failed to receive em_bright.json from {uid}')
            em_bright_dict = None

        if em_bright_dict:
            output = {}
            time = event["time"]
            datasource = event["datasource"]
            farstring = event["farstring"]

            # determine source from inspiral table
            coinc_file = utils.load_xml(event["coinc"])
            simtable = lsctables.SimInspiralTable.get_table(coinc_file)
            simrow = simtable[0]
            source = utils.source_tag(simtable)

            # get masses and spins to use in computing the disk mass
            mass1 = simrow.mass1
            mass2 = simrow.mass2
            spin1z = simrow.spin1z
            spin2z = simrow.spin2z

            M_rem = computeDiskMass.computeDiskMass(
                mass1,
                mass2,
                spin1z,
                spin2z,
                eosname="2H",
                kerr=False,
                R_ns=None,
                max_mass=None,
            )
            hasNS = "True" if M_rem else "False"

            # construct output
            trigger_dict = self._new_trigger()
            trigger_dict["combined_far"] = event["far"]
            trigger_dict["m1"] = simrow.mass1
            trigger_dict["m2"] = simrow.mass2
            trigger_dict["M_rem"] = M_rem

            for key, value in em_bright_dict.items():
                output[f"p_{key}"] = {"time": [time], "data": [value]}
                trigger_dict[f"p_{key}"] = value

            logging.debug(
                f"Source: {source} | Remnant disk mass: {M_rem} | " +
                f"hasNS: {hasNS}"
            )

            # send time series data to kafka
            for topic, data in output.items():
                topic = f"{datasource}.{self.tag}.testsuite.{topic}"
                self.client.write(
                    topic, data, tags=[farstring, source, hasNS],
                )
                logging.info(f"Sent output message to output topic: {topic}.")

            # store trigger data to influx
            self.influx_helper.store_triggers(
                time,
                trigger_dict,
                route="embright",
                tags=(farstring, source, hasNS),
            )

            return True

        else:
            return False

    @staticmethod
    def _new_trigger():
        dict = {}
        columns = (
            "combined_far",
            "m1",
            "m2",
            "M_rem",
            "p_HasNS",
            "p_HasRemnant",
        )
        for col in columns:
            dict[col] = None

        # we will initialize the combined far value to
        # an arbitrary high value which will get replaced
        # with the actual far from events
        dict["combined_far"] = 1.0

        return dict


def main():
    opts, args = parse_command_line()

    # call computeDiskMass for the first time
    # to download all the necessary files
    _ = computeDiskMass.computeDiskMass(
        2.6, 1.6, 0, 0, eosname="2H", kerr=False, R_ns=None, max_mass=None
    )

    # set up logging
    utils.set_up_logger(opts.verbose)

    processor = EMBright(opts)
    processor.start()


if __name__ == "__main__":
    main()
