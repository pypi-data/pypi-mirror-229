#!/usr/bin/env python3

import json
import logging

from cronut import App

from ligo.lw import lsctables

from ligo.scald.io import kafka

from gw.lts import utils
from gw.lts.utils import influx_helper


def parse_command_line():
    parser = utils.add_general_opts()
    parser.add_option(
        "--ifo", action="append", help="Interferometer(s) to get data from"
    )
    opts, args = parser.parse_args()

    return opts, args


class SNRConsistency(object):
    def __init__(self, options):
        self.ifos = options.ifo
        self.tag = options.tag
        self.kafka_server = options.kafka_server
        self.topics = options.input_topic

        # set up producer
        self.client = kafka.Client(f"kafka://{self.tag}@{self.kafka_server}")

        # initialize influx helper to write out trigger data
        self.influx_helper = influx_helper.InfluxHelper(
            config_path=options.scald_config,
            routes={
                "snr_accuracy": {"aggregate": "min"},
            },
        )

        # create a job service using cronut
        self.app = App(
            "snr_consistency",
            broker=f"kafka://{self.tag}_snr_consistency@{self.kafka_server}",
        )

        # subscribes to a topic
        @self.app.process(self.topics)
        def process(message):
            mdatasource, mtag, mtopic = utils.parse_msg_topic(message)
            farstring = utils.parse_msg_key(message)

            # unpack information from the message
            event = json.loads(message.value())
            time = event["time"] + event["time_ns"] * 10**-9.0
            coinc_file = utils.load_xml(event["coinc"])

            # get sim table and injected ifo snrs
            simtable = lsctables.SimInspiralTable.get_table(coinc_file)

            # get coinc table and recovered ifo snrs
            sngltable = lsctables.SnglInspiralTable.get_table(coinc_file)

            # compute accuracy and construct output
            trigger_dict = self._new_trigger()
            trigger_dict["combined_far"] = event["far"]
            trigger_dict["H1_injsnr"] = simtable[0].alpha4
            trigger_dict["L1_injsnr"] = simtable[0].alpha5
            trigger_dict["V1_injsnr"] = simtable[0].alpha6

            for r in sngltable:
                if r.snr:
                    trigger_dict[f"{r.ifo}_recsnr"] = r.snr

            output = {}
            for ifo in self.ifos:
                injsnr = trigger_dict[f"{ifo}_injsnr"]
                recsnr = trigger_dict[f"{ifo}_recsnr"]
                if injsnr and recsnr:
                    accuracy = (injsnr - recsnr) / injsnr
                    output[f"{ifo}_snr_accuracy"] = {
                        "time": [time],
                        "data": [accuracy]
                    }
                    trigger_dict[f"{ifo}_snr_accuracy"] = accuracy

            # send time series data to kafka
            topic_prefix = f"{mdatasource}.{self.tag}.testsuite."
            for key, value in output.items():
                topic = topic_prefix + key

                self.client.write(topic, value, tags=farstring)
                logging.info(f"Sent msg to: {topic}")

            # store trigger data to influx
            self.influx_helper.store_triggers(
                time,
                trigger_dict,
                route="snr_accuracy",
                tags=(farstring),
            )

    def start(self):
        # start up
        logging.info("Starting up...")
        self.app.start()

    def _new_trigger(self):
        dict = {}
        columns = [
            "combined_far",
        ]
        for ifo in self.ifos:
            columns += [f"{ifo}_injsnr", f"{ifo}_recsnr",
                        f"{ifo}_snr_accuracy"]
        for col in columns:
            dict[col] = None

        # we will initialize the combined far value to
        # an arbitrary high value which will get replaced
        # with the actual far from events
        dict["combined_far"] = 1.0

        return dict


def main():
    opts, args = parse_command_line()

    # sanity check input options
    required_opts = ["ifo", "tag", "input_topic", "kafka_server"]
    for r in required_opts:
        if not getattr(opts, r):
            raise ValueError(f"Missing option: {r}.")

    # set up logging
    utils.set_up_logger(opts.verbose)

    # start up processor
    processor = SNRConsistency(opts)
    processor.start()


if __name__ == "__main__":
    main()
