"""SCOPE guard (Brandon Oct 29 / Oct 30). Hours, fees and closures: KENTUCKY ONLY. Parking, trails, camping: US + Canada.
Outlines and maps / pages: US + Canada + the world. The engine refuses a row outside a plug-in's scope here, in one place,
BEFORE the plug-in sees it (and every plug-in's wants() calls this too)."""
KY_ONLY = {'hours', 'fees', 'closures'}
NA_ONLY = {'parking', 'camping', 'trail'}
WORLD = {'outline', 'map', 'page', 'docs'}


class ScopeError(Exception):
    pass


def allowed(kind, area):
    """Per-plug-in on/off and allowed areas come from config/rules.json (defaults = the rules above, exactly).
    'map' and 'page' follow the docs plug-in's switch."""
    from core import rules
    k = 'docs' if kind in ('map', 'page') else kind
    if k not in rules.DEFAULTS['plugins']: return False
    return rules.area_ok(k, area or '')


def guard(kind, row):
    a = row.get('area') if isinstance(row, dict) else row
    if not allowed(kind, a): raise ScopeError(f'{kind} refuses {a}: out of scope')
    return row
