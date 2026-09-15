"""Run with studio.ps1 or python -m studio."""
import argparse
import importlib.metadata
import json
from pathlib import Path
import shutil
import sys
from .core import Studio


def parser():
    p = argparse.ArgumentParser(description='Touchline: creator-led football production studio')
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    sub = p.add_subparsers(dest='command', required=True)
    for name in ('doctor', 'index', 'dashboard', 'learn', 'jobs', 'run-next'):
        sub.add_parser(name)
    n = sub.add_parser('new'); n.add_argument('episode'); n.add_argument('--title', required=True)
    take = n.add_mutually_exclusive_group(required=True)
    take.add_argument('--take'); take.add_argument('--take-file', type=Path)
    c = sub.add_parser('context'); c.add_argument('episode'); c.add_argument('--save', action='store_true')
    s = sub.add_parser('search'); s.add_argument('query')
    f = sub.add_parser('feedback'); f.add_argument('episode'); f.add_argument('note')
    f.add_argument('--kind', choices=['voice', 'visual', 'workflow'], default='voice')
    r = sub.add_parser('revoke'); r.add_argument('id')
    m = sub.add_parser('metrics'); m.add_argument('episode')
    for field in ('impressions', 'ctr', 'retention30', 'hours', 'cost'):
        m.add_argument('--' + field, type=float, required=True)
    for cmd in ('prepare', 'transcribe'):
        a = sub.add_parser(cmd); a.add_argument('input', type=Path); a.add_argument('--output', required=True)
        if cmd == 'transcribe':
            a.add_argument('--model', choices=['tiny', 'base', 'small'], default='tiny')
    for cmd in ('demo', 'render-package'):
        a = sub.add_parser(cmd); a.add_argument('--output', required=True)
        if cmd == 'render-package':
            a.add_argument('--seconds', type=int, default=8)
    i = sub.add_parser('intake'); i.add_argument('url'); i.add_argument('--output', required=True)
    i.add_argument('--download', action='store_true', help='Also download media you are authorized to obtain.')
    s = sub.add_parser('source'); s.add_argument('episode'); s.add_argument('--url', required=True)
    s.add_argument('--title', required=True)
    for field in ('author', 'published', 'event-date', 'quote', 'archive', 'notes'):
        s.add_argument('--' + field, default='')
    q = sub.add_parser('enqueue'); q.add_argument('action', choices=['index', 'dashboard', 'prepare', 'render-package'])
    q.add_argument('--args', default='{}', help='JSON object; no shell commands.')
    retry = sub.add_parser('retry'); retry.add_argument('id')
    ep = sub.add_parser('episode-package'); ep.add_argument('episode'); ep.add_argument('--output', required=True)
    assembly = sub.add_parser('assemble'); assembly.add_argument('frames', type=Path)
    assembly.add_argument('--output', required=True); assembly.add_argument('--audio', type=Path)
    assembly.add_argument('--fps', type=int, default=24)
    h = sub.add_parser('hermes-prompt'); h.add_argument('episode')
    task = h.add_mutually_exclusive_group(required=True)
    task.add_argument('--task'); task.add_argument('--task-file', type=Path)
    h.add_argument('--max-chars', type=int, default=12000)
    voice = sub.add_parser('voice-guide'); voice.add_argument('episode'); voice.add_argument('--output', required=True)
    voice.add_argument('--opening', action='store_true'); voice.add_argument('--rate', type=int, default=0)
    voice.add_argument('--voice', default='Microsoft David Desktop')
    mux = sub.add_parser('mux-guide'); mux.add_argument('video', type=Path); mux.add_argument('audio', type=Path)
    mux.add_argument('--output', required=True)
    review = sub.add_parser('review'); review.add_argument('episode')
    review.add_argument('--output', help='Optional fresh .studio/ folder for Markdown, JSON and edit CSV.')
    caption = sub.add_parser('align-captions'); caption.add_argument('audio', type=Path)
    caption.add_argument('--text', type=Path, required=True); caption.add_argument('--output', required=True)
    caption.add_argument('--model', choices=['tiny', 'base', 'small'], default='tiny')
    finishing = sub.add_parser('finish-opening'); finishing.add_argument('video', type=Path)
    for field in ('audio', 'alignment', 'text'):
        finishing.add_argument('--' + field, type=Path, required=True)
    finishing.add_argument('--output', required=True)
    return p


