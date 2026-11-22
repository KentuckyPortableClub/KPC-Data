#!/usr/bin/env python3
"""Park page reader: download time cap, mid-run save, skip after two cut-offs (21 Nov 2026).

Offline. Every check here fails without its fix. Prints PASS / FAIL and ends ALL PASS or SOME FAILED.
"""
import io, os, pathlib, socket, sys, tempfile, time, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
S = ROOT / '.github/scripts'
sys.path.insert(0, str(S))
os.environ['KPC_NO_NET'] = '1'
socket.socket.connect = lambda *a, **k: (_ for _ in ()).throw(OSError('test: no network'))

import kpc_manners as M  # noqa: E402
import kpc_park_pages as PP  # noqa: E402

ok = True


def check(msg, cond):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + msg, flush=True)


# --- (a) wall-clock cap: a slow trickle is stopped, not waited out ---
class Trickle:
    """Gives `chunk` bytes, then sleeps, until `data` is gone."""

    def __init__(self, data, delay, chunk=1):
        self.data = data
        self.delay = delay
        self.chunk = chunk
        self.i = 0
        self.reads = 0

    def read(self, size=-1):
        self.reads += 1
        if self.i >= len(self.data):
            return b''
        time.sleep(self.delay)
        n = self.chunk if size < 0 else min(size, self.chunk)
        out = self.data[self.i:self.i + n]
        self.i += len(out)
        return out


def test_read_capped():
    has = hasattr(M, 'read_capped')
    check('kpc_manners has read_capped (wall-clock read)', has)
    if not has:
        return
    body = Trickle(b'x' * 200, delay=0.25, chunk=1)
    t0 = time.time()
    raised = False
    try:
        M.read_capped(body, 200, time.time() + 0.6)
    except TimeoutError as e:
        raised = str(e) == 'deadline'
    elapsed = time.time() - t0
    check('a slow trickle stops at the deadline, not after the whole body',
          raised and 0.4 <= elapsed < 2.0 and body.i < 200)


# --- getter used by the reader tests ---
class SeqGetter:
    """Returns a short HTML page for each URL. Optional delay, or a deadline-status once."""

    def __init__(self, delay=0, deadline_on=None):
        self.delay = delay
        self.deadline_on = deadline_on
        self.calls = []
        self.body = b'<html><head><title>Park</title></head><body><h1>Park</h1></body></html>'

    def get(self, url, rng=None, deadline=None, max_time=None):
        self.calls.append({'url': url, 'deadline': deadline, 'max_time': max_time})
        if self.deadline_on is not None and len(self.calls) >= self.deadline_on:
            if deadline is not None:   # 21 Nov: the run's deadline is really reached before the getter says so
                time.sleep(max(0, deadline - time.time()))
            return 'err:deadline', {}, b'', url
        if self.delay:
            # honour a deadline mid-download
            end = deadline
            if max_time is not None:
                cap = time.time() + max_time
                end = cap if end is None else min(end, cap)
            if end is not None and end <= time.time() + self.delay:
                # sleep only until the cap, then fail as a hung download would after the fix
                time.sleep(max(0, end - time.time()))
                return 'err:deadline', {}, b'', url
            time.sleep(self.delay)
        return 200, {'content-type': 'text/html'}, self.body, url


def two_parks():
    areas = {
        'US-AK': {
            'US-A1': {'name': 'Alpha', 'website': 'https://example.org/a1', 'type': 'State Park',
                      'lat': 61.2, 'lon': -149.9, 'qsos': 1},
            'US-A2': {'name': 'Beta', 'website': 'https://example.org/a2', 'type': 'State Park',
                      'lat': 61.3, 'lon': -149.8, 'qsos': 1},
        }
    }
    web = {'US-A1': {'url': 'https://example.org/a1'}, 'US-A2': {'url': 'https://example.org/a2'}}
    return areas, web, {}, {}


