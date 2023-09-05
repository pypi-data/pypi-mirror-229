"""
General utilities and convenience functions used
throughout the project.
"""
import numpy
import logging
from io import BytesIO
from ligo.lw import ligolw
from ligo.lw import lsctables
from ligo.lw import utils as ligolw_utils

from optparse import OptionParser

from lal import G_SI, MSUN_SI, C_SI


class LIGOLWContentHandler(ligolw.LIGOLWContentHandler):
    pass


lsctables.use_in(LIGOLWContentHandler)

all_sngl_rows = (
    "process:process_id",
    "ifo",
    "search",
    "channel",
    "end_time",
    "end_time_ns",
    "end_time_gmst",
    "impulse_time",
    "impulse_time_ns",
    "template_duration",
    "event_duration",
    "amplitude",
    "eff_distance",
    "coa_phase",
    "mass1",
    "mass2",
    "mchirp",
    "mtotal",
    "eta",
    "kappa",
    "chi",
    "tau0",
    "tau2",
    "tau3",
    "tau4",
    "tau5",
    "ttotal",
    "psi0",
    "psi3",
    "alpha",
    "alpha1",
    "alpha2",
    "alpha3",
    "alpha4",
    "alpha5",
    "alpha6",
    "beta",
    "f_final",
    "snr",
    "chisq",
    "chisq_dof",
    "bank_chisq",
    "bank_chisq_dof",
    "cont_chisq",
    "cont_chisq_dof",
    "sigmasq",
    "rsqveto_duration",
    "Gamma0",
    "Gamma1",
    "Gamma2",
    "Gamma3",
    "Gamma4",
    "Gamma5",
    "Gamma6",
    "Gamma7",
    "Gamma8",
    "Gamma9",
    "spin1x",
    "spin1y",
    "spin1z",
    "spin2x",
    "spin2y",
    "spin2z",
    "event_id",
)

all_coinc_rows = (
    "coinc_event:coinc_event_id",
    "combined_far",
    "end_time",
    "end_time_ns",
    "false_alarm_rate",
    "ifos",
    "mass",
    "mchirp",
    "minimum_duration",
    "snr",
)

all_coinc_event_rows = (
    "coinc_definer:coinc_def_id",
    "coinc_event_id",
    "instruments",
    "likelihood",
    "nevents",
    "process:process_id",
    "time_slide:time_slide_id",
)

all_coinc_map_rows = {"coinc_event:coinc_event_id", "event_id", "table_name"}

all_process_rows = (
    "comment",
    "cvs_entry_time",
    "cvs_repository",
    "domain",
    "end_time",
    "ifos",
    "is_online",
    "jobid",
    "node",
    "process_id",
    "program",
    "start_time",
    "unix_procid",
    "username",
    "version",
)

# GLOBAL CONSTANTS #
SUBTHRESHOLD = 1.0
ONE_PER_HOUR = 1.0 / 3600.0
TWO_PER_DAY = 2.0 / 3600.0 / 24.0
ONE_PER_MONTH = 1.0 / 3600.0 / 24.0 / 30.0
TWO_PER_YEAR = 1.0 / 3600.0 / 24.0 / 365.25

FARSTRINGS_DICT = {
    SUBTHRESHOLD: "subthreshold",
    ONE_PER_HOUR: "oneperhour",
    TWO_PER_DAY: "twoperday",
    ONE_PER_MONTH: "onepermonth",
    TWO_PER_YEAR: "twoperyear",
}


