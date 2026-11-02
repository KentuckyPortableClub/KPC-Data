"""A pretend ArcGIS server for offline tests. No network is used."""
import re
import urllib.parse


def square(lon, lat, size, dx=0.0):
    """Clockwise ring (an outer ring in Esri JSON)."""
    x0, y0, x1, y1 = lon + dx, lat, lon + dx + size, lat + size
    return [[x0, y0], [x0, y1], [x1, y1], [x1, y0], [x0, y0]]


class FakeWeb:
    def __init__(self, problem_cls):
        self.SourceProblem = problem_cls
        self.layers = {}      # url -> {"name_field", "edit", "agency_field", "records": {oid: {...}}, "status"}
        self.folders = {}     # folder url -> [{"name", "type"}]
        self.requests_made = 0
        self.log = []

    def add_layer(self, url, name_field, edit=None, agency_field=None):
        self.layers[url] = {"name_field": name_field, "edit": edit, "agency_field": agency_field,
                            "records": {}, "status": "ok"}
        return self.layers[url]

    def get_json(self, url, params=None, max_age_s=None, use_cache=True):
        params = dict(params or {})
        self.requests_made += 1
        self.log.append((url, params))
        base = re.sub(r"/query$", "", url)
        if base in self.folders:
            return {"services": self.folders[base]}
        lyr = self.layers.get(base)
        if lyr is None or lyr["status"] == "moved":
            raise self.SourceProblem("LAYER MOVED", "the server says: Service not found")
        if lyr["status"] == "down":
            raise self.SourceProblem("SOURCE DOWN", "no answer (ConnectionError)")
        nf = lyr["name_field"]
        if not url.endswith("/query"):
            meta = {"name": "test layer", "objectIdField": "OBJECTID", "fields": [{"name": "OBJECTID", "type": "esriFieldTypeOID"},
                                                     {"name": nf, "type": "esriFieldTypeString"}]}
            if lyr["edit"] is not None:
                meta["editingInfo"] = {"lastEditDate": lyr["edit"]}
            return meta
        recs = lyr["records"]
        if params.get("returnCountOnly") == "true":
            return {"count": len(recs)}
        if "objectIds" in params:
            want = [int(x) for x in params["objectIds"].split(",")]
            feats = []
            for o in want:
                if o in recs:
                    r = recs[o]
                    full = {"OBJECTID": o, nf: r["name"]}
                    if lyr["agency_field"]:
                        full[lyr["agency_field"]] = r.get("agency")
                    want_f = params.get("outFields", "*").split(",")
                    # like the real servers: only the fields asked for come back
                    attrs = {k: v for k, v in full.items() if "*" in want_f or k in want_f}
                    feats.append({"attributes": attrs, "geometry": {"rings": r["rings"]}})
            return {"features": feats}
        if params.get("returnDistinctValues") == "true":
            return {"features": [{"attributes": {nf: r["name"]}} for r in recs.values()]}
        if params.get("returnIdsOnly") == "true":
            w = params.get("where", "")
            m = re.search(r"UPPER\(\w+\)=UPPER\('(.*)'\)", w)
            if m:
                want = m.group(1).replace("''", "'").upper()
                return {"objectIds": [o for o, r in recs.items() if r["name"].upper() == want]}
            m = re.search(r"\w+='(.*?)'", w)
            if m:
                want = m.group(1).replace("''", "'")
                return {"objectIds": [o for o, r in recs.items() if r["name"] == want]}
            return {"objectIds": list(recs)}
        return {"features": []}
