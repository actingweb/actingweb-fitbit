import logging
import time
import base64
import json
import datetime
from cognite.client import CogniteClient
from cognite.client.data_classes import TimeSeries
from cognite.client.exceptions import CogniteAPIError, CogniteDuplicatedError

class Cognite:

    def __init__(self, me=None, project=None, environment=None):
        if not me or not project:
            return
        self.myself = me
        self.project = project
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
            self.check_timeseries()
        else:
            self.is_ok = False

    def check_timeseries(self):
        if self.myself.property.timeseries_id:
            return self.myself.property.timeseries_id
        try:
            ts = self.client.time_series.create(TimeSeries(name="heartrate_greger", 
                external_id="fitbit_greger", unit="beats"))
        except CogniteAPIError:
            self.is_ok = False
        except CogniteDuplicatedError:
            ts = self.client.time_series.retrieve(external_id="fitbit_greger")
        if ts and ts.id:
            self.myself.property.timeseries_id = str(ts.id)