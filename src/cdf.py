import logging
import time
import base64
import json
import datetime
from cognite.client import CogniteClient
from cognite.client.data_classes import TimeSeries
from cognite.client.exceptions import CogniteAPIError, CogniteDuplicatedError

class Cognite:

    def __init__(self, me=None, project=None, environment=None, ts_name=None, ts_ext_id=None):
        if not me or not project or not ts_name or not ts_ext_id:
            return
        self.myself = me
        self.project = project
        self.ts_name = ts_name
        self.ts_ext_id = ts_ext_id
        self.ts_id = None
        self.is_ok = False
        if environment:
            if environment == "greenfield":
                url="https://greenfield.cognitedata.com/"
            self.environment = environment
        else:
            url = "https://api.cognitedata.com/"
            self.environment = None
        self.api_key = self.myself.property.cdf_api_key
        self.client = CogniteClient(api_key=self.api_key, project=project, 
            client_name="actingweb_fitbit_v1", base_url=url, debug=True)
        status = self.client.login.status()
        if status.logged_in:
            self.is_ok = True
            self.ts_id = self.check_timeseries()
        else:
            self.is_ok = False

    def check_timeseries(self):
        if self.myself.property.timeseries_id:
            ts = self.client.time_series.retrieve(external_id=self.ts_ext_id)
            if ts and ts.id:
                self.myself.property.timeseries_id = str(ts.id)
                return ts.id
        try:
            ts = self.client.time_series.create(TimeSeries(name=self.ts_name, 
                external_id=self.ts_ext_id, unit="beats"))
        except CogniteAPIError:
            self.is_ok = False
        except CogniteDuplicatedError:
            ts = self.client.time_series.retrieve(external_id=self.ts_ext_id)
        if ts and ts.id:
            self.myself.property.timeseries_id = str(ts.id)
        return int(self.myself.property.timeseries_id)

    def ingest_timeseries(self, tuples):
        if not tuples:
            return False
        try:
            self.client.datapoints.insert(tuples, id=self.ts_id)
        except CogniteAPIError:
            logging.ERROR("API failure to ingest timeseries " + self.ts_id)
        return True