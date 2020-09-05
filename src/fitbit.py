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
        if detail == 1:
            detail = "1sec"
        else:
            detail == "1min"
        url = None
        if not start:
            # Today and get the whole day
            date_start = datetime.datetime.now().strftime('%Y-%m-%d')
            url = FITBIT_URL + "1/user/-/activities/heart/date/" + date_start + \
                "/1d/" + detail + ".json"
        else:
            # Start from a specific timestamp
            date_start = start.strftime('%Y-%m-%d')
            time_start = start.strftime('%H:%M')
            if stop:
                # Set a specific stop
                date_stop = stop.strftime('%Y-%m-%d')
                time_stop = stop.strftime('%H:%M')
            else:
                # Less than a day
                if (start + datetime.timedelta(days=1)) > datetime.datetime.now():
                    # Set stop now
                    date_stop = datetime.datetime.now().strftime('%Y-%m-%d')
                    time_stop = datetime.datetime.now().strftime('%H:%M')
                else:
                    # Get a full day
                    url = FITBIT_URL + "1/user/-/activities/heart/date/" + date_start + \
                        "/1d/" + detail + ".json"
        if not url:
            url = FITBIT_URL + "1/user/-/activities/heart/date/" + date_start + \
                "/" + date_stop + "/" + detail + "/time/" + time_start + "/" + time_stop + ".json"
        res = self.auth.oauth_get(url)
        return res

    def make_tuples(self, date=None, datapoints=None):
        if not datapoints or not date:
            return []
        ret = list()
        for i in datapoints:
            ts = date.replace(hour=0, minute=0, second=0, microsecond=0) + \
                datetime.timedelta(
                    hours=int(i['time'][0:2]), 
                    minutes=int(i['time'][3:5]),
                    seconds=int(i['time'][6:8])
                )
            item = (ts, i['value'])
            ret.append(tuple(item))
        return ret

    def load_lastten(self):
        res = self.get_heartrate(datetime.datetime.now() - datetime.timedelta(minutes=20))
        last_datapoints = res.get('activities-heart-intraday', {}).get('dataset', [{}])
        return last_datapoints[0:10]


    def load_day(self, date=None):
        # Get since last time or 1 day
        if not date:
            date = datetime.datetime.now() - datetime.timedelta(days=1)
        r = self.get_heartrate(start=date)
        res = self.make_tuples(date, r.get('activities-heart-intraday', {}).get('dataset', [{}]))
        return res

    # Load since start, default last 24h
    def load(self, start=None, stop=None):
        # Get since last time or 1 day
        if not start:
            start = datetime.datetime.now() - datetime.timedelta(days=1)
        if not stop:
            stop = datetime.datetime.now()
        res = list()
        while (start < stop):
            res = res + list(self.load_day(start))
            start = start + datetime.timedelta(days=1)
        return res
  