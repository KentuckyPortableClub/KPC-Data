"""Nov 9 2026 weekly batch: kpc_push_retry.sh (tools-out / board push fetch-and-retry). Local bare repos only, no network."""
import json, os, pathlib, subprocess, tempfile

S = pathlib.Path(__file__).resolve().parents[1] / '.github/scripts/kpc_push_retry.sh'
ENV = dict(os.environ, GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@t', GIT_COMMITTER_NAME='t', GIT_COMMITTER_EMAIL='t@t')


def sh(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, env=ENV)


def setup(tmp, branch):
    sh(f'git init -q --bare -b {branch} origin.git', tmp)
    sh(f'git clone -q origin.git a && cd a && git checkout -q -b {branch} 2>/dev/null; mkdir -p picture-trace data/status/bots && '
       'echo "v0" > picture-trace/report.csv && echo "{}" > data/status/board.json && echo keep > other.txt && '
       f'git add -A && git commit -qm base && git push -q origin HEAD:{branch}', tmp)
    sh(f'git clone -q -b {branch} origin.git b', tmp)


def test_generated_output_conflict_is_settled_and_pushed():
    with tempfile.TemporaryDirectory() as t:
        setup(t, 'tools-out')
        b = os.path.join(t, 'b'); a = os.path.join(t, 'a')
        sh('echo other-run > picture-trace/report.csv && git commit -qam other && git push -q origin HEAD:tools-out', b)
        sh('echo this-run > picture-trace/report.csv && git commit -qam this', a)
        r = sh(f'bash {S} tools-out 3 "picture-trace"', a)
        assert r.returncode == 0, r.stdout + r.stderr
        sh('git fetch -q && git reset -q --hard origin/tools-out', b)
        assert open(os.path.join(b, 'picture-trace/report.csv')).read().strip() == 'this-run'


def test_board_conflict_is_rewritten_on_top_of_newest():
    with tempfile.TemporaryDirectory() as t:
        setup(t, 'main')
        a = os.path.join(t, 'a'); b = os.path.join(t, 'b')
        sh('echo \'{"other": 1}\' > data/status/board.json && git commit -qam other && git push -q origin HEAD:main', b)
        sh('echo \'{"mine": 1}\' > data/status/board.json && git commit -qam mine', a)
        redo = os.path.join(t, 'redo.py')
        open(redo, 'w').write("import json\nd = json.load(open('data/status/board.json'))\nd['mine'] = 1\n"
                              "json.dump(d, open('data/status/board.json', 'w'))\n")
        r = sh(f'bash {S} main 3 "" "python3 {redo}"', a)
        assert r.returncode == 0, r.stdout + r.stderr
        sh('git fetch -q && git reset -q --hard origin/main', b)
        assert json.load(open(os.path.join(b, 'data/status/board.json'))) == {'other': 1, 'mine': 1}


def test_conflict_outside_own_files_is_aborted_not_forced():
    with tempfile.TemporaryDirectory() as t:
        setup(t, 'tools-out')
        a = os.path.join(t, 'a'); b = os.path.join(t, 'b')
        sh('echo theirs > other.txt && git commit -qam o && git push -q origin HEAD:tools-out', b)
        sh('echo mine > other.txt && git commit -qam m', a)
        r = sh(f'bash {S} tools-out 2 "picture-trace"', a)
        assert r.returncode == 1 and '::error' in r.stdout
        assert not os.path.isdir(os.path.join(a, '.git/rebase-merge'))      # nothing left half done
        sh('git fetch -q && git reset -q --hard origin/tools-out', b)
        assert open(os.path.join(b, 'other.txt')).read().strip() == 'theirs'  # never forced


if __name__ == '__main__':
    for n, f in list(globals().items()):
        if n.startswith('test_'): f(); print('ok', n)
