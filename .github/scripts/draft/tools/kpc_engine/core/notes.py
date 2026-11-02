"""The notes standard (Engine spec PART 3.5, method §10). Every result row carries:
  where_looked     each source and what it gave: hit / no hit / points only / blocked (reason)
  solved           PIN OFF: lat,lon, km, source | NAME SOLVED: agency calls it X | WRONG KIND: lighthouse | DELISTED ...
  why_this_record  name, distance, size, the confirming page
  confidence       sure / likely / weak, plus what a checker should double-check
'confidence' is a reading for the person who grades; it never turns into a YES (the engine decides nothing)."""


class Notes:
    def __init__(self):
        self.where_looked, self.solved, self.why, self.check = [], [], [], []
        self.confidence = None

    def looked(self, source, gave, url=None):
        r = {'source': source, 'gave': gave}
        if url: r['url'] = url
        self.where_looked.append(r); return self

    def solve(self, text): self.solved.append(text); return self
    def because(self, text): self.why.append(text); return self
    def double_check(self, text): self.check.append(text); return self

    def set_confidence(self, c, check=None):
        assert c in ('sure', 'likely', 'weak'), c
        self.confidence = c
        if check: self.check.append(check)
        return self

    def as_dict(self):
        return {'where_looked': self.where_looked, 'solved': '; '.join(self.solved), 'why_this_record': '; '.join(self.why),
                'confidence': {'level': self.confidence or 'weak', 'double_check': '; '.join(self.check)}}

    def any_blocked(self):
        return [w for w in self.where_looked if str(w['gave']).startswith('blocked')]

    def blocked_only(self):
        """True when every source we looked at was blocked: then the row may NOT say 'not found' (blocked is not 'no hit')."""
        return bool(self.where_looked) and all(str(w['gave']).startswith('blocked') for w in self.where_looked)


def confidence_of(tier, band, grade='official'):
    if grade == 'parcel': return 'weak', 'parcel under the pin: not the park line; check the owner and the record number'
    if grade != 'official': return 'weak', 'approximate source: never a full YES'
    if band == 'STRONG' and tier in ('T-1', 'T-2'): return 'sure', 'name + pin inside; check the size against the agency page'
    if tier in ('T-1', 'T-2', 'T-3'): return 'likely', 'check the kind of place and the size'
    return 'weak', 'name or pin only: read the agency map'
