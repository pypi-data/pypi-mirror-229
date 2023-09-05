#!/usr/bin/env python3

import json
import logging

from collections import defaultdict

from cronut import App

from ligo.lw import lsctables

from ligo.scald.io import kafka

from gw.lts import utils
from gw.lts.utils import influx_helper


def parse_command_line():
    parser = utils.add_general_opts()
    opts, args = parser.parse_args()

    return opts, args


class InjMissedFound(object):
    def __init__(self, options):
        self.tag = options.tag
        self.kafka_server = options.kafka_server
        self.topics = options.input_topic

        # set up producer
        self.client = kafka.Client(f"kafka://{self.tag}@{self.kafka_server}")
        self.output_topics = (
            "H1_injsnr",
            "L1_injsnr",
            "V1_injsnr",
            "H1_recsnr",
            "L1_recsnr",
            "V1_recsnr",
            "inj_snr",
            "decisive_snr",
            "injchi_eff",
            "recchi_eff",
            "injchi_p",
            "combined_far",
            "likelihood",
            "snr",
        )
        trigger = self._new_trigger()
        for topic in self.output_topics:
            if topic not in trigger.keys():
                raise ValueError(
                    "Output topics must be a subset of keys "
                    "stored in the trigger object."
                )

        # initialize influx helper to write out trigger data
        self.influx_helper = influx_helper.InfluxHelper(
            config_path=options.scald_config,
            routes={
                "triggers": {"aggregate": "min"},
                "missed_triggers": {"aggregate": None},
            },
        )

        # create a job service using cronut
        self.app = App(
            "inj_missed_found",
            broker=f"kafka://{self.tag}_inj_missed_found@{self.kafka_server}",
        )

        # subscribes to a topic
        @self.app.process(self.topics)
        def process(message):
            mdatasource, mtag, mtopic = utils.parse_msg_topic(message)
            farstring = utils.parse_msg_key(message)

            # these are injections that were never associated
            # with an event from the search
            if mtopic == "missed_inj":
                # unpack information from the message
                injection = json.loads(message.value())
                sim_file = utils.load_xml(injection["sim"])
                on_ifos = utils.sort_ifos(injection["onIFOs"])

                # the event is automatically missed and
                # there are no participating IFOs
                part_ifos = "None"

                # process injection information from
                # the sim inspiral table
                time, source, trigger_dict = (
                    self.process_injection(sim_file, on_ifos)
                )
                logging.debug(
                    f"{mdatasource}: {source} injection from time {time} " +
                    "missed: no associated event message received."
                )

                # send time series data to kafka
                self.produce_output(
                    time,
                    trigger_dict,
                    prefix=f"{mdatasource}.{self.tag}.testsuite",
                    tags=[farstring, source],
                )

                # store trigger data to influx
                self.influx_helper.store_triggers(
                    time,
                    trigger_dict,
                    route="missed_triggers",
                    tags=(farstring, on_ifos, part_ifos),
                )

            # these are injections that were associated with
            # a recovered event from the search on gracedb
            elif mtopic == "events":
                # unpack information from the message
                event = json.loads(message.value())
                coinc_file = utils.load_xml(event["coinc"])
                time = event["time"] + event["time_ns"] * 10**-9.0
                on_ifos = utils.sort_ifos(event["onIFOs"])

                # process the injection and recovered event information
                # from the tables in the coinc file
                source, part_ifos, trigger_dict = self.process_event(
                    coinc_file, on_ifos
                )

                trigger_dict["latency"] = event["latency"]

                logging.debug(
                    f"{mdatasource}: {source} event from time {time} " +
                    f"with far: {farstring}."
                )

                # send time series data to kafka
                self.produce_output(
                    time,
                    trigger_dict,
                    prefix=f"{mdatasource}.{self.tag}.testsuite",
                    tags=[farstring, source],
                )

                # store trigger data to influx
                self.influx_helper.store_triggers(
                    time,
                    trigger_dict,
                    route="triggers",
                    tags=(farstring, on_ifos, part_ifos),
                )

    def start(self):
        # start up
        logging.info("Starting up...")
        self.app.start()

    def produce_output(self, time, dict, prefix="", tags=[]):
        output = defaultdict(lambda: {"time": [], "data": []})

        for topic in self.output_topics:
            if dict[topic] is not None:
                output[topic] = {"time": [time], "data": [dict[topic]]}

        for topic, data in output.items():
            self.client.write(f"{prefix}.{topic}", data, tags=tags)
            logging.info(f"Sent msg to: {prefix}.{topic} with tags: {tags}")

        return

    def process_injection(self, xmldoc, on_ifos):
        trigger_dict = self._new_trigger()
        inj_snrs = defaultdict(lambda: None)

        # load sim inspiral table
        simtable = lsctables.SimInspiralTable.get_table(xmldoc)

        # get info from sim table
        time = (
            simtable[0].geocent_end_time +
            simtable[0].geocent_end_time_ns * 10.0**-9
        )
        trigger_dict["end"] = time
        inj_snrs["H1"] = simtable[0].alpha4
        inj_snrs["L1"] = simtable[0].alpha5
        inj_snrs["V1"] = simtable[0].alpha6

        for ifo in ("H1", "L1", "V1"):
            trigger_dict[f"{ifo}_injsnr"] = inj_snrs[ifo]

        net_snr = utils.network_snr(inj_snrs.values())
        trigger_dict["inj_snr"] = net_snr

        # add injection parameters to trigger dict
        for attr in (
            "mass1",
            "mass2",
            "spin1x",
            "spin1y",
            "spin1z",
            "spin2x",
            "spin2y",
            "spin2z",
        ):
            try:
                trigger_dict[f"sim_{attr}"] = (
                    float(simtable.getColumnByName(attr)[0])
                )
            except TypeError:
                pass

        source = utils.source_tag(simtable)

        # add decisive snr to trigger dict
        dec_snr = utils.decisive_snr(inj_snrs, on_ifos)
        trigger_dict["decisive_snr"] = dec_snr

        m1 = trigger_dict["sim_mass1"]
        m2 = trigger_dict["sim_mass2"]
        s1x = trigger_dict["sim_spin1x"]
        s1y = trigger_dict["sim_spin1y"]
        s1z = trigger_dict["sim_spin1z"]
        s2x = trigger_dict["sim_spin2x"]
        s2y = trigger_dict["sim_spin2y"]
        s2z = trigger_dict["sim_spin2z"]

        # add mchirp
        mchirp = utils.mchirp_from_m1_m2(m1, m2)
        trigger_dict["injmchirp"] = mchirp
        trigger_dict["inj_mchirp"] = mchirp

        if all([isinstance(x, float) for x in (m1, m2, s1z, s2z)]):
            # compute mu1, mu2, and beta
            mu1, mu2, beta = utils.calc_mu(m1, m2, s1z, s2z)
            trigger_dict["mu1"] = mu1
            trigger_dict["mu2"] = mu2
            trigger_dict["beta"] = beta

            # add effective spin parameter
            chi_eff = utils.effective_spin(m1, m2, s1z, s2z)
            trigger_dict["injchi_eff"] = chi_eff
            trigger_dict["inj_chi_eff"] = chi_eff

        if all([isinstance(x, float) for x in (m1, m2, s1x, s1y, s2x, s2y)]):
            # add precession spin parameter
            chi_p = utils.effective_precession_spin(
                m1, m2, s1x, s1y, s2x, s2y
            )
            trigger_dict["injchi_p"] = chi_p
            trigger_dict["inj_chi_p"] = chi_p

        return time, source, trigger_dict

    def process_event(self, coinc_file, on_ifos):
        # get inj SNR information
        time, source, trigger_dict = (
            self.process_injection(coinc_file, on_ifos)
        )

        # load tables
        coinctable = lsctables.CoincInspiralTable.get_table(coinc_file)
        sngltable = lsctables.SnglInspiralTable.get_table(coinc_file)
        coinceventtable = lsctables.CoincTable.get_table(coinc_file)

        # keep track of participating IFOs
        part_ifos = utils.participating_ifos(sngltable)

        # get info from coinc table
        trigger_dict["end"] = (
            coinctable[0].end_time + 10.0**-9 * coinctable[0].end_time_ns
        )
        for attr in ("combined_far", "snr", "false_alarm_rate", "mchirp"):
            try:
                trigger_dict[attr] = float(coinctable.getColumnByName(attr)[0])
            except TypeError:
                pass

        # get likelihood from coinc event table
        try:
            trigger_dict["likelihood"] = float(
                coinceventtable.getColumnByName("likelihood")[0]
            )
        except TypeError:
            pass

        # get info from sngl inspiral table
        for r in sngltable:
            if r.snr:
                trigger_dict[f"{r.ifo}_recsnr"] = float(r.snr)

            for attr in (
                "chisq",
                "mass1",
                "mass2",
                "spin1x",
                "spin1y",
                "spin1z",
                "spin2x",
                "spin2y",
                "spin2z",
                "coa_phase",
            ):
                if getattr(r, attr):
                    if not trigger_dict[f"sngl_{attr}"]:
                        trigger_dict[f"sngl_{attr}"] = float(getattr(r, attr))

        part_ifos = utils.sort_ifos(part_ifos)

        # check that we have all the required params for
        # calculating the effective spin
        m1 = trigger_dict["sngl_mass1"]
        m2 = trigger_dict["sngl_mass2"]
        s1x = trigger_dict["sngl_spin1x"]
        s1y = trigger_dict["sngl_spin1y"]
        s1z = trigger_dict["sngl_spin1z"]
        s2x = trigger_dict["sngl_spin2x"]
        s2y = trigger_dict["sngl_spin2y"]
        s2z = trigger_dict["sngl_spin2z"]

        if all([isinstance(x, float) for x in (m1, m2, s1z, s2z)]):
            rec_chi_eff = utils.effective_spin(m1, m2, s1z, s2z)
            trigger_dict["recchi_eff"] = rec_chi_eff
            trigger_dict["chi_eff"] = rec_chi_eff

        if all([isinstance(x, float) for x in (m1, m2, s1x, s1y, s2x, s2y)]):
            # add precession spin parameter
            chi_p = utils.effective_precession_spin(
                m1, m2, s1x, s1y, s2x, s2y
            )
            trigger_dict["chi_p"] = chi_p

        return source, part_ifos, trigger_dict

    @staticmethod
    def _new_trigger():
        dict = {}
        columns = (
            "combined_far",
            "likelihood",
            "snr",
            "inj_snr",
            "decisive_snr",
            "latency",
            "H1_injsnr",
            "L1_injsnr",
            "V1_injsnr",
            "H1_recsnr",
            "L1_recsnr",
            "V1_recsnr",
            "chisq",
            "end",
            "mu1",
            "mu2",
            "beta",
            "sim_mass1",
            "sim_mass2",
            "sim_spin1x",
            "sim_spin1y",
            "sim_spin1z",
            "sim_spin2x",
            "sim_spin2y",
            "sim_spin2z",
            "sngl_mass1",
            "sngl_mass2",
            "sngl_spin1x",
            "sngl_spin1y",
            "sngl_spin1z",
            "sngl_spin2x",
            "sngl_spin2y",
            "sngl_spin2z",
            "sngl_chisq",
            "sngl_coa_phase",
            "injchi_p",  # depecrate in future version
            "injchi_eff",  # depecrate in future version
            "recchi_eff",  # depecrate in future version
            "mchirp",
            "injmchirp",  # depecrate in future version
            "inj_chi_p",
            "chi_p"
            "inj_chi_eff",
            "chi_eff",
            "inj_mchirp",
        )
        for col in columns:
            dict[col] = None

        # we will initialize the combined far value to
        # an arbitrary high value which will get replaced
        # with the actual far from events
        dict["combined_far"] = 1.0

        return dict


def main():
    # parse options from command line
    opts, args = parse_command_line()

    # set up logging
    utils.set_up_logger(opts.verbose)

    # initialize the processor
    processor = InjMissedFound(opts)
    processor.start()


if __name__ == "__main__":
    main()
