# Copyright (c) 2026 Soufiane Lemqari. MIT.
import argparse
import json
import platform
import resource
import shutil
import sys
import time
from pathlib import Path
from . import __version__
from .core import BUNDLE, audit, compare, digest, evaluate, hypothesis, load_csv, read, write


def inventory(root):
    return {str(p.relative_to(root)): digest(p) for p in sorted(root.rglob('*')) if p.is_file() and p.name != 'manifest.json'}


def code_hashes():
    return {p.name: digest(p) for p in sorted(Path(__file__).parent.glob('*.py'))}


def verify_run(root):
    root = Path(root)
    if any(p.is_symlink() for p in root.rglob('*')):
        raise ValueError('Liens symboliques interdits')
    manifest = read(root/'manifest.json')
    if inventory(root) != manifest['files'] or code_hashes() != manifest['code']:
        raise ValueError('Snapshot/code altere')
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description='PAH/GroEL-ES: demonstration de recherche bornee')
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('ingest', 'audit', 'evaluate'):
        p = sub.add_parser(name)
        p.add_argument('--bundle', type=Path, default=BUNDLE)
        p.add_argument('--out', type=Path, required=True)
    p = sub.add_parser('compare'); p.add_argument('--run', type=Path, required=True); p.add_argument('--out', type=Path, required=True)
    p = sub.add_parser('export'); p.add_argument('--run', type=Path, required=True); p.add_argument('--out', type=Path, required=True)
    p = sub.add_parser('restore'); p.add_argument('--run', type=Path, required=True); p.add_argument('--out', type=Path, required=True)
    a = parser.parse_args(argv)
    start = time.perf_counter(); cpu = time.process_time()
    try:
        if a.out.exists():
            raise ValueError('Destination existante: refus ecrasement')
        if a.command in ('audit', 'ingest', 'evaluate'):
            admission = audit(a.bundle)
            if a.command == 'audit':
                write(a.out, admission)
            elif admission['status'] == 'rejected':
                a.out.mkdir(parents=True)
                write(a.out/'admission.json', admission)
            elif a.command == 'ingest':
                shutil.copytree(a.bundle, a.out)
                write(a.out/'admission.json', admission)
            else:
                a.out.mkdir(parents=True)
                shutil.copytree(a.bundle, a.out/'inputs')
                write(a.out/'admission.json', admission)
                report = evaluate(load_csv(a.bundle/'data/activity_pairs.csv'), read(a.bundle/'configs/study.json'))
                write(a.out/'report.json', report)
                write(a.out/'comparison.json', compare(report, read(BUNDLE/'reference/pilot.json')))
                write(a.out/'runtime.json', {'python': platform.python_version(), 'platform': platform.platform(),
                    'package_version': __version__, 'wall_seconds': time.perf_counter()-start,
                    'cpu_seconds': time.process_time()-cpu,
                    'peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform == 'darwin' else 1024),
                    'cost_total': None, 'external_paid_compute': 'not_requested', 'gpu': 'not_used'})
                write(a.out/'manifest.json', {'files': inventory(a.out), 'code': code_hashes(), 'version': __version__})
            if admission['status'] == 'rejected':
                print(json.dumps(admission, ensure_ascii=False)); return 2
            result = {'status': 'ok', 'command': a.command, 'observations': 14, 'variants': 7}
        else:
            verify_run(a.run)
            if a.command == 'restore':
                shutil.copytree(a.run, a.out)
                verify_run(a.out)
                regenerated = evaluate(load_csv(a.out/'inputs/data/activity_pairs.csv'), read(a.out/'inputs/configs/study.json'))
                if regenerated != read(a.out/'report.json'):
                    raise ValueError('Reexecution divergente')
                result = {'status': 'ok', 'command': 'restore', 'report_identical': True}
            elif a.command == 'compare':
                result = compare(read(a.run/'report.json'), read(BUNDLE/'reference/pilot.json')); write(a.out, result)
            else:
                result = hypothesis(read(a.run/'report.json')); write(a.out, result)
        print(json.dumps(result, ensure_ascii=False, indent=2)); return 0
    except (ValueError, OSError, KeyError, TypeError) as e:
        print(json.dumps({'status': 'rejected', 'reason': str(e)}, ensure_ascii=False), file=sys.stderr)
        return 2

if __name__ == '__main__':
    sys.exit(main())
