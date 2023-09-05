#!/usr/bin/env python

import os
import htcondor
import itertools
import yaml
from yaml.loader import SafeLoader

from gw.lts.utils import FARSTRINGS_DICT


def add_job_opts(job, prefix):
    opts = {
        "executable": os.path.join(prefix, f"bin/{job}"),
        "error": f"logs/{job}-$(cluster)-$(process).err",
        "output": f"logs/{job}-$(cluster)-$(process).out",
    }
    return opts


def add_job_args(opts):
    args = ""
    for k, v in opts.items():
        if isinstance(v, list):
            for vv in v:
                args += f'--{k.replace("_", "-")} {vv} '
        elif isinstance(v, bool):
            if v:
                args += f'--{k.replace("_", "-")} '
            else:
                continue
        else:
            args += f'--{k.replace("_", "-")} {v} '
    return {"arguments": args}


def get_topics(datasource, topic_suffix, tag):
    topics = []
    if len(datasource) >= len(topic_suffix):
        combinations = [
            list(zip(p, topic_suffix))
            for p in itertools.permutations(datasource, len(topic_suffix))
        ]
    else:
        combinations = [
            list(zip(datasource, p))
            for p in itertools.permutations(topic_suffix, len(datasource))
        ]
    for c in combinations:
        for pipeline, topic in c:
            topics.append(f"{pipeline}.{tag}.{topic}")
    return topics


def add_common_args(config, job):
    # FIXME: only one datasource is supported
    source = config["data-source"][0]

    job_args = {}
    job_args.update({
        "tag": config["tag"],
        "kafka_server": config["kafka_server"],
        "scald_config": config["metrics"][source]["config"],
    })

    for arg, val in config["jobs"][job].items():
        # input topic arg is handled differently
        if arg == "input_topic":
            continue
        job_args.update({arg: val})

    return job_args


def send_inj_stream_layer(dag, config, opts, prefix):
    # add job options
    opts.update(add_job_opts("send-inj-stream", prefix))

    job_args = {}

    # add job arguments
    job_args.update(add_common_args(config, "send_inj_stream"))
    job_args.update({"data_source": config["data-source"]})
    job_args.update({"inj-file": config["injections"]})
    job_args.update({"ifo": [ifo for ifo in config["ifos"].split(",")]})

    this_job_opts = config["jobs"]["send_inj_stream"]
    if this_job_opts["track-psd"] or this_job_opts["track-segments"]:
        job_args.update({
            "input-topic": [topic for topic in this_job_opts["input_topic"]]
        })

    opts.update(add_job_args(job_args))

    # add job to the dag
    dag.layer(
        name="send_inj_stream",
        submit_description=htcondor.Submit(opts), retries="1000"
    )
    return dag


def inspinjmsg_find_layer(dag, config, opts, prefix):
    # add job options
    opts.update(add_job_opts("inspinjmsg-find", prefix))

    job_args = {}

    # add job arguments
    job_args.update(add_common_args(config, "inspinjmsg_find"))
    tag = config["tag"]
    topics = get_topics(
        config["data-source"],
        config["jobs"]["inspinjmsg_find"]["input_topic"],
        f"{tag}.testsuite",
    )
    job_args.update({"input_topic": topics})
    opts.update(add_job_args(job_args))

    # add job to the dag
    dag.layer(
        name="inspinjmsg_find",
        submit_description=htcondor.Submit(opts), retries="1000"
    )
    return dag


def igwn_alert_listener_layer(dag, config, opts, prefix):
    # add job options
    opts.update(add_job_opts("igwn-alert-listener", prefix))

    job_args = {}

    # add job arguments
    job_args.update(add_common_args(config, "igwn_alert_listener"))
    job_args.update({"gracedb_server": config["gracedb_server"]})
    opts.update(add_job_args(job_args))

    # add job to the dag
    dag.layer(
        name="igwn_alert_listener",
        submit_description=htcondor.Submit(opts),
        retries="1000",
    )
    return dag


def inj_missed_found_layer(dag, config, opts, prefix):
    # add job options
    opts.update(add_job_opts("inj-missed-found", prefix))
    for i, source in enumerate(config["data-source"]):
        job_args = {}

        # add job arguments
        job_args.update(add_common_args(config, "inj_missed_found"))
        tag = config["tag"]
        topics = get_topics(
            [source],
            config["jobs"]["inj_missed_found"]["input_topic"],
            f"{tag}.testsuite",
        )
        job_args.update({"input_topic": topics})
        opts.update(add_job_args(job_args))

        # add job to the dag
        dag.layer(
            name=f"inj_missed_found_{int(i):04d}",
            submit_description=htcondor.Submit(opts),
            retries="3",
        )
    return dag


def vt_layer(dag, config, opts, prefix):
    # add job options
    opts.update(add_job_opts("vt", prefix))

    # for each datasource provided in the config we need to
    # add one calculate-expected job if that option is given
    # in the config. Then we need to add a job to compute VT
    # with each far threshold
    far_thresholds = FARSTRINGS_DICT.keys()
    num_far_jobs = len(far_thresholds)
    tag = config["tag"]
    for i, source in enumerate(config["data-source"]):
        # add job arguments
        job_args = {}
        job_args.update(add_common_args(config, "vt"))

        topics = get_topics(
            [source], config["jobs"]["vt"]["input_topic"], f"{tag}.testsuite"
        )

        job_args.update(
            {
                "data_source": source,
                "input_topic": topics,
                "inj-file": config["injections"],
            }
        )

        if "calculate-expected" in job_args.keys():
            opts.update(add_job_args(job_args))
            dag.layer(
                name=f"expected_vt_{int(i):04d}",
                submit_description=htcondor.Submit(opts),
                retries="3",
            )

            # remove the options for expected VT calculation
            # so we can move on to add regualr VT jobs that
            # dont take this option
            job_args.pop("calculate-expected")

        for f, far_thresh in enumerate(far_thresholds):
            job_args.update(
                {
                    "far-threshold": far_thresh,
                }
            )

            opts.update(add_job_args(job_args))
            dag.layer(
                name=f"vt_{((num_far_jobs * int(i)) + f):04d}",
                submit_description=htcondor.Submit(opts),
                retries="3",
            )

    return dag


def latency_layer(dag, config, opts, prefix):
    # add job options
    opts.update(add_job_opts("latency", prefix))

    job_args = {}

    # add job arguments
    job_args.update(add_common_args(config, "latency"))
    tag = config["tag"]
    topics = get_topics(
        config["data-source"],
        config["jobs"]["latency"]["input_topic"],
        f"{tag}.testsuite",
    )
    job_args.update({"input_topic": topics})
    opts.update(add_job_args(job_args))

    # add job to the dag
    dag.layer(
        name="latency",
        submit_description=htcondor.Submit(opts), retries="3"
    )

    return dag


def likelihood_layer(dag, config, opts, prefix):
    # add job options
    opts.update(add_job_opts("likelihood", prefix))

    job_args = {}

    # add job arguments
    job_args.update(add_common_args(config, "likelihood"))
    tag = config["tag"]
    topics = get_topics(
        config["data-source"],
        config["jobs"]["likelihood"]["input_topic"],
        f"{tag}.testsuite",
    )
    job_args.update({"input_topic": topics})
    opts.update(add_job_args(job_args))

    # add job to the dag
    dag.layer(
        name="likelihood",
        submit_description=htcondor.Submit(opts), retries="3"
    )

    return dag


def em_bright_layer(dag, config, opts, prefix):
    # add job options
    opts.update(add_job_opts("em-bright", prefix))

    job_args = {}

    # add job arguments
    job_args.update(add_common_args(config, "em_bright"))
    tag = config["tag"]
    topics = get_topics(
        config["data-source"],
        config["jobs"]["em_bright"]["input_topic"],
        f"{tag}.testsuite",
    )
    job_args.update({"input_topic": topics})
    job_args.update({"gracedb_server": config["gracedb_server"]})
    opts.update(add_job_args(job_args))

    # add job to the dag
    dag.layer(
        name="em_bright",
        submit_description=htcondor.Submit(opts), retries="3"
    )

    return dag


def p_astro_layer(dag, config, opts, prefix):
    # add job options
    opts.update(add_job_opts("p-astro", prefix))

    job_args = {}

    # add job arguments
    job_args.update(add_common_args(config, "p_astro"))
    tag = config["tag"]
    topics = get_topics(
        config["data-source"],
        config["jobs"]["p_astro"]["input_topic"],
        f"{tag}.testsuite",
    )
    job_args.update({"input_topic": topics})
    if "gdb-pastros" in job_args.keys():
        job_args.update({"gracedb_server": config["gracedb_server"]})
    opts.update(add_job_args(job_args))

    # add job to the dag
    dag.layer(
        name="p_astro",
        submit_description=htcondor.Submit(opts), retries="3"
    )

    return dag


