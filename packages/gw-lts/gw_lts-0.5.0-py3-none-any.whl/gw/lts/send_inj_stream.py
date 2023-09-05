#!/usr/bin/env python3

import logging
import json
import os
import io
import copy
import numpy
from time import sleep
from collections import defaultdict, OrderedDict

from ligo.lw import ligolw
from ligo.lw import lsctables
from ligo.lw import utils as ligolw_utils
from ligo.lw.param import Param
from ligo.skymap.tool import bayestar_realize_coincs
from ligo.skymap.bayestar import filter as bayestar_filter

from confluent_kafka import Consumer

import lal
from lal import GPSTimeNow, LIGOTimeGPS, GreenwichMeanSiderealTime
import lal.series
import lalsimulation

from ligo.scald.io import kafka

from gw.lts import utils
from gw.lts.utils import pastro_utils


class LIGOLWContentHandler(ligolw.LIGOLWContentHandler):
    pass


lsctables.use_in(LIGOLWContentHandler)


# define input opts
def parse_command_line():
    parser = utils.add_general_opts()
    parser.add_option(
        "--time-offset",
        type=int,
        default=0,
        help=(
            "Time offset to shift injections by. Not used if data-source "
            "is fake-data, required otherwise. If using mdc injections "
            "this should be a non-zero number that corresponds to the time "
            "h(t) is shifted by, otherwise, 0."
        ),
    )
    parser.add_option(
        "--psd-file",
        metavar="file",
        help="Path to reference PSD file."
    )
    parser.add_option(
        "--track-psd",
        action="store_true",
        default=False,
        help=(
            "Dynamically update PSD. If given, kafka-server and input-topic "
            "are required. Default is False."
        ),
    )
    parser.add_option(
        "--track-segments",
        action="store_true",
        default=False,
        help=(
            "Track IFO states. If given, kafka-server and input-topic "
            "are required. Default is False."
        ),
    )
    parser.add_option(
        "--ifo",
        action="append",
        help="IFOs to use. Can be given more than once."
    )
    parser.add_option(
        "--fake-far-threshold",
        type=float,
        default=2.315e-5,
        help=(
            "Set the FAR threshold for sending coincs. "
            "Used if data-source is fake-data. "
            "Default is 2 per day."
        ),
    )
    parser.add_option(
        "--f-max",
        type=float,
        default=1600.0,
        help=(
            "Set the high frequency cut off for estimating"
            " the injection SNR."
        ),
    )
    parser.add_option(
        "--inj-rate",
        type=float,
        default=20.0,
        help=(
            "Rate to send injection messages in the fake-data scheme."
            "Default is 20 seconds."
        ),
    )
    parser.add_option(
        "--output-coinc",
        metavar="dir",
        default="output_files",
        help="the directory to output coinc files to",
    )
    opts, args = parser.parse_args()

    return opts, args


