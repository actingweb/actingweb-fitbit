import logging
import time
import base64
import json
import datetime
from actingweb import actor

FITBIT_URL = "https://api.fitbit.com/"


class Fitbit:

    def __init__(self, me=None, config=None, auth=None):
        if not me or not config or not auth:
            return
        self.myself = me
        self.auth = auth
        self.config = config
        self.myconf = {}
        self.my_config()

    def my_config(self, **kwargs):
        dirty = False
        if not self.myconf:
            self.myconf = self.myself.property.config
            if self.myconf:
                try:
                    self.myconf = json.loads(self.myconf)
                except json.JSONDecodeError:
                    self.myconf = {}
            else:
                dirty = True
                # Set default
                self.myconf = {
                    'save': True,
                    'ingest': False
                }
        if kwargs:
            for k, v in kwargs.items():
                dirty = True
                self.myconf[k] = v
        if dirty:
            self.myself.property.config = json.dumps(self.myconf)

    def get_heartrate(self, start=None, stop=None, detail=1):
        if not start:
            date_start = datetime.datetime.now().strftime('%Y-%m-%d')
            time_start = "00:00"
        else:
            date_start = start.strftime('%Y-%m-%d')
            time_start = start.strftime('%H:%M')
        if not stop:
            date_stop = datetime.datetime.now().strftime('%Y-%m-%d')
            time_stop = datetime.datetime.now().strftime('%H:%M')
        else:
            date_stop = stop.strftime('%Y-%m-%d')
            time_stop = stop.strftime('%H:%M')
        if detail == 1:
            detail = "1sec"
        else:
            detail == "1min"
        url = FITBIT_URL + "1/user/-/activities/heart/date/" + date_start + \
            "/" + date_stop + "/" + detail + "/time/" + time_start + "/" + time_stop + ".json"
        res = self.auth.oauth_get(url)
        return res

    def load(self):
        if not self.myconf.get('save', None):
            self.my_config(save=True)
        save = self.myconf['save']
        if save: 
            # Get and save last 10 minutes
            res = self.get_heartrate(datetime.datetime.now() - datetime.timedelta(minutes=5))
            last_datapoints = res.get('activities-heart-intraday', {}).get('dataset', [{}])
            self.myself.property.heartrate = json.dumps(last_datapoints)
        # Get since last time or 1 day
        if self.myself.property.last_load:
            last_load = datetime.datetime.strptime(self.myself.property.last_load, '%Y-%m-%dT%H:%M')
        else:
            last_load = datetime.datetime.now() - datetime.timedelta(days=1)
        res = self.get_heartrate(last_load)
        self.myself.property.last_load = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M')
        return res.get('activities-heart-intraday', {}).get('dataset', [{}])