#!/usr/bin/env python

import os
import tempfile
from optparse import OptionParser

import yaml
from yaml.loader import SafeLoader

from htcondor import dags as htcondor_dags

from gw.lts import dags as gwlts_dags


def parse_command_line():
    parser = OptionParser()
    parser.add_option(
        "-v", "--verbose", action="store_true", help="Be verbose."
    )
    parser.add_option("-c", "--config", help="Path to config.yml.")
    parser.add_option(
        "-n", "--name", default="test_suite", help="Name for the DAG file."
    )
    parser.add_option("-p", "--prefix", help="Prefix for executables")
    opts, args = parser.parse_args()

    return opts, args


class DAG(object):
    def __init__(self, options):
        self.jobs = {
            "send_inj_stream": gwlts_dags.send_inj_stream_layer,
            "inspinjmsg_find": gwlts_dags.inspinjmsg_find_layer,
            "igwn_alert_listener": gwlts_dags.igwn_alert_listener_layer,
            "inj_missed_found": gwlts_dags.inj_missed_found_layer,
            "vt": gwlts_dags.vt_layer,
            "latency": gwlts_dags.latency_layer,
            "p_astro": gwlts_dags.p_astro_layer,
            "skymap": gwlts_dags.skymap_layer,
            "snr_consistency": gwlts_dags.snr_consistency_layer,
            "inj_accuracy": gwlts_dags.inj_accuracy_layer,
            "likelihood": gwlts_dags.likelihood_layer,
            "em_bright": gwlts_dags.em_bright_layer,
            "scald_metric_collector": gwlts_dags.collect_metrics_layer,
        }

        self.config_path = options.config
        self.prefix = options.prefix
        self.config = self.load_config(self.config_path)
        self.retries = "3"

        self.dag_name = options.name
        self.dag = htcondor_dags.DAG()

        self.verbose = options.verbose

    def load_config(self, config_path):
        config = {}

        with open(config_path, "r") as f:
            config = yaml.load(f, Loader=SafeLoader)

        return config

    def create_dag(self):
        if self.verbose:
            print("Building DAG...")
        opts = self.condor_opts()

        # add jobs
        for job in self.config["jobs"]:
            self.dag = self.jobs[job](self.dag, self.config, opts, self.prefix)

        # add a scald metric collector job for each datasource
        self.dag = self.jobs["scald_metric_collector"](
            self.dag, self.config, self.config_path, opts, self.prefix
        )

        if self.verbose:
            print(f"Writing DAG out to file: {self.dag_name}.dag")
        htcondor_dags.write_dag(
            self.dag, os.getcwd(), dag_file_name=f"{self.dag_name}.dag"
        )

        return self.dag

    def write_script(self):
        if self.verbose:
            print(f"Writing script out to file: {self.dag_name}.sh")
        with open(f"{self.dag_name}.sh", "w") as f:
            jobnames = []
            for layer in self.dag.walk():
                executable = layer.submit_description["executable"]
                args = layer.submit_description["arguments"]
                jobname = executable.split("/")[-1]

                jobnames.extend([jobname])
                if jobname in jobnames:
                    jobname = jobname + f"_{int(jobnames.count(jobname)):04d}"

                print(f"# Job {jobname}", file=f)
                print(executable + " " + args + "\n", file=f)

    def condor_opts(self):
        # set up condor logging
        tempfile.tempdir = os.environ["TMPDIR"]
        fd, logfile = tempfile.mkstemp()
        with os.fdopen(fd, "w"):
            pass

        # set up general condor options across all jobs
        opts = {
            "want_graceful_removal": True,
            "getenv": True,
            "kill_sig": 15,
            "log": logfile,
            "notification": "never",
        }

        opts.update(self.config["condor"])

        return opts


def main():
    # parse command line options
    opts, args = parse_command_line()

    if not opts.config:
        raise Exception("You need to specify a config file.")

    if not opts.prefix:
        raise Exception(
            "You need to specify the location of the executable files " +
            "with --prefix."
        )

    # build the dag
    dag_generator = DAG(opts)

    dag_generator.create_dag()
    dag_generator.write_script()

    # make a directory for logs
    if not os.path.exists("logs"):
        os.mkdir("logs")


if __name__ == "__main__":
    main()