class SendInjStream(object):
    """
    Producer class for sending messages associated with
    injections in real-time as they appear in the data.

    Parameters
    ----------
    tag (str)
        unique identifier to be used in the Kafka
        broker name and output topic names.
    kafka_server (str)
        server url that Kafka is hosted on.
    datasource (str)
        Source to consider recovered events from. Used in
        the output message topic name as
        `{datasource}.{tag}.testsuite.inj_stream`. Can be
        given multiple times, in which case injection
        messages are sent to multiple output topic names,
        one to one with the datasources provided. eg,
        "fake-data", "gstlal", etc.
    input_topic (str)
        Topic to consume messages from. Required when
        --track-segments or --track-psd is True, not used
        otherwise.
    ifos (str)
        Interferometers to use, eg "H1", "L1", "V1".
    reference_psd (file)
        File path from which to load reference PSD. Used
        for SNR estimation.
    injection_file (file)
        File path from which to load injection set.
    fake_coinc_output (dir)
        Name of directory for writing coinc files. Only used
        if --data-source is "fake-data".
    fake_injection_rate (int)
        Cadence in seconds upon which to produce injection
        messages. Only used if --data-source is "fake-data".
    fake_far_threshold (float)
        FAR threshold used to produce fake data event messages.
    offset (int)
        Offset by which to shift injection times from the
        injection file.
    track_segments (bool)
        Whether to track IFO status by consuming IFO state
        messages from Kafka.
    track_psd (bool)
        Whether to track the PSD by consuming PSD measurement
        from Kafka.
    verbose (bool)
        Be verbose.

    """
    def __init__(self, tag, kafka_server, datasource, input_topic,
                 ifos, reference_psd, injection_file,
                 f_max=1600., fake_coinc_output="output_files",
                 fake_injection_rate=20, fake_far_threshold=2.315e-5,
                 offset=0, track_segments=False, track_psd=False,
                 verbose=False):
        logging.info("Setting up injection stream...")

        self.tag = tag
        self.kafka_server = kafka_server
        self.datasources = datasource
        self.ifos = ifos
        self.f_max = f_max
        self.fake_coinc_output = fake_coinc_output
        self.fake_inj_rate = fake_injection_rate
        self.fake_far_threshold = fake_far_threshold
        self.time_offset = offset
        self.track_segments = track_segments
        self.track_psd = track_psd
        self.verbose = verbose

        if "fake-data" in self.datasources:
            self.send_fake_coincs = True
        else:
            self.send_fake_coincs = False

        # set up kafka consumer and producer
        self.producer = kafka.Client(f"kafka://{self.tag}@{self.kafka_server}")

        if input_topic:
            kafka_settings = {
                "bootstrap.servers": self.kafka_server,
                "group.id": self.tag,
                "message.max.bytes": 5242880,  # 5 MB
            }
            self.client = Consumer(kafka_settings)
            self.client.subscribe([topic for topic in input_topic])

        # set up psds and segments
        self.new_psds = {}
        self.psds = self.load_psd(reference_psd)
        self.psds_dict = {
            key: bayestar_filter.InterpolatedPSD(
                bayestar_filter.abscissa(psd), psd.data.data
            )
            for key, psd in self.psds.items()
            if psd is not None
        }

        if self.track_segments:
            self.segments = defaultdict(lambda: OrderedDict())

        # additional set up for the fake data configuration
        if self.send_fake_coincs:
            self.fake_data_setup()

        # load sorted sim inspiral table
        self.simtable = self.load_sim_table(injection_file)

    def start(self):
        """
        Start the injection stream. Iterate through the
        injection file, processing each injection one-by-one
        in time order. If --data-source is "fake-data", process
        one injection each --inj-rate seconds. Otherwise, shift
        injection times according to --time-offset and process
        them "on the fly", ie when the time now matches the
        injection time.
        """
        logging.info("Starting injection stream...")
        # step through sim table row by row, update sim col values as
        # necessary, send message to inj_stream, then if data-source is
        # fake-data, generate a coinc file and send a message to events topic
        while self.simtable:
            # remove and return the oldest/first inj in the table
            thisrow = self.simtable.pop(0)

            if self.send_fake_coincs:
                # sleep for inj cadence
                sleep(self.fake_inj_rate)

                timenow = float(GPSTimeNow())
                time_offset = timenow - thisrow.geocent_end_time
                injection_time = thisrow.geocent_end_time + time_offset

            else:
                timenow = float(GPSTimeNow())
                time_offset = self.time_offset
                injection_time = thisrow.geocent_end_time + time_offset

                # if the injection is already passed, skip it
                if timenow - (injection_time) >= 5 * 60.0:
                    logging.debug("Skipping old injection")
                    continue

                # sleep until its close to the next inj time
                time_to_sleep = (injection_time) - timenow
                if time_to_sleep > 0.0:
                    logging.debug("Sleeping until next injection...")
                    sleep(time_to_sleep)

            logging.debug("Processing injection at coalescence time: " +
                          f"{injection_time}.")

            # track segments and psds
            if self.track_segments:
                self.segments_tracker(injection_time)
            elif self.track_psd:
                new_psd_msgs, _ = self.pull_dq_messages()
                self.new_psds.update(new_psd_msgs)

            # once we have the state vector segments that we need,
            # update the psds just once
            if self.track_psd and self.new_psds:
                self.track_psds()

            # proceed to generate the correct sim row and send
            # an output message kafka
            outxml, output_simtable = self.new_sim_xml()
            output_row = copy.copy(thisrow)

            # if time offset is nonzero, shift the times, longitude
            # and re-calculate the inj snrs
            if time_offset:
                output_row = self.shift_times(output_row, time_offset)
                inj_snrs = self.calc_inj_snrs(output_row)

                # add inj snrs to appropriate cols in output_row
                for (col_name, ifo) in zip(("alpha4", "alpha5", "alpha6"),
                                           ("H1", "L1", "V1")):
                    if ifo not in self.ifos:
                        continue
                    setattr(output_row, col_name, inj_snrs[ifo])

                logging.debug(
                    f"SNRs: H1: {output_row.alpha4} | L1: {output_row.alpha5}"
                    f" | V1: {output_row.alpha6}"
                )

            # construct sim table
            output_simtable.append(output_row)
            outxml.childNodes[-1].appendChild(output_simtable)

            sim_msg = io.BytesIO()
            ligolw_utils.write_fileobj(outxml, sim_msg)

            # get state vector at time of this injection
            # in fake data configuration, lets just assume all IFOs
            # are always on
            onIFOs = []
            if self.send_fake_coincs:
                onIFOs = ["H1", "L1", "V1"]
            # FIXME: we are assuming that no state info for a given time
            # means that the IFO was off. This is a bad idea and we should
            # really fix it to make sure that we receive explicit 0 states
            # at times when the IFOs actually were off.
            if self.track_segments:
                for ifo, states in self.segments.items():
                    try:
                        ifo_on = states[injection_time]
                        if ifo_on:
                            onIFOs.append(ifo)
                    except KeyError:
                        near_times = []
                        for time, state in states.items():
                            t_minus = injection_time - 0.5
                            t_plus = injection_time + 0.5

                            if t_minus < time < t_plus:
                                near_times.append((time, state))

                        ifo_on = near_times and all(s[1] for s in near_times)
                        if ifo_on:
                            onIFOs.append(ifo)
            logging.debug(f"on IFOs: {onIFOs}")

            # construct output json packet
            output = {
               "sim": sim_msg.getvalue().decode(),
               "onIFOs": (",").join(onIFOs)
            }

            # output msgs to kafka
            for datasource in self.datasources:
                topic = f"{datasource}.{self.tag}.testsuite.inj_stream"
                self.producer.write(topic, output)
                logging.info(f"Sent msg to: {topic}")

            if not self.send_fake_coincs:
                outxml.unlink()
                continue

            # otherwise, proceed to send the coinc message
            trigger = copy.copy(output_row)
            outxml.unlink()

            coincfar = self.snr_to_far_map(
                [trigger.alpha4, trigger.alpha5, trigger.alpha6]
            )

            # propduce a fake coinc if the far passes the threshold
            if coincfar < self.fake_far_threshold:
                logging.debug("Sending a coinc trigger...")
                self.produce_coinc_output(trigger, coincfar)
            else:
                logging.debug(f"Coinc FAR {coincfar:e} " +
                              "above threshold to send message.")

        logging.info("Sent all injections. Exiting ...")

    def load_psd(self, file):
        """
        Load reference PSD from a filename.
        """
        xmldoc = ligolw_utils.load_filename(
            file, contenthandler=lal.series.PSDContentHandler
        )
        return lal.series.read_psd_xmldoc(xmldoc, root_name=None)

    def fake_data_setup(self):
        """
        Set-up some data products needed for simulating
        coinc events in the "fake-data" scheme. Produce
        an interpolated PSD object used to simulate SNR
        time-series and compute prior distributions for
        simulated p(astro).
        """
        self.detectors = [
            lalsimulation.DetectorPrefixToLALDetector(ifo)
            for ifo in self.ifos
        ]
        self.responses = [det.response for det in self.detectors]
        self.locations = [det.location for det in self.detectors]

        # the interpolated object is used for SNR time series simulation
        self.psds_interp = [self.psds_dict[ifo] for ifo in self.ifos]

        # compute distributions required for pastro calculation
        self.p_x_c = pastro_utils.p_x_c(
            bns=(1.22, 0.06), nsbh=(6.27, 1.84), bbh=(42.98, 8.11)
        )
        self.p_c = pastro_utils.p_c(
            self.p_x_c,
            N_events={
                "Terrestrial": 0,
                "BNS": 60800,
                "NSBH": 48400,
                "BBH": 60800},
        )

    def load_sim_table(self, file):
        """
        Load SimInspiral table from ligolw filename,
        order the rows in the table by time.

        Parameters
        ----------
        file (path)
            Path to ligolw file from which to load
            SimInspiral table.

        Returns (ligolw table)
            ligolw SimInspiral table object
        """
        xmldoc = ligolw_utils.load_filename(
            file, contenthandler=LIGOLWContentHandler
        )
        simtable = lsctables.SimInspiralTable.get_table(xmldoc)
        simtable.sort(
            key=lambda row: row.geocent_end_time
            + 10.0**-9.0 * row.geocent_end_time_ns
        )

        return simtable

    def segments_tracker(self, injection_time, max_retries=100):
        """
        Track IFO state segments by consuming Kafka messages sent
        by GstLAL low-latency inspiral jobs.

        Parameters
        ----------
        injection_time (float)
            Time at which to find each IFO state.
        max_retries (int)
            Number of times to try consuming messages from Kafka
            in order to find the state at the given time.
        """
        have_states = {ifo: False for ifo in self.ifos}

        tries = 0
        while not all(have_states.values()) and tries < max_retries:
            for ifo in self.ifos:
                logging.debug(f"Try {tries} to get state vector segments")
                # either we have a state corresponding to this injection time
                # or we have later states (for now assuming no state = IFO off)
                have_states[ifo] = self.segments[ifo] and (
                    injection_time in self.segments[ifo].keys()
                    or next(reversed(self.segments[ifo])) > injection_time
                )

                if have_states[ifo]:
                    # move on to check the next ifo
                    continue
                else:
                    # sleep for one second to allow the
                    # state vector segments to catch up
                    sleep(1)

                    # pull and store new messages and try again
                    new_psd_msgs, new_segs = self.pull_dq_messages()
                    self.new_psds.update(new_psd_msgs)
                    self.store_segments(new_segs)

                    tries += 1
                    break

    def store_segments(self, new_segs):
        """
        Reduce and store IFO state segments from Kafka
        into dictionary structure.
        """
        for ifo in new_segs.keys():
            for time, states in sorted(new_segs[ifo].items()):
                # for each time, we can receive states from each job.
                # take the max over the recored state from each job,
                # ie if at least one job reports that the data was on
                # at this time, assume it was really on.
                self.segments[ifo].update({time: int(max(states))})
            while len(self.segments[ifo].keys()) >= 500.0:
                self.segments[ifo].popitem(last=False)

    def pull_dq_messages(self, num_messages=10000, timeout=0.3):
        """
        Consume data quality (PSD, and IFO status) messages
        sent to Kafka by GstLAL low-latency inspiral jobs.
        """
        psds = {}
        statevectorsegments = defaultdict(lambda: {})
        msgs = self.client.consume(num_messages=num_messages, timeout=0.2)
        for msg in sorted(msgs, key=self.sortfunc, reverse=True):
            if msg and not msg.error():
                pipeline, tag, ifo, topic = utils.parse_dq_topic(msg.topic())

                if topic.endswith("psd"):
                    psd = json.loads(msg.value())
                    psds.setdefault(ifo, psd)

                elif topic.endswith("statevectorsegments"):
                    value = json.loads(msg.value())
                    time = value["time"]
                    state = value["data"]
                    ifo_dict = statevectorsegments[ifo]
                    for t, s in zip(time, state):
                        ifo_dict.setdefault(t, [])
                        # dont store duplicate states from each job
                        if s not in ifo_dict[t]:
                            ifo_dict[t].append(s)

        return psds, statevectorsegments

    def track_psds(self):
        """
        Process PSD messages received from Kafka.
        Interpolate the PSD data and store by IFO.
        """
        for ifo, data in self.new_psds.items():
            # parse psd data
            x = numpy.array(data["freq"])
            y = abs(numpy.array(data["asd"])) ** 2.0

            # make sure they are the same length
            if len(y) != len(x):
                x = x[: len(y)]

            # remove nans
            psd_data = numpy.array([])
            frequency = numpy.array([])
            for f, p in zip(x, y):
                if not numpy.isnan(p):
                    psd_data = numpy.append(psd_data, p)
                    frequency = numpy.append(frequency, f)

            # update psds dict with interpolated psds
            new_psd = lal.CreateREAL8FrequencySeries(
                "new_psd",
                None,
                min(frequency),
                data["deltaF"],
                "s strain^2",
                len(psd_data),
            )
            new_psd.data.data = psd_data
            self.psds.update({ifo: new_psd})

            self.psds_dict.update(
                {ifo: bayestar_filter.InterpolatedPSD(frequency, psd_data)}
            )
            logging.debug(f"Updated {ifo} PSD.")

        self.psds_interp = [self.psds_dict[ifo] for ifo in self.psds.keys()]

    def sortfunc(self, m):
        return m.timestamp()

    def new_sim_xml(self):
        """
        Open a new xml doc and write a SimInspiral
        table with a single row.
        """
        xml = ligolw.Document()
        xml.appendChild(ligolw.LIGO_LW())

        simtable = lsctables.New(lsctables.SimInspiralTable)
        return xml, simtable

    def shift_times(self, row, time_offset):
        """
        fix RA and GPS times according to the time offset

        Parameters
        ----------
        row (ligolw table row)
            SimInspiral table row object corresponding to
            a single injection.
        time_offset (int)
            Offset to shift injection times by.

        Returns
        ----------
        row (ligolw table row)
            SimInspiral table row with shifted times and
            corrected right ascension
        """
        end_time = row.geocent_end_time + row.geocent_end_time_ns * 10.0**-9.0
        gmst0 = GreenwichMeanSiderealTime(LIGOTimeGPS(end_time))
        gmst = GreenwichMeanSiderealTime(LIGOTimeGPS(end_time + time_offset))
        dgmst = gmst - gmst0
        row.longitude = row.longitude + dgmst

        row.geocent_end_time = int(row.geocent_end_time + time_offset)
        row.h_end_time = row.h_end_time + time_offset
        row.l_end_time = row.l_end_time + time_offset
        row.v_end_time = row.v_end_time + time_offset

        return row

    def calc_inj_snrs(self, inj):
        """
        Estimate injected SNRs given injection time,
        waveform, intrinsic and extrinsic parameters.

        Parameters
        ----------
        inj (ligolw table row)
            SimInspiral table row object corresponding to
            a single injection.

        Returns
        ----------
        snr (dict)
            Dictionary, keyed by ifo, of estimated injected
            SNRs.
        """
        snr = dict.fromkeys(self.ifos, 0.0)

        injtime = inj.geocent_end_time
        f_min = inj.f_lower
        approximant = lalsimulation.GetApproximantFromString(str(inj.waveform))
        sample_rate = 16384.0
        f_max = self.f_max

        h_plus, h_cross = lalsimulation.SimInspiralTD(
            m1=inj.mass1 * lal.MSUN_SI,
            m2=inj.mass2 * lal.MSUN_SI,
            S1x=inj.spin1x,
            S1y=inj.spin1y,
            S1z=inj.spin1z,
            S2x=inj.spin2x,
            S2y=inj.spin2y,
            S2z=inj.spin2z,
            distance=inj.distance * 1e6 * lal.PC_SI,
            inclination=inj.inclination,
            phiRef=inj.coa_phase,
            longAscNodes=0.0,
            eccentricity=0.0,
            meanPerAno=0.0,
            deltaT=1.0 / sample_rate,
            f_min=f_min,
            f_ref=0.0,
            LALparams=None,
            approximant=approximant,
        )

        h_plus.epoch += injtime
        h_cross.epoch += injtime

        # Compute strain in each detector. If one detector wasn't on,
        # snr will be set to zero.
        for instrument in snr:
            if instrument not in self.psds.keys():
                continue
            h = lalsimulation.SimDetectorStrainREAL8TimeSeries(
                h_plus,
                h_cross,
                inj.longitude,
                inj.latitude,
                inj.polarization,
                lalsimulation.DetectorPrefixToLALDetector(instrument),
            )
            snr[instrument] = lalsimulation.MeasureSNR(
                h, self.psds[instrument], f_min, f_max
            )

        return snr

    def snr_to_far_map(self, snrs):
        """
        Create a map to simulate a FAR given an SNR. This is
        set so that a network SNR 7 event (H1 SNR = L1 SNR = 4.)
        is recovered with FAR < 2/day.
        """
        snrs = [snr for snr in snrs if snr > 4.0]
        net_snr = numpy.sqrt(numpy.linalg.norm(snrs))
        return 6 * 10**-4.0 * numpy.exp(-(net_snr)**2.0 / 2.0)

    def produce_coinc_output(self, trigger, coincfar, key=None):
        """
        Send output messages of simulated coinc events to output
        `inj_events` topic.

        Parameters
        ----------
        trigger (ligowl table row)
            Row corresponding to a single injection in the SimInspiral
            table.
        coincfar (float)
            FAR value for simulated recovered event associated with
            this injection.
        key (str)
            Optional string to use in the file name for writing coincs
            to disk.
        """
        # build coinc xml doc, calculate p_astro, and produce message
        newxmldoc = self.build_coinc_xml(trigger, coincfar)
        if not newxmldoc:
            return False

        coinctable = lsctables.CoincInspiralTable.get_table(newxmldoc)
        coincsnr = coinctable[0].snr

        p_astro = self.get_pastro(newxmldoc, coincsnr)

        output = self.construct_event_ouput(newxmldoc, p_astro, filekey=key)

        # send coinc message to events topic
        logging.info(f"network SNR: {output['snr']} | FAR: {output['far']}")

        topic = f"fake-data.{self.tag}.testsuite.inj_events"
        self.producer.write(topic, output)
        logging.info(f"Sent msg to: {topic}")
        newxmldoc.unlink()

        return True

    def build_coinc_xml(self, row, coincfar):
        """
        Construct a full ligolw file object to represent a simulated
        recovered event.

        Parameters
        ----------
        row (ligolw table row)
            A single SimInspiral row corresponding to the injection.
        coincfar (float)
            FAR value for simulated recovered event associated with
            this injection.

        Returns
        ----------
        newxmldoc (ligolw file object)
            ligo-lw coinc file object with all required tables.
        """
        # instantiate relevant lsctables objects
        newxmldoc = ligolw.Document()
        ligolw_elem = newxmldoc.appendChild(ligolw.LIGO_LW())
        new_process_table = ligolw_elem.appendChild(
            lsctables.New(lsctables.ProcessTable,
                          columns=utils.all_process_rows)
        )
        new_sngl_inspiral_table = ligolw_elem.appendChild(
            lsctables.New(lsctables.SnglInspiralTable,
                          columns=utils.all_sngl_rows)
        )
        new_coinc_inspiral_table = ligolw_elem.appendChild(
            lsctables.New(lsctables.CoincInspiralTable,
                          columns=utils.all_coinc_rows)
        )
        new_coinc_event_table = ligolw_elem.appendChild(
            lsctables.New(lsctables.CoincTable)
        )
        new_coinc_map_table = ligolw_elem.appendChild(
            lsctables.New(lsctables.CoincMapTable)
        )

        # simulate SNR time series using interpolated psd object
        # measurement_error is set as gaussian but one can switch
        # to no noise by measurement_error="zero-noise"
        bayestar_sim_list = bayestar_realize_coincs.simulate(
            seed=None,
            sim_inspiral=row,
            psds=self.psds_interp,
            responses=self.responses,
            locations=self.locations,
            measurement_error="gaussian-noise",
            f_low=20,
            f_high=2048,
        )

        # get mass parameters
        mass1 = max(numpy.random.normal(loc=row.mass1, scale=1.0), 1.1)
        mass2 = max(numpy.random.normal(loc=row.mass2, scale=1.0), mass1)
        mchirp, eta = self.mc_eta_from_m1_m2(mass1, mass2)

        snrs = defaultdict(lambda: 0)
        coincsnr = None

        # populate process table
        process_row_dict = {k: 0 for k in utils.all_process_rows}
        process_row_dict.update(
            {"process_id": 0, "program": "gstlal_inspiral", "comment": ""}
        )
        new_process_table.extend([
            lsctables.ProcessTable.RowType(**process_row_dict)
        ])

        # populate sngl table, coinc map table, and SNR timeseriess
        for event_id, (
            ifo, (horizon, abs_snr, arg_snr, toa, snr_series)
        ) in enumerate(zip(self.ifos, bayestar_sim_list)):
            sngl_row_dict = {k: 0 for k in utils.all_sngl_rows}

            sngl_row_dict.update(
                {
                    "process_id": 0,
                    "event_id": event_id,
                    "end": toa,
                    "mchirp": mchirp,
                    "mass1": mass1,
                    "mass2": mass2,
                    "eta": eta,
                    "ifo": ifo,
                    "snr": abs_snr,
                    "coa_phase": arg_snr,
                }
            )

            # add to the sngl inspiral table
            new_sngl_inspiral_table.extend(
                [lsctables.SnglInspiralTable.RowType(**sngl_row_dict)]
            )
            snrs[ifo] = abs_snr

            coinc_map_row_dict = {
                "coinc_event_id": 0,
                "event_id": event_id,
                "table_name": "sngl_inspiral",
            }

            # add to the coinc map table
            new_coinc_map_table.extend(
                [lsctables.CoincMapTable.RowType(**coinc_map_row_dict)]
            )

            # add SNR time series as array objects
            elem = lal.series.build_COMPLEX8TimeSeries(snr_series)
            elem.appendChild(Param.from_pyvalue("event_id", event_id))
            ligolw_elem.appendChild(elem)

        # calculate coinc SNR, only proceed if above 4
        coincsnr = numpy.linalg.norm([snr for snr in snrs.values() if snr > 4])
        if not coincsnr:
            logging.debug(f"Coinc SNR {coincsnr} too low to send a message.")
            return None

        # populate coinc inspiral table
        coinc_row_dict = {col: 0 for col in utils.all_coinc_rows}
        coincendtime = row.geocent_end_time
        coincendtimens = row.geocent_end_time_ns
        coinc_row_dict.update(
            {
                "coinc_event_id": 0,
                "snr": coincsnr,
                "mass": row.mass1 + row.mass2,
                "mchirp": row.mchirp,
                "end_time": coincendtime,
                "end_time_ns": coincendtimens,
                "combined_far": coincfar,
            }
        )
        new_coinc_inspiral_table.extend(
            [lsctables.CoincInspiralTable.RowType(**coinc_row_dict)]
        )

        # populate coinc event table
        coinc_event_row_dict = {col: 0 for col in utils.all_coinc_event_rows}
        coinc_event_row_dict.update(
            {
                "coinc_def_id": 0,
                "process_id": 0,
                "time_slide_id": 0,
                "instruments": "H1,L1,V1",
                "numevents": len(new_sngl_inspiral_table),
            }
        )
        new_coinc_event_table.extend(
            [lsctables.CoincTable.RowType(**coinc_event_row_dict)]
        )

        # add psd frequeny series
        lal.series.make_psd_xmldoc(self.psds, ligolw_elem)

        return newxmldoc

    def mc_eta_from_m1_m2(self, m1, m2):
        """
        Compute chirp mass and mass ratio from component masses.
        """
        mc = (m1 * m2) ** (3.0 / 5.0) / (m1 + m2) ** (1.0 / 5.0)
        eta = (m1 * m2) / (m1 + m2) ** 2.0

        return mc, eta

    def get_pastro(self, xmldoc, rankstat):
        """
        Compute simulated p(astro).
        """
        coinctable = lsctables.CoincInspiralTable.get_table(xmldoc)

        mchirp = coinctable[0].mchirp

        return pastro_utils.p_astro(mchirp, rankstat, self.p_x_c, self.p_c)

    def construct_event_ouput(self, xmldoc, p_astro, filekey=None):
        """
        Construct payload for sending fake coinc messages to Kafka.

        Parameters
        ----------
        xmldoc (ligolw file object)
            ligo-lw coinc file object for this simulated recovered event
        p_astro (dict)
            Dictionary containing simulated p(astro) values.
        filekey (str)
            Optional string to use in the file name for writing coincs
            to disk.

        Returns
        ----------
        output (dict)
            Kafka message payload
        """
        coinctable = lsctables.CoincInspiralTable.get_table(xmldoc)
        time = coinctable[0].end_time

        # write coinc file to disk
        file = (
            f"fake_coinc-{int(time)}.xml"
            if not filekey
            else f"{filekey}-fake_coinc-{int(time)}.xml"
        )
        ligolw_utils.write_filename(
            xmldoc,
            os.path.join(self.fake_coinc_output, file), verbose=self.verbose
        )

        coinc_msg = io.BytesIO()
        ligolw_utils.write_fileobj(xmldoc, coinc_msg)

        # create json packet
        output = {
            "time": time,
            "time_ns": coinctable[0].end_time_ns,
            "snr": coinctable[0].snr,
            "far": coinctable[0].combined_far,
            "p_astro": json.dumps(p_astro),
            "coinc": coinc_msg.getvalue().decode(),
        }
        return output


def main():
    # parse command line
    opts, args = parse_command_line()

    if opts.track_psd or opts.track_segments:
        if not getattr(opts, "kafka_server"):
            raise ValueError(
                "Must specify --kafka-server when " +
                "--track-psd or --track-segments is set."
            )
        if not getattr(opts, "input_topic"):
            raise ValueError(
                "Must specify at least one --input-topic when " +
                "--track-psd or --track-segments is set."
            )

    if "fake-data" in opts.data_source:
        try:
            os.mkdir(opts.output_coinc)
        except OSError:
            pass

    # set up logger
    utils.set_up_logger(opts.verbose)

    # initialize and set up
    send_inj_stream = (SendInjStream(opts.tag, opts.kafka_server,
                       opts.data_source, opts.input_topic, opts.ifo,
                       opts.psd_file, opts.inj_file,
                       f_max=opts.f_max, fake_coinc_output=opts.output_coinc,
                       fake_injection_rate=opts.inj_rate,
                       fake_far_threshold=opts.fake_far_threshold,
                       offset=opts.time_offset,
                       track_segments=opts.track_segments,
                       track_psd=opts.track_psd,
                       verbose=opts.verbose)
                       )

    # start the stream
    send_inj_stream.start()


if __name__ == "__main__":
    main()
