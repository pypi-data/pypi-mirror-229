#!/usr/bin/env python3

import os
import json
import logging
import copy

from collections import deque

from cronut import App
from io import BytesIO

from ligo.lw import lsctables

from ligo.skymap.bayestar import localize
from ligo.skymap.io import events as LIGOSkymapEvents
from ligo.skymap.postprocess import crossmatch

from astropy.coordinates import SkyCoord
from astropy.table import Table

from ligo.scald.io import kafka

from gw.lts import utils
from gw.lts.utils.gracedb_helper import GraceDbHelper
from gw.lts.utils import influx_helper


def parse_command_line():
    parser = utils.add_general_opts()
    parser.add_option(
        "--output", help="Output directory to write skymap fits files to."
    )
    parser.add_option(
        "--gdb-skymaps",
        action="store_true",
        default=False,
        help="Use skymaps from GraceDB instead of calculating them manually.",
    )
    opts, args = parser.parse_args()

    return opts, args


class Skymap(object):
    def __init__(self, options):
        self.tag = options.tag
        self.kafka_server = options.kafka_server
        self.topics = options.input_topic
        self.output_dir = options.output

        self.gdb_skymaps = options.gdb_skymaps

        if self.gdb_skymaps:
            self.gracedb_helper = GraceDbHelper(options.gracedb_server)

        # set up producer
        self.client = kafka.Client(f"kafka://{self.tag}@{self.kafka_server}")

        self.events = deque(maxlen=10)

        # initialize influx helper to write out trigger data
        self.influx_helper = influx_helper.InfluxHelper(
            config_path=options.scald_config,
            routes={
                "sky_loc": {"aggregate": "min"},
            },
        )

        # create a job service using cronut
        self.app = App(
            "skymap", broker=f"kafka://{self.tag}_skymap@{self.kafka_server}"
        )

        # subscribes to a topic
        @self.app.process(self.topics)
        def process(message):
            mdatasource, mtag, mtopic = utils.parse_msg_topic(message)
            farstring = utils.parse_msg_key(message)
            logging.info(f"Read message from {mdatasource} {mtopic}.")

            # parse event info
            event = json.loads(message.value())
            coinc_file = utils.load_xml(event["coinc"])
            sngl_inspiral = lsctables.SnglInspiralTable.get_table(coinc_file)

            # keep track of which IFOs participated in recovering this event
            part_ifos = utils.participating_ifos(sngl_inspiral)

            event.update(
                {
                    "datasource": mdatasource,
                    "part_ifos": part_ifos,
                    "farstring": farstring,
                }
            )

            # process the event - get a skymap and calculate
            # searched area and probability, send messages to
            # kafka
            response = self.process_event(event)
            if not response:
                # keep track of events that failed
                # to get a skymap on the first try
                # when getting skymaps from gracedb, this
                # can happen if the skymap isnt uploaded
                # immediately
                times = [e["time"] for e in self.events]
                if not event["time"] in times:
                    self.events.append(event)

            # iterate over events and try again to grab a
            # skymap for each one. On success, remove the
            # event from the deque
            for e in copy.deepcopy(self.events):
                response = self.process_event(e)
                if response:
                    self.events.remove(e)

    def start(self):
        # start up
        logging.info("Starting up...")
        self.app.start()

    def process_event(self, event):
        # either download skymap from gracedb or
        # generate one with bayestar
        if self.gdb_skymaps:
            file = self.gracedb_helper.query_file(
                event["uid"],
                "bayestar.multiorder.fits",
                outpath=self.output_dir,
                tag=self.tag,
            )
            if file:
                filename = f'{self.tag}-{event["uid"]}.fits'
                skymap = Table.read(os.path.join(self.output_dir, filename))
            else:
                skymap = None
        else:
            skymap = self.make_skymap(event)

        if skymap:
            output = {}
            time = event["time"]
            datasource = event["datasource"]
            farstring = event["farstring"]
            part_ifos = event["part_ifos"]

            # get right ascension and declination
            # from sim inspiral table
            coinc = utils.load_xml(event["coinc"])
            simtable = lsctables.SimInspiralTable.get_table(coinc)
            ra, dec = simtable[0].ra_dec

            # use SkyCoord and crossmatch to get pvalues
            loc = SkyCoord(ra=ra, dec=dec, unit="rad")
            p = crossmatch(skymap, loc).searched_prob
            deg2 = crossmatch(skymap, loc).searched_area

            logging.debug(f"Searched probability: {p} | searched area: {deg2}")

            # construct output
            trigger_dict = self._new_trigger()
            trigger_dict["combined_far"] = event["far"]
            trigger_dict["snr"] = event["snr"]
            for key, value in (("searched_prob", p), ("searched_area", deg2)):
                output[key] = {
                    "time": [time],
                    "data": [value]
                }
                trigger_dict[key] = value

            # send time series data to kafka
            topic_prefix = f"{datasource}.{self.tag}.testsuite."
            for key, value in output.items():
                topic = topic_prefix + key
                self.client.write(topic, value, tags=[farstring, part_ifos])
                logging.info(f"Sent msg to: {topic}")

            # store trigger data to influx
            self.influx_helper.store_triggers(
                time,
                trigger_dict,
                route="sky_loc",
                tags=(farstring, part_ifos),
            )

            return True

        else:
            return False

    def make_skymap(self, event):
        skymap = None
        coinc_obj = BytesIO(event["coinc"].encode())
        # make a copy of coinc file to avoid I/O error in events.ligolw.open()
        psd_obj = copy.copy(coinc_obj)

        event_source = LIGOSkymapEvents.ligolw.open(
            coinc_obj, psd_file=psd_obj, coinc_def=None
        )

        if len(event_source) > 1:
            logging.info(
                "Warning: Defaulting to use the first event in coinc."
            )

        # produce the skymap
        for event_id, event in event_source.items():
            skymap = localize(event)
            # break out of the loop after computing just one skymap
            # in case there are multiple rows in coinc inspiral we just
            # go with the first one
            break

        return skymap

    @staticmethod
    def _new_trigger():
        dict = {}
        columns = (
            "combined_far",
            "snr",
            "searched_prob",
            "searched_area"
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

    # make a dir for skymaps
    if not os.path.exists(opts.output):
        os.makedirs(opts.output)

    # start up the processor
    processor = Skymap(opts)
    processor.start()


if __name__ == "__main__":
    main()