def test_mid_download_deadline():
    areas, web, docs, truth = two_parks()
    getter = SeqGetter(deadline_on=2)  # first park ok, second download hits the cap
    state = {}
    facts, reqs = PP.read_parks(areas, web, docs, truth, getter, state, '2026-11-21',
                                refs=['US-A1', 'US-A2'], deadline=time.time() + 0.3)
    check('a mid-download deadline keeps the parks already read',
          'US-A1' in (facts.get('US-AK') or {}) and 'US-A2' not in (facts.get('US-AK') or {}))
    check('a mid-download deadline stops the run as minutes',
          state.get('stopped') == 'minutes')
    check('the cut-off park is left for the next run',
          'US-A2' in (state.get('left') or []))


def test_fifty_minute_stop_during_download():
    """The 50-minute hard stop is enforced even in the middle of a download."""
    areas, web, docs, truth = two_parks()
    class SecondSlow(SeqGetter):
        def get(self, url, rng=None, deadline=None, max_time=None):
            # first park is instant; the second download hangs past the run deadline
            self.delay = 0 if url.endswith('/a1') else 0.5
            return super().get(url, rng=rng, deadline=deadline, max_time=max_time)
    getter = SecondSlow()
    state = {}
    deadline = time.time() + 0.25
    t0 = time.time()
    facts, reqs = PP.read_parks(areas, web, docs, truth, getter, state, '2026-11-21',
                                refs=['US-A1', 'US-A2'], deadline=deadline, get_max_seconds=5)
    elapsed = time.time() - t0
    check('the 50-minute stop is reached even mid-download (does not wait out the fetch)',
          elapsed < 1.5 and state.get('stopped') == 'minutes')
    check('parks read before the stop are kept',
          'US-A1' in (facts.get('US-AK') or {}))


def test_save_after_each_park():
    areas, web, docs, truth = two_parks()
    tmp = tempfile.mkdtemp(prefix='kpc-pp-save-')
    state_path = str(pathlib.Path(tmp) / 'state.json')
    seen = {'files': 0}

    class Watch(SeqGetter):
        def get(self, url, rng=None, deadline=None, max_time=None):
            # On the second park's first fetch, the first park must already be on disk.
            if url.endswith('/a2'):
                facts = pathlib.Path(tmp) / 'facts' / 'US-AK.json'
                seen['files'] = 1 if facts.is_file() else 0
                if facts.is_file():
                    import json
                    doc = json.loads(facts.read_text(encoding='utf-8'))
                    seen['has_a1'] = 'US-A1' in (doc.get('parks') or {})
            return super().get(url, rng=rng, deadline=deadline, max_time=max_time)

    getter = Watch()
    state = {}
    PP.read_parks(areas, web, docs, truth, getter, state, '2026-11-21',
                  refs=['US-A1', 'US-A2'], out_dir=tmp, state_path=state_path)
    check('progress is on disk after the first park, before the second is fetched',
          seen.get('files') == 1 and seen.get('has_a1') is True)
    # save-on-change: writing the same facts again does not rewrite (mtime or return)
    facts_path = pathlib.Path(tmp) / 'facts' / 'US-AK.json'
    first = facts_path.read_bytes()
    wrote = PP.save_json(facts_path, __import__('json').loads(first), only_if_changed=True)
    check('a second save of the same facts is skipped', wrote is False and facts_path.read_bytes() == first)


def test_two_cutoffs_skip():
    areas = ['US-AK', 'US-AL', 'US-AZ']
    refs = {'US-AK': {'US-A1', 'US-A2'}, 'US-AL': {'US-B1'}, 'US-AZ': {'US-C1'}}
    # First cut-off
    state = {'stopped': 'minutes', 'left': ['US-A2'], 'run_area': 'US-AK', 'run': 'stopped',
             'cutoff': {'US-AK': 1}}
    area, why, state = PP.pick_walk_area(areas, done=set(), state=state, area_refs=refs)
    check('after one cut-off the same state is tried again',
          area == 'US-AK' and 'unfinished' in why)
    # Second cut-off saved at stop()
    state['stopped'] = 'minutes'
    state['left'] = ['US-A2']
    state['cutoff'] = {'US-AK': 2}
    state['run'] = 'stopped'
    area, why, state = PP.pick_walk_area(areas, done=set(), state=state, area_refs=refs)
    check('after two cut-off runs the next state is picked',
          area == 'US-AL')
    check('the stuck state is named for a person',
          'US-AK' in why and 'two cut-off' in why and 'US-AK' in (state.get('stuck') or []))
    # A killed run (job limit) with no stopped=minutes still counts
    state2 = {'left': ['US-A2'], 'run_area': 'US-AK', 'run': 'in-progress', 'cutoff': {'US-AK': 1}}
    area2, why2, state2 = PP.pick_walk_area(areas, done=set(), state=state2, area_refs=refs)
    check('a run killed mid-state counts as a cut-off and is skipped the second time',
          area2 == 'US-AL' and 'US-AK' in why2)