def skymap_layer(dag, config, opts, prefix):
    # add job options
    opts.update(add_job_opts("skymap", prefix))

    job_args = {}

    # add job arguments
    job_args.update(add_common_args(config, "skymap"))
    tag = config["tag"]
    topics = get_topics(
        config["data-source"],
        config["jobs"]["skymap"]["input_topic"],
        f"{tag}.testsuite",
    )
    job_args.update({"input_topic": topics})
    if "gdb-skymaps" in job_args.keys():
        job_args.update({"gracedb_server": config["gracedb_server"]})
    opts.update(add_job_args(job_args))

    # add job to the dag
    dag.layer(
        name="skymap",
        submit_description=htcondor.Submit(opts), retries="3"
    )

    return dag


def snr_consistency_layer(dag, config, opts, prefix):
    # add job options
    opts.update(add_job_opts("snr-consistency", prefix))

    job_args = {}

    # add job arguments
    job_args.update(add_common_args(config, "snr_consistency"))
    tag = config["tag"]
    topics = get_topics(
        config["data-source"],
        config["jobs"]["snr_consistency"]["input_topic"],
        f"{tag}.testsuite",
    )

    job_args.update({"input_topic": topics})
    job_args.update({"ifo": config["ifos"].split(",")})
    opts.update(add_job_args(job_args))

    # add job to the dag
    dag.layer(
        name="snr_consistency",
        submit_description=htcondor.Submit(opts), retries="3"
    )

    return dag


def inj_accuracy_layer(dag, config, opts, prefix):
    # add job options
    opts.update(add_job_opts("inj-accuracy", prefix))
    for i, source in enumerate(config["data-source"]):
        job_args = {}

        # add job arguments
        job_args.update(add_common_args(config, "inj_accuracy"))
        tag = config["tag"]
        topics = get_topics(
            config["data-source"],
            config["jobs"]["inj_accuracy"]["input_topic"],
            f"{tag}.testsuite",
        )
        job_args.update({"input_topic": topics})
        opts.update(add_job_args(job_args))

        # add job to the dag
        dag.layer(
            name=f"inj_accuracy_{int(i):04d}",
            submit_description=htcondor.Submit(opts),
            retries="3",
        )

    return dag


def collect_metrics_layer(dag, config, config_path, opts, prefix):
    # load options from the config

    kafka_server = config["kafka_server"]
    tag = config["tag"]

    for i, source in enumerate(config["data-source"]):
        # grab the web config
        web_config_path = config["metrics"][source]["config"]
        with open(web_config_path, "r") as f:
            web_config = yaml.load(f, Loader=SafeLoader)

        # add job options
        log_base_name = "logs/scald_metric_collector"
        opts.update(
            {
                "executable": os.path.join(prefix, "bin/scald"),
                "error": f"{log_base_name}-$(cluster)-$(process).err",
                "output": f"{log_base_name}-$(cluster)-$(process).out",
            }
        )

        metrics = [metric for metric in web_config["schemas"]]
        # these metrics are special, they dont get aggregated
        # by the metric collector
        metrics_to_remove = (
            "triggers", "missed_triggers", "analysis_start",
            "parameter_accuracy", "embright", "source_class",
            "sky_loc", "snr_accuracy",
        )
        for metric in metrics_to_remove:
            if metric in metrics:
                metrics.remove(metric)

        # add scald jobs to process all metrics in groups of 4
        for j, metric_group in enumerate(scald_topics_grouper(metrics, 4)):
            arguments = (
                f"aggregate --config {web_config_path} " +
                f"--uri kafka://{tag}@{kafka_server} " +
                "--data-type timeseries "
            )
            for metric in metric_group:
                arguments += (
                    f"--topic {source}.{tag}.testsuite.{metric} " +
                    f"--schema {metric} "
                )
            opts.update({"arguments": arguments})

            dag.layer(
                name=f"scald_metric_collector_{i*1000+j:04d}",
                submit_description=htcondor.Submit(opts),
                retries="1000",
            )

    return dag


def scald_topics_grouper(seq, size):
    return (seq[idx: idx + size] for idx in range(0, len(seq), size))
