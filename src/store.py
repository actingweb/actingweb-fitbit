import datetime
from actingweb import attribute

class GlobalStore():

    def __init__(self, id=None, config=None, bucket=None):
        if not config:
            return
        self.id = id
        self.config = config
        if not bucket:
            self.bucket = "global"
        else:
            self.bucket = bucket

    def set_attr(self, name, data=None):
        if not self.id:
            return False
        ts = datetime.datetime.now()
        if not name:
            return False
        if not data:
            data = ''
        message_bucket = attribute.Attributes(self.bucket, self.id, config=self.config)
        try:
            message_bucket.set_attr(
                name,
                data=data,
                timestamp=ts
            )
        except Exception as e:
            return False
        return True

    def get_attr(self, name=None):
        if not name:
            return {}
        if not self.id:
            return None
        message_bucket = attribute.Attributes(self.bucket, self.id, config=self.config)
        res = message_bucket.get_bucket()
        ret = {}
        for m, v in res.items():
            if m == name:
                ret = {
                        "data": v["data"],
                        "timestamp": v["timestamp"]
                    }
        return ret

    def get_attrs(self):
        if not self.id:
            return None
        message_bucket = attribute.Attributes(self.bucket, self.id, config=self.config)
        res = message_bucket.get_bucket()
        ret = []
        for m, v in res.items():
            ret.append({ 
                m: {
                    "data": v["data"],
                    "timestamp": v["timestamp"]
                }
            }
            )
        return ret

    def get_bucket(self, filter=None):
        message_bucket = attribute.Buckets(self.bucket, config=self.config)
        msgs = message_bucket.fetch()
        ret = []
        if not msgs:
            return ret
        for m, v in msgs.items():
            for a, b in v.items():
                if not filter or (filter and a == filter):
                    ret.append({
                        "id": m,
                        a: {
                            "data": b["data"],
                            "timestamp": b["timestamp"]
                        }
                    })
        return ret