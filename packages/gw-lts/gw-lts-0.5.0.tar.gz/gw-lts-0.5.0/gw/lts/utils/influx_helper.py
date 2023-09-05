#!/usr/bin/env python3

import sys
import yaml
from collections import defaultdict, deque

from ligo.scald.io import influx
from lal import GPSTimeNow


class InfluxHelper(object):
    def __init__(self, config_path=None, routes={}, reduce_time=100.):
        # set up dicts to store trigger information
        self.routes = list(routes.keys())
        agg = {}
        for route, value in routes.items():
            agg[route] = value["aggregate"]
        self.aggregate = agg
        self.triggers = {
            route: defaultdict(
                lambda: {
                    "time": deque(maxlen=1000),
                    "fields": defaultdict(lambda: deque(maxlen=1000)),
                }
            )
            for route in self.routes
        }
        self.last_trigger_snapshot = None
        self.reduce_time = reduce_time

        # set up influx configuration
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        self.influx_sink = influx.Aggregator(**config["backends"]["default"])
        self.influx_sink.load(path=config_path)

    def store_triggers(self, time, data, route=None, tags=None):
        self.triggers[route][tags]["time"].append(time)
        this_triggers = self.triggers[route][tags]["fields"]
        for key, value in data.items():
            this_triggers[key].append(value)

        # output data to influx if enough time has passed
        now = float(GPSTimeNow())
        if not self.last_trigger_snapshot or (
            now - self.last_trigger_snapshot >= self.reduce_time
        ):
            self.last_trigger_snapshot = now
            self.write_triggers()

    def write_triggers(self, ):
        # cast data from deques to lists to output
        outdata = {}
        for key in self.triggers:
            outdata[key] = {}
            for tag, value in self.triggers[key].items():
                outdata[key][tag] = {
                    "time": list(value["time"]),
                    "fields": {
                        dataname: list(datadeq)
                        for dataname, datadeq in value["fields"].items()
                    },
                }

        # finally, write to influxdb
        for route in self.routes:
            if outdata[route]:
                print(f"Writing {route} to influx...", file=sys.stderr)
                self.influx_sink.store_columns(
                    route, outdata[route], aggregate=self.aggregate[route]
                )
