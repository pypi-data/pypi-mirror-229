#!/usr/bin/env python

import os
import http.client

from ligo.gracedb.rest import GraceDb
from ligo.gracedb.exceptions import HTTPError


class GraceDbHelper(object):
    def __init__(self, group):
        self.group = group
        service_url = f"https://{self.group}.ligo.org/api/"
        self.client = GraceDb(service_url=service_url)

    def get_event(
                  self, uid=None, time=None, pipeline=None,
                  search=None, retries=10):
        tries = 1
        while tries <= retries:
            try:
                if uid:
                    event = self.client.event(uid).json()
                    break

                else:
                    query = ""
                    if time:
                        query += f"{time - 1.} .. {time + 1.} "
                    if pipeline:
                        query += f"pipeline: {pipeline} "

                    if search:
                        query += f"search: {search} "

                    event = next(self.client.events(query)).json()
                    break

            except HTTPError:
                tries += 1

        return event

    def query_file(self, graceid, filename, outpath=None, tag=None):
        """
        Download a file from given GraceDb event.
        Optionally write out the file to disk.
        Return the file.
        """
        try:
            response = self.client.files(graceid, filename)
            if response.status == http.client.OK:
                if outpath:
                    outfile = os.path.join(outpath, f"{tag}-{graceid}.fits")
                    with open(outfile, "wb") as f:
                        f.write(response.read())
        except HTTPError:
            response = None

        return response