def add_general_opts():
    """
    Common input options.

    Returns
    ----------
    OptionParser
    """
    parser = OptionParser()
    parser.add_option(
        "--data-source",
        metavar="string",
        action="append",
        help=("Source of test suite data. Options:"
              "fake-data, gstlal, mbta, pycbc, superevents."
              "Can only be given once (FIXME)."),
    )
    parser.add_option(
        "--tag",
        help=("The tag used to uniquely identify the analysis"
              "you wish to process metrics from. Used as Kafka group ID."),
    )
    parser.add_option(
        "--kafka-server", metavar="string",
        help="Sets the url for the kafka broker."
    )
    parser.add_option("--analysis-dir", metavar="path", help="")
    parser.add_option("--inj-file", metavar="file", help="")
    parser.add_option(
        "--input-topic",
        metavar="string",
        action="append",
        help="The Kafka topic(s) to subscribe to.",
    )
    parser.add_option(
        "--gracedb-server",
        metavar="string",
        help=("GraceDb server to use. Valid options are "
              "gracedb, gracedb-playground, and gracedb-test."),
    )
    parser.add_option(
        "--scald-config",
        metavar="file",
        help="sets ligo-scald options based on yaml configuration.",
    )
    parser.add_option(
        "--verbose", default=False, action="store_true", help="Be verbose."
    )

    return parser


def set_up_logger(verbose):
    """
    Initialize logging for job services.

    Parameters
    ----------
    verbose (bool)
        be verbose in logging. If True,
        log level is set to DEBUG otherwise,
        INFO.
    """
    logging.getLogger()
    if verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logging.getLogger("").addHandler(handler)
    logging.getLogger("").setLevel(log_level)


def load_xml(f):
    """
    Load a ligolw file object.
    """
    if isinstance(f, str):
        f = BytesIO(f.encode("utf-8"))
    xmldoc = ligolw_utils.load_fileobj(f, contenthandler=LIGOLWContentHandler)

    return xmldoc


def load_filename(f):
    """
    Load a ligolw file name.
    """
    xmldoc = ligolw_utils.load_filename(f, contenthandler=LIGOLWContentHandler)

    return xmldoc


def get_ifos(sngltable):
    """
    Get participating interferometers
    from a SnglInspiral table.

    Parameters
    ----------
    sngltable
        ligolw SnglInspiral Table object

    Returns
    ----------
    ifos (str)
        string of ifos, eg "H1L1V1"
    """
    ifos = ""
    for row in sngltable:
        if row.ifo not in ifos:
            ifos += str(row.ifo)

    return ifos


def source_tag(simtable):
    """
    Get source of an injection according
    to component masses in the SimInspiral
    Table. The neutron star maximum mass
    is taken to be 3 M_sun.

    Parameters
    ----------
    simtable
        ligolw SimInsiral Table object

    Returns
    ----------
    source (str)
        source class of the injection. Either
        BBH, BNS, or NSBH.
    """

    mass1 = simtable[0].mass1
    mass2 = simtable[0].mass2
    cutoff = 3  # minimum BH mass

    if mass1 < cutoff and mass2 < cutoff:
        source = "BNS"
    elif mass1 >= cutoff and mass2 >= cutoff:
        source = "BBH"
    else:
        source = "NSBH"
    return source


def parse_msg_topic(message):
    """
    Parse Kafka topic into its various
    parts.

    All topics written to by the gw-lts
    code are in a form:
        <datasource>.<analysis_tag>.testsuite.<topic>

    Parameters
    ----------
    message
        Kafka message object

    Returns
    ----------
    datasource (str)
        datasource that the event is associated
        with. eg, gstlal or fake-data
    tag (str)
        unique string to identify this analysis
    topic (str)
        string representing the type of message
        being sent. eg inj_stream, inj_events, etc.
    """
    datasource, tag, _, topic = message.topic().split(".")
    return datasource, tag, topic


def parse_msg_key(message):
    """
    Parse Kafka message for its key,
    if there is one.

    Parameters
    ----------
    message
        Kafka message object

    Returns
    ----------
    key (str)
        Kafka message key, or "None"
    """
    try:
        key = message.key().decode("utf-8")
    except AttributeError:
        key = "None"
    return key


