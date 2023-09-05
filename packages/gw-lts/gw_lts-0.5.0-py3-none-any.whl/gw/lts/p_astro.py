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


def parse_command_line():
    parser = utils.add_general_opts()
    parser.add_option(
        "--pastro-file",
        metavar="name=file",
        action="append",
        help=(
            "Name to identify p_astro with and filename to download from "
            "GraceDB, given as name=file. Can be given multiple times, but "
            "names should be one to one with files. Example: "
            "gstlal=gstlal.p_astro.json, mbta=mbta.p_astro.json. "
            "If no file name is provided, it is assumed the filename is "
            "of the form <pipeline>.p_astro.json. If the option is not "
            "provided, the p_astro name will be the job tag and filenames "
            "are assumed to be <pipeline>.p_astro.json."
        ),
    )
    parser.add_option(
        "--gdb-pastros",
        action="store_true",
        default=False,
        help=(
            "Download p(astro) files from GraceDB. "
            "This will fail if the data source is fake-data."
        ),
    )
    opts, args = parser.parse_args()

    return opts, args


class PAstro(object):
    def __init__(self, options):
        self.tag = options.tag
        self.kafka_server = options.kafka_server
        self.gdb_pastros = options.gdb_pastros

        self.pastro_files = {}
        if options.pastro_file:
            for option in options.pastro_file:
                name, file = option.split("=")
                self.pastro_files.update({name: file})
        else:
            self.pastro_files = {self.tag: None}

        # set up producer
        self.client = kafka.Client(f"kafka://{self.tag}@{self.kafka_server}")

        if self.gdb_pastros:
            self.gracedb_helper = GraceDbHelper(options.gracedb_server)

        # initialize output dict
        self.events = {
            name: deque(maxlen=10)
            for name in self.pastro_files.keys()
        }

        # initialize influx helper to write out trigger data
        self.influx_helper = influx_helper.InfluxHelper(
            config_path=options.scald_config,
            routes={
                "source_class": {"aggregate": "min"},
            },
        )

        # create a job service using cronut
        self.app = App(
            "pastro", broker=f"kafka://{self.tag}_pastro@{self.kafka_server}"
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

            for name, file in self.pastro_files.items():
                response = self.process_event(event, name, file)
                if not response:
                    # keep track of events that failed
                    # to get a p(astro) on the first try
                    # when getting p(astro)s from gracedb, this
                    # can happen if the p(astro) isnt uploaded
                    # immediately
                    times = [e["time"] for e in self.events[name]]
                    if not event["time"] in times:
                        self.events[name].append(event)

            # iterate over events and try again to grab a
            # p(astro) for each one. On success, remove the
            # event from the deque
            for name, file in self.pastro_files.items():
                for e in copy.deepcopy(self.events[name]):
                    response = self.process_event(e, name, file)
                    if response:
                        self.events[name].remove(e)

    def start(self):
        # start up
        logging.info("Starting up...")
        self.app.start()

    def process_event(self, event, pastro_name, filename):
        if self.gdb_pastros:
            if not filename:
                filename = event["pipeline"] + ".p_astro.json"
            uid = event["uid"]
            file = self.gracedb_helper.query_file(uid, filename=filename)
            if file:
                p_astro_dict = json.loads(file.read())
            else:
                p_astro_dict = None

        else:
            try:
                p_astro_dict = json.loads(event["p_astro"])
            except KeyError:
                raise KeyError(
                    "Event message does not include p(astro) and " +
                    "--gdb-pastros is not given. " +
                    "There is no way to retrieve the p(astro) in this case."
                )

        if p_astro_dict:
            output = {}
            time = event["time"]
            datasource = event["datasource"]
            farstring = event["farstring"]

            p_astro_dict["astro"] = 1 - p_astro_dict["Terrestrial"]

            # determine source from inspiral table
            coinc_file = utils.load_xml(event["coinc"])
            simtable = lsctables.SimInspiralTable.get_table(coinc_file)
            source = utils.source_tag(simtable)

            trigger_dict = self._new_trigger()
            trigger_dict["combined_far"] = event["far"]

            for key, value in p_astro_dict.items():
                output[f"p_{key}"] = {
                    "time": [float(time)],
                    "data": [float(value)]
                }
                trigger_dict[f"p_{key}"] = float(value)

            logging.debug(f"{source} event: {pastro_name}: {p_astro_dict}")

            # send time series data to kafka
            for route, data in output.items():
                topic = f"{datasource}.{self.tag}.testsuite.{route}"
                self.client.write(
                    topic, data, tags=[farstring, pastro_name, source],
                )
                logging.info(
                    f"Sent output message to output topic: {topic}."
                )

            # store trigger data to influx
            self.influx_helper.store_triggers(
                time,
                trigger_dict,
                route="source_class",
                tags=(farstring, pastro_name, source),
            )

            return True

        else:
            return False

    @staticmethod
    def _new_trigger():
        dict = {}
        columns = (
            "combined_far",
            "p_astro",
            "p_Terrestrial",
            "p_BNS",
            "p_BBH",
            "p_NSBH",
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

    # set up logging
    utils.set_up_logger(opts.verbose)

    # sanity check input option
    if opts.pastro_file:
        names = []
        files = []
        for option in opts.pastro_file:
            name, file = option.split("=")
            if name in names:
                raise ValueError(
                    f"pastro name {name} was provided more than once. " +
                    "Please only provide one filename for each pastro name."
                )
            elif file in files:
                logging.warning(
                    f"pastro filename {file} was provided more than once " +
                    " for different pastro names. " +
                    "Are you sure this is what you want?"
                )
            elif not file:
                logging.warning(
                    f"no pastro filename provided for {name}. Assuming " +
                    "filenames are of the form <pipeline>.p_astro.json"
                )

            names.append(name)
            files.append(file)
    else:
        logging.warning(
            "No pastro file option provided, " +
            "defaulting to use <tag>=<pipeline>.p_astro.json."
        )

    processor = PAstro(opts)
    processor.start()


if __name__ == "__main__":
    main()
