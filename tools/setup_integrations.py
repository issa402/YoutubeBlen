"""Install reviewed upstream runtime dependencies in isolated local environments."""
import argparse
from pathlib import Path
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('target', choices=['hermes', 'vimax'])
    args = parser.parse_args()
    name = 'hermes-agent' if args.target == 'hermes' else 'ViMax'
    repo = ROOT / '.studio/repos' / name
    env = ROOT / '.studio/envs' / args.target
    python = env / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
    if not repo.is_dir():
        parser.error('Run tools/fetch_studio_repos.ps1 first.')
    if not python.exists():
        subprocess.run([sys.executable, '-m', 'venv', str(env)], check=True)
    lock = ROOT / 'integrations/studio' / f'{args.target}-requirements.lock.txt'
    if lock.is_file():
        requirements = ['-r', str(lock)]
        if args.target == 'hermes':
            requirements += ['-e', str(repo)]
    elif args.target == 'hermes':
        requirements = ['-e', str(repo)]
    else:
        # ViMax is a source application with no build backend: install its
        # declared runtime and run its documented source entry point.
        config = tomllib.loads((repo / 'pyproject.toml').read_text(encoding='utf-8'))
        requirements = config['project']['dependencies']
    subprocess.run([str(python), '-m', 'pip', 'install', *requirements], check=True)
    subprocess.run([str(python), '-m', 'pip', 'check'], check=True)


if __name__ == '__main__':
    main()
