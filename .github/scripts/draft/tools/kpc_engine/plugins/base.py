"""What every plug-in has (Engine spec PART 4): KIND, wants(gap_row), work(agency_group, engine), write(results, out_dir),
grade(results, engine). work() is a loop over work_row() so the engine's workers / passes can drive single rows."""
import datetime as dt, json, pathlib
from core import scope


class Plugin:
    KIND = 'base'
    GAP_KINDS = ()          # which gap kinds this plug-in answers

    def wants(self, row):
        return any(k in row.get('kinds', []) for k in self.GAP_KINDS) and scope.allowed(self.KIND, row.get('area'))

    def work(self, agency_group, engine):
        agency, rows = agency_group
        return [self.work_row(agency, r, engine, 1) for r in rows if self.wants(r)]

    def work_row(self, agency, row, engine, pass_no):
        raise NotImplementedError

    def write(self, results, out_dir):
        raise NotImplementedError

    def grade(self, results, engine):
        n = len(results); f = sum(1 for r in results if r.get('status') in ('found', 'candidate'))
        b = sum(1 for r in results if r.get('status') == 'blocked')
        return {'rows': n, 'found_or_candidate': f, 'blocked': b, 'hit_rate': round(f / n, 3) if n else None}


def today(): return dt.date.today().isoformat()


def dump(obj, path):
    path = pathlib.Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    json.dump(obj, open(tmp, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    tmp.replace(path)