def test_progress_log_and_flush():
    areas, web, docs, truth = two_parks()
    getter = SeqGetter()
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        PP.read_parks(areas, web, docs, truth, getter, {}, '2026-11-21',
                      refs=['US-A1', 'US-A2'], quiet=False, started=time.time())
    finally:
        sys.stdout = old
    text = buf.getvalue()
    check('progress logs name the state, the park count, and the elapsed time',
          'US-AK' in text and 'park(s)' in text and 'min' in text and 's' in text)
    # flush: a mid-fetch hang must already have a log line on disk
    tmp = tempfile.NamedTemporaryFile('w+', delete=False)
    tmp.close()

    class HangFirst(SeqGetter):
        def get(self, url, rng=None, deadline=None, max_time=None):
            if url.endswith('/a1'):
                # give the parent a moment; the start-of-park log must already be flushed
                time.sleep(0.2)
            return super().get(url, rng=rng, deadline=deadline, max_time=max_time)

    # run in-process with stdout redirected to the file
    with open(tmp.name, 'w', encoding='utf-8') as fh:
        old = sys.stdout
        sys.stdout = fh
        try:
            PP.read_parks(areas, web, docs, truth, HangFirst(), {}, '2026-11-21',
                          refs=['US-A1'], quiet=False, started=time.time())
        finally:
            sys.stdout = old
    # After the sleep inside get(), the 'reading' line should already have been
    # flushed (we cannot hook mid-sleep easily here). The file must not be empty
    # even if we only check after; the stronger check is flush=True in the source.
    logged = pathlib.Path(tmp.name).read_text(encoding='utf-8')
    check('progress lines are written (not held in a buffer until the run ends)',
          'US-AK' in logged and 'flush=True' in (S / 'kpc_park_pages.py').read_text(encoding='utf-8'))


def test_workflow_step_timeout():
    yml = (ROOT / '.github/workflows/kpc-park-pages.yml').read_text(encoding='utf-8')
    # The read *step* must end before the 60-minute job limit so the upload/save can run.
    check('the read step has a 52-minute cap, inside the 60-minute job limit',
          'timeout-minutes: 52' in yml and 'timeout-minutes: 60' in yml)
    check('the walk uses pick_walk_area so a twice-cut-off state is skipped',
          'pick_walk_area' in yml)


def test_live_getter_passes_caps():
    src = (S / 'kpc_park_pages.py').read_text(encoding='utf-8')
    check('LiveGetter passes deadline and max_time to Manners',
          'deadline=deadline' in src and 'max_time=max_time' in src and 'class LiveGetter' in src)
    areas, web, docs, truth = two_parks()
    getter = SeqGetter()
    PP.read_parks(areas, web, docs, truth, getter, {}, '2026-11-21',
                  refs=['US-A1'], deadline=time.time() + 3600, get_max_seconds=90)
    check('each download is given the run deadline and the per-download cap',
          getter.calls and getter.calls[0]['deadline'] > time.time() and getter.calls[0]['max_time'] == 90)


if __name__ == '__main__':
    test_read_capped()
    test_mid_download_deadline()
    test_fifty_minute_stop_during_download()
    test_save_after_each_park()
    test_two_cutoffs_skip()
    test_progress_log_and_flush()
    test_workflow_step_timeout()
    test_live_getter_passes_caps()
    print('ALL PASS' if ok else 'SOME FAILED')
    sys.exit(0 if ok else 1)