def doctor(studio):
    packages = {}
    for name in ('yt-dlp', 'imageio-ffmpeg', 'opencv-python-headless', 'faster-whisper'):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = 'MISSING: run tools/setup_studio.ps1'
    from .media import ffmpeg
    try:
        binary = ffmpeg()
    except ImportError:
        binary = 'MISSING'
    repo_names = ('hermes-agent', 'ViMax', 'Understand-Anything', 'last30days-skill')
    repos = {name: 'source downloaded' if (studio.state / 'repos' / name).is_dir() else 'not downloaded' for name in repo_names}
    return {'python': sys.version.split()[0], 'packages': packages, 'ffmpeg': binary,
            'blender': shutil.which('blender') or next((str(p) for p in (studio.state / 'bin').rglob('blender.exe')), 'not installed'),
            'repos': repos, 'learning': 'explicit feedback retrieval; no model retraining',
            'providers': 'Provider login/API configuration required for unattended AI generation; no paid job launched.'}


def execute(s, a):
    cmd = a.command
    if cmd == 'doctor': return doctor(s)
    if cmd == 'new': return s.new(a.episode, a.title, a.take if a.take is not None else a.take_file.read_text(encoding='utf-8-sig'))
    if cmd == 'context':
        content = s.context(a.episode)
        if a.save:
            out = s.state / 'handoffs' / (a.episode + '.md')
            out.parent.mkdir(exist_ok=True)
            out.write_text(content, encoding='utf-8')
            return {'path': str(out)}
        return content
    if cmd == 'index': return s.index()
    if cmd == 'search': return s.search(a.query)
    if cmd == 'dashboard': return {'path': str(s.dashboard())}
    if cmd == 'feedback': return s.feedback(a.episode, a.note, a.kind)
    if cmd == 'learn': return s.feedback_records()
    if cmd == 'revoke': return s.revoke(a.id)
    if cmd == 'metrics':
        return s.metrics(a.episode, **{k: getattr(a, k) for k in ('impressions', 'ctr', 'retention30', 'hours', 'cost')})
    if cmd in ('prepare', 'transcribe', 'demo'):
        from . import media
        output = s.output(a.output)
        if cmd == 'demo': return media.demo(output)
        if cmd == 'prepare': return media.prepare(a.input, output)
        return media.transcribe(a.input, output, model=a.model)
    if cmd == 'render-package':
        from .render import create_package
        return create_package(s.output(a.output), seconds=a.seconds)
    if cmd == 'source':
        from .sources import add_source
        return add_source(s, a.episode, **{k: getattr(a, k) for k in ('url', 'title', 'author', 'published', 'event_date', 'quote', 'archive', 'notes')})
    if cmd == 'intake':
        from .sources import intake
        return intake(a.url, s.output(a.output), download=a.download)
    if cmd == 'enqueue':
        args = json.loads(a.args)
        if not isinstance(args, dict): raise ValueError('--args must be a JSON object.')
        return s.enqueue(a.action, args)
    if cmd == 'jobs': return s.jobs()
    if cmd == 'retry': return s.retry(a.id)
    if cmd == 'episode-package':
        from .episode import package
        return package(s, a.episode, s.output(a.output))
    if cmd == 'assemble':
        from .episode import assemble
        return assemble(a.frames, s.output(a.output), audio=a.audio, fps=a.fps)
    if cmd == 'hermes-prompt':
        from .hermes import prepare_prompt
        text = a.task if a.task is not None else a.task_file.read_text(encoding='utf-8-sig')
        return prepare_prompt(s, a.episode, text, max_chars=a.max_chars)
    if cmd == 'voice-guide':
        from .narration import create_guide
        return create_guide(s, a.episode, s.output(a.output), opening=a.opening, rate=a.rate, voice=a.voice)
    if cmd == 'mux-guide':
        from .narration import mux_guide
        return mux_guide(a.video, a.audio, s.output(a.output))
    if cmd == 'review':
        from .review import review_episode, export_review
        return export_review(s, a.episode, s.output(a.output)) if a.output else review_episode(s, a.episode)
    if cmd == 'align-captions':
        from .captions import align
        return align(a.audio, a.text, s.output(a.output), model=a.model)
    if cmd == 'finish-opening':
        from .finish import finish
        return finish(a.video, a.audio, a.alignment, a.text, s.output(a.output))
    return s.run_next()


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        result = execute(Studio(args.root), args)
        status = 'error' if isinstance(result, dict) and result.get('status') == 'error' else 'success'
        print(json.dumps({'status': status, 'command': args.command, 'result': result}, indent=2, ensure_ascii=False, default=str))
        return 1 if status == 'error' else 0
    except Exception as exc:
        print(json.dumps({'status': 'error', 'command': args.command, 'summary': str(exc),
                          'next_actions': ['Correct the input or run doctor. Existing artifacts are preserved; use a fresh output folder for retries.']}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
