#!/usr/bin/env python3

import json
import logging

from cronut import App

from ligo.lw import lsctables

from gw.lts import utils
from gw.lts.utils import influx_helper


def parse_command_line():
    parser = utils.add_general_opts()

    parser.add_option(
        "--input-params",
        default=[],
        action="append",
        help=(
            "Parameters from sim inspiral table for which to compute "
            "recovered accuracy. Can be given multiple times."
        ),
    )
    opts, args = parser.parse_args()

    return opts, args


def _new_trigger(params):
    dict = {}
    columns = [param for param in params]
    columns += [f"{param}_accuracy" for param in params]
    columns += ["combined_far"]

    for col in columns:
        dict[col] = None

    # we will initialize the combined far value to
    # an arbitrary high value which will get replaced
    # with the actual far from events
    dict["combined_far"] = 1.0

    return dict


def end_time_accuracy(simtable, sngltable):
    injected_time = None
    diff = None
    try:
        injected_time = (
            simtable.getColumnByName("geocent_end_time")[0]
            + 10.0**-9.0 * simtable.getColumnByName("geocent_end_time_ns")[0]
        )
        # assume the end time is the same for each ifo
        # and just take the first one
        recovered_time = (
            sngltable.getColumnByName("end_time")[0]
            + 10.0**-9.0 * sngltable.getColumnByName("end_time_ns")[0]
        )

        # calculate difference in ms
        diff = (recovered_time - injected_time) * 10**3.0
    except Exception as e:
        logging.debug(f"Error getting end time difference: {e}")

    return injected_time, diff


def fractional_param_accuracy(param, simtable, sngltable):
    inj_param = None
    rec_param = None
    frac_accuracy = None

    # first get the injected parameter value
    # from the sim inspiral table
    try:
        inj_param = simtable.getColumnByName(param)[0]
    except Exception as e:
        logging.debug(f"Error getting {param} from sim table: {e}")
    if inj_param is None:
        # some parameters can be computed if they are missing
        if param == "eta":
            mass1 = simtable.getColumnByName("mass1")[0]
            mass2 = simtable.getColumnByName("mass2")[0]
            inj_param = utils.eta_from_m1_m2(mass1, mass2)
        elif param == "mchirp":
            mass1 = simtable.getColumnByName("mass1")[0]
            mass2 = simtable.getColumnByName("mass2")[0]
            inj_param = utils.mchirp_from_m1_m2(mass1, mass2)

    # get the recovered parameter value
    # from the sngl inspiral table
    try:
        # assume that the recovered parameters are all the
        # same for each ifo and just take the first one
        rec_param = sngltable.getColumnByName(param)[0]
    except Exception as e:
        logging.debug(f"Error getting {param} from sngl table: {e}")

    # calculate fractional accuracy
    # Note: I guess this is more like error than accuracy, but whatever
    if (rec_param is not None) and (inj_param is not None):
        frac_accuracy = (rec_param - inj_param) / inj_param
        logging.debug(
            f"{param}: rec: {rec_param} | "
            f"inj: {inj_param} | accuracy: {frac_accuracy}"
        )

    return inj_param, frac_accuracy


def main():
    opts, args = parse_command_line()

    # sanity check input options
    required_opts = ("tag", "input_params", "scald_config", "kafka_server")
    for r in required_opts:
        if not getattr(opts, r):
            raise ValueError(f"Missing option: {r}.")

    tag = opts.tag
    kafka_server = opts.kafka_server
    scald_config = opts.scald_config
    input_topic = opts.input_topic
    input_params = opts.input_params

    # set up logging
    utils.set_up_logger(opts.verbose)

    # initialize influx helper to write out trigger data
    InfluxHelper = influx_helper.InfluxHelper(
        config_path=scald_config,
        routes={
            "parameter_accuracy": {"aggregate": "min"}
        }
    )

    # create a job service using cronut
    app = App(
        "inj_accuracy", broker=f"kafka://{tag}_inj_accuracy@{kafka_server}"
    )

    # subscribes to a topic
    @app.process(input_topic)
    def process(message):
        mdatasource, mtag, mtopic = utils.parse_msg_topic(message)
        farstring = utils.parse_msg_key(message)
        logging.info(f"Read message from input {mtopic}.")

        # parse event info
        event = json.loads(message.value())
        time = event["time"] + event["time_ns"] * 10**-9.0
        coinc_file = utils.load_xml(event["coinc"])
        SimInspiralTable = lsctables.SimInspiralTable.get_table(coinc_file)
        SnglInspiralTable = lsctables.SnglInspiralTable.get_table(coinc_file)

        # keep track of which IFOs participated in recovering this event
        part_ifos = utils.participating_ifos(SnglInspiralTable)

        # initialize a dictionary to store info about this event
        trigger = _new_trigger(input_params)
        trigger["combined_far"] = event["far"]

        # calculate accuracy on all the requested parameters
        for param in input_params:
            # end time is handled differently because
            # we just want the difference in ms
            if param == "end_time":
                inj_value, accuracy = end_time_accuracy(
                    SimInspiralTable, SnglInspiralTable
                )
            else:
                inj_value, accuracy = fractional_param_accuracy(
                    param, SimInspiralTable, SnglInspiralTable
                )
            trigger[param] = inj_value
            trigger[f"{param}_accuracy"] = accuracy

        # write out the trigger type data to influx
        InfluxHelper.store_triggers(
            time, trigger,
            route="parameter_accuracy", tags=(farstring, part_ifos)
        )

    # start up
    logging.info("Starting up...")
    app.start()


if __name__ == "__main__":
    main()