def find_nearest_msg(msgs, t):
    """
    given a list of event msgs, find the one
    closest to the given time.

    Construct a list of tuples (msg, Delta_t) where Delta_t is
    the difference in time between this msg and the input time.
    Sort by Delta_t, and take the first element in the list which
    corresponds to the msg closest to the input time

    Parameters
    ----------
    msgs (list)
        list or list-type object (deque) of
        dicts containing at least a "time"
        field.
    t (float)
        time for which to find the nearest
        message from the list.

    Returns
    ----------
    nearest_msg (dict)
        dict-type object whose time field
        is closest to the input time, within
        1 second, or None
    """
    delta = 1.0

    nearest_msg = None
    try:
        near_msgs = list(
            (msg, abs(msg["time"] - t))
            for msg in msgs
            if t - delta <= msg["time"] <= t + delta
        )
        if near_msgs:
            nearest_msg = sorted(near_msgs, key=lambda x: x[1])[0][0]

            logging.debug(
                f'Time to search for: {t} | ' +
                f'Nearest msg time: {nearest_msg["time"]}'
            )
    # FIXME: catch a specific exception
    except Exception as e:
        logging.debug(f"Error: {e}")
    return nearest_msg


def decisive_snr(sngl_snrs, ifos):
    """
    Calculate the decisive SNR. If only one
    interferometer is operating, this is the
    snr in the most sensitive IFO, otherwise it
    is the snr in the second most sensitive IFO.
    If no ifos are given, assume all were off
    and set the decisive snr to 0.

    Parameters
    ----------
    sngl_snrs (dict)
        dictionary, keyed by ifo, of SnglInspiral
        SNRs
    ifos (str)
        string of comma separated ifos

    Returns
    ----------
    decisive_snr (float)
        decisive snr
    """
    if ifos == "None":
        return 0.0

    ifos = ifos.split(",")
    sngl_snrs = [sngl_snrs[ifo] for ifo in ifos]

    if len(ifos) == 1:
        return sorted(sngl_snrs, reverse=True)[0]

    elif len(ifos) >= 2:
        return sorted(sngl_snrs, reverse=True)[1]


def network_snr(snrs):
    """
    Compute network snr.
    """
    return numpy.linalg.norm([x for x in snrs if x])


def effective_spin(m1, m2, s1z, s2z):
    """
    Compute effective inspiral spin.
    """
    return (m1 * s1z + m2 * s2z) / (m1 + m2)


def effective_precession_spin(m1, m2, s1x, s1y, s2x, s2y):
    """
    Compute effective precession spin.
    See 10.1103/PhysRevD.91.024043 for
    details.
    """

    # determine the primary mass
    if m2 >= m1:
        m_pri = m2
        m_sec = m1
        s_pri = numpy.sqrt(s2x**2.0 + s2y**2.0)
        s_sec = numpy.sqrt(s1x**2.0 + s1y**2.0)
    else:
        m_pri = m1
        m_sec = m2
        s_pri = numpy.sqrt(s1x**2.0 + s1y**2.0)
        s_sec = numpy.sqrt(s2x**2.0 + s2y**2.0)

    q = m_pri / m_sec  # mass ratio >= 1
    a_pri = 2.0 + 3.0 / (2.0 * q)
    a_sec = 2.0 + 3.0 * q / 2.0

    # equation (3.3)
    sp = max(a_pri * s_pri, a_sec * s_sec)

    # equation (3.4)
    return sp / (a_pri * m_pri**2.0)


