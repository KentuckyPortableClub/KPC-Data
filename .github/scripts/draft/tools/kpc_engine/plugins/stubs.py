"""Plug-ins with a slot but no worker yet (Engine spec PART 5): they accept no rows and say so on the board."""
from .base import Plugin


class Stub(Plugin):
    WHY = 'not built yet'

    def wants(self, row): return False
    def work_row(self, agency, row, eng, pass_no): return None
    def write(self, results, out_dir, eng=None): pass
    def grade(self, results, eng): return {'stub': self.WHY}


class Cell(Stub): KIND = 'cell'; WHY = 'cell coverage: needs the FCC / ISED coverage maps reader (not built)'
class Acres(Stub): KIND = 'acres'; WHY = 'acres: outline plug-in writes acres_approx; a full acreage check is not built'
class MissedFers(Stub): KIND = 'missed_fers'; WHY = 'missed 2-fers: needs the club key polygons for overlap (not built)'
class GpsPack(Stub): KIND = 'gps_pack'; WHY = 'GPS packs: built from approved outlines only, after chat 11 (not built)'
class BoundaryChanges(Stub): KIND = 'boundary_changes'; WHY = 'boundary changes: needs two dated copies of a layer (not built)'


ALL = [Cell(), Acres(), MissedFers(), GpsPack(), BoundaryChanges()]
