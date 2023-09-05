#!/usr/bin/env python3

import json
import logging

from cronut import App

from ligo.lw import lsctables

from ligo.scald.io import kafka

from gw.lts import utils


def parse_command_line():
    parser = utils.add_general_opts()
    opts, args = parser.parse_args()

    return opts, args


def main():
    opts, args = parse_command_line()

    tag = opts.tag

    # set up producer
    client = kafka.Client(f"kafka://{tag}@{opts.kafka_server}")

    # set up logging
    utils.set_up_logger(opts.verbose)

    # create a job service using cronut
    app = App("likelihood",
              broker=f"kafka://{tag}_likelihood@{opts.kafka_server}")

    # subscribes to a topic
    @app.process(opts.input_topic)
    def process(message):
        mdatasource, mtag, mtopic = utils.parse_msg_topic(message)
        farstring = utils.parse_msg_key(message)
        logging.debug(f"Read message from {mdatasource} {mtopic}.")

        # parse event info
        event = json.loads(message.value())

        coinc_file = utils.load_xml(event["coinc"])
        time = event["time"] + event["time_ns"] * 10**-9.0

        # load likelihood from coinc event table
        event_table = lsctables.CoincTable.get_table(coinc_file)
        likelihood = event_table[0].likelihood

        # output message
        output = {
            "time": [float(time)],
            "data": [float(likelihood)],
        }

        # send message to output topics
        topic = f"{mdatasource}.{tag}.testsuite.likelihood"
        client.write(topic, output, tags=farstring)
        logging.info(f"Sent output message to topic: {topic}.")

    # start up
    logging.info("Starting up...")
    app.start()


if __name__ == "__main__":
    main()