def calc_mu(mass1, mass2, spin1z, spin2z):
    """
    Calculate the first orthogonal PN phase coefficient
    see https://arxiv.org/abs/2007.09108 for details.
    """

    M = mass1 + mass2
    mchirp = (mass1 * mass2) ** 0.6 / M**0.2
    eta = mass1 * mass2 / M**2
    beta = (
        (113.0 * (mass1 / M) ** 2 + 75.0 * eta) * spin1z
        + (113.0 * (mass2 / M) ** 2 + 75.0 * eta) * spin2z
    ) / 12.0

    # the reference frequency below is taken from the literature. Please note
    # that the coefficients in the resultant linear combination depend on the
    # fref.
    fref = 200
    norm = G_SI * MSUN_SI / C_SI**3
    v = numpy.pi * mchirp * fref * norm
    psi0 = 3.0 / 4 / (8 * v) ** (5.0 / 3)
    psi2 = (20.0 / 9 * (743.0 / 336 + 11.0 / 4 * eta) * eta ** (-0.4) *
            v ** (2.0 / 3) * psi0)
    psi3 = (4 * beta - 16 * numpy.pi) / eta**0.6 * v * psi0

    # FIXME : the following linear combinations are taken from the ones in the
    # paper above, but this will need to be re-computed with o4 representitive
    # psd.
    mu1 = 0.974 * psi0 + 0.209 * psi2 + 0.0840 * psi3
    mu2 = -0.221 * psi0 + 0.823 * psi2 + 0.524 * psi3
    return mu1, mu2, beta


def eta_from_m1_m2(m1, m2):
    """
    Calculate the symmetric mass ratio given
    the component masses.
    """
    m1 = float(m1)
    m2 = float(m2)
    return (m1 * m2) / (m1 + m2) ** 2.0


def mchirp_from_m1_m2(m1, m2):
    """
    Calculate the chirp mass given the
    the component masses
    """
    m1 = float(m1)
    m2 = float(m2)
    return (m1 * m2) ** (3.0 / 5.0) / (m1 + m2) ** (1.0 / 5.0)


def parse_dq_topic(topic):
    pipeline, tag, topic = topic.split(".")
    ifo, topic = topic.split("_")

    return pipeline, tag, ifo, topic


def participating_ifos(sngltable):
    """
    Determine which ifos participated in an
    event, using an SNR threshold of 4.0 for
    inclusion.

    Parameters
    ----------
    sngltable
        ligolw SnglInspiral table

    Returns
    ----------
    ifos (str)
        string of comma separated ifos, eg
        "H1,L1,V1"
    """
    ifos = ""
    for r in sngltable:
        if r.snr >= 4.0:
            ifos += r.ifo
    return sort_ifos(ifos)


def sort_ifos(string):
    """
    Sort ifos in alphabetical order.

    Parameters
    ----------
    string (str)
        string of comma separated ifos, eg
        "H1,L1,V1"

    Returns
    ----------
    sorted_ifos (str)
        string of comma separated ifos in
        alphabetical order.
    """
    if not string:
        return "None"
    else:
        # return the sorted string of IFOs in alphabetical order
        list = string.split(",")
        list.sort()
        return ",".join(list)


def far_string(far, to_float=False):
    """
    we want to tag all of the output timeseries
    event data with a string indicating their FAR.

    Note: this was a workaround to account for the
    limitation that timeseries metadata in InfluxDB
    (ie tags) must be strings. This is not needed
    for trigger type data, since this data structure
    can include any number of numeric fields as meta
    data. This is kept in version 0.5.0 for backwards
    compatibility but will be deprecated in a future
    version.

    Thresholds are:
            * 1 per hour
            * 2 per day
            * 1 per month
            * 2 per year

    The far tag is a space delimited string of
    each threshold that is passed.

    Parameters
    ----------
        far (float or str)
           If string, must be one of: "oneperhour",
           "twoperday", "onepermonth", or "twoperday".
           Otherwise, any float.
        to_float (bool)
            if True, convert far string to float and return
    """

    if isinstance(far, str):
        # convert to float
        idx = list(FARSTRINGS_DICT.values()).index(far)
        far = list(FARSTRINGS_DICT.keys())[idx]
        if to_float:
            return far

    far_string = []
    for key, value in FARSTRINGS_DICT.items():
        if far <= key:
            far_string.append(value)

    return " ".join(far_string)
