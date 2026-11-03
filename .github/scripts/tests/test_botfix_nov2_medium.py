"""Nov 2 review fixes (MEDIUM): key ids, stale 2-fer alerts, grade queue. Run: python3 .github/scripts/tests/test_botfix_nov2_medium.py"""
import gzip, hashlib, importlib, json, os, pathlib, subprocess, sys, tempfile, unittest

S = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(S))


def w(p, d):
    p = pathlib.Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(d if isinstance(d, str) else json.dumps(d))


class KeyId(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.mkdtemp()
        w(f'{self.t}/data/us-key/index.json', {'states': {'AK': {'parks': 3, 'seconds': 10}}})
        w(f'{self.t}/data/us-key/US-AK.json', {'st': 'AK', 'parks': {'K-1': {'m': 1}}})
        w(f'{self.t}/data/ca-key/index.json', {'provinces': {'AB': {'parks': 1}}})
        import kpc_key_id; self.K = kpc_key_id

    def test_time_stamps_do_not_change_the_id(self):
        a = self.K.one(self.t, 'us-key')
        w(f'{self.t}/data/us-key/index.json', {'states': {'AK': {'parks': 3, 'seconds': 99}}, 'build': 'US-1', 'made': '2026-11-02'})
        self.assertEqual(a, self.K.one(self.t, 'us-key'))

    def test_real_change_changes_the_id(self):
        a = self.K.one(self.t, 'us-key')
        w(f'{self.t}/data/us-key/US-AK.json', {'st': 'AK', 'parks': {'K-1': {'m': 0}}})
        self.assertNotEqual(a, self.K.one(self.t, 'us-key'))

    def test_canada_change_leaves_the_us_id_alone(self):
        a, all_a = self.K.one(self.t, 'us-key'), self.K.all_keys(self.t)
        w(f'{self.t}/data/ca-key/CA-AB.json', {'parks': {'CA-1': {}}})
        self.assertEqual(a, self.K.one(self.t, 'us-key'))
        self.assertNotEqual(all_a, self.K.all_keys(self.t))


class FersAlerts(unittest.TestCase):
    def test_stale_area_is_left_out(self):
        t = tempfile.mkdtemp(); cwd = os.getcwd(); os.chdir(t)
        try:
            raw_ok = b'{"spots": []}'
            w('data/fers/US-AA.json', raw_ok.decode())
            with gzip.open('data/fers/US-BB.json.gz', 'wb') as fh: fh.write(b'{"spots": [1]}')
            rows = {'x': {'verdict': 'GONE'}, 'y': {'verdict': 'SHRUNK'}}
            w('data/fers-check/US-AA.json', {'area': 'US-AA', 'fers_file': 'data/fers/US-AA.json', 'fers_sha256': hashlib.sha256(raw_ok).hexdigest(), 'started': '2026-11-01T11:14:06Z', 'rows': rows})
            w('data/fers-check/US-BB.json', {'area': 'US-BB', 'fers_file': 'data/fers/US-BB.json.gz', 'fers_sha256': 'old', 'started': '2026-11-01T11:14:06Z', 'rows': rows})
            out = subprocess.run([sys.executable, str(S / 'kpc_tools_run.py'), 'fers-alerts'], capture_output=True, text=True).stdout
            md = pathlib.Path('data/fers-check/alerts.md').read_text()
            self.assertIn('ALERTS=2', out)
            self.assertIn('**US-AA** (checked 2026-11-01 5:14 AM CST)', md)
            self.assertIn('## Stale', md); self.assertIn('- US-BB', md)
        finally: os.chdir(cwd)


class GradeQueue(unittest.TestCase):
    def test_queue(self):
        t = tempfile.mkdtemp(); os.environ['DATA'] = t
        w(f'{t}/data/us-key/index.json', {'states': {'AK': {'parks': 1}}})
        w(f'{t}/data/waiting/in/data/us-key/index.json', {'states': {'AK': {'parks': 2}}, 'build': 'US-9'})
        w(f'{t}/data/us-key/layers.json', {'a': 1})
        w(f'{t}/data/waiting/in/data/us-key/layers.json', {'a': 2})
        w(f'{t}/data/waiting/in/data/fers/US-AA.json', {'spots': []})
        w(f'{t}/data/waiting/in/data/fers/US-KY.json', {'spots': []})
        w(f'{t}/data/status/fers-ready.json', {'areas': {'US-AA': {'status': 'waiting for audit'}, 'US-KY': {'status': 'waiting for key', 'fers_started': '2026-11-01'}}})
        import kpc_waiting_room as K; K = importlib.reload(K)
        K.grade_queue([{'path': p, 'kind': k, 'verdict': 'PASS'} for p, k in (('data/us-key/index.json', 'key'), ('data/us-key/layers.json', 'key'),
                                                                               ('data/fers/US-AA.json', 'fers'), ('data/fers/US-KY.json', 'fers'))])
        md = pathlib.Path(f'{t}/data/status/grade-queue.md').read_text()
        self.assertIn('**data/us-key/index.json** (key, PASS; grader chat 11 (+ chat 2 G-4); held build US-9): 0 new, 1 changed', md)
        self.assertIn('**data/us-key/layers.json**', md); self.assertIn('whole file changed, no rows to list', md)
        self.assertIn('**data/fers/US-KY.json**', md)
        self.assertNotIn('**data/fers/US-AA.json**', md)
        self.assertIn('## Paused, not for grading (1 2-fer file(s)', md)


if __name__ == '__main__':
    unittest.main(verbosity=2)
