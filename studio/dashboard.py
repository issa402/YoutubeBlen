"""Generate an offline production desk; no model calls or background jobs."""
from html import escape
import json
from pathlib import Path
import shutil
from .dashboard_data import build_data


def build(studio):
    data = build_data(studio)
    source = Path(__file__).with_name('web')
    assets = studio.state / 'dashboard-assets'
    assets.mkdir(exist_ok=True)
    for name in ('app.js', 'style.css'):
        shutil.copyfile(source / name, assets / name)
    payload = json.dumps(data, ensure_ascii=True).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    fallback = ''.join(f'<p>{escape(e["title"])} · <a href="{escape(e["links"]["take"] or "#", quote=True)}">CREATOR_TAKE.md</a></p>' for e in data['episodes'])
    template = (source / 'index.html').read_text(encoding='utf-8')
    out = studio.state / 'dashboard.html'
    out.write_text(template.replace('<!--STUDIO_DATA-->', payload).replace('<!--FALLBACK-->', fallback), encoding='utf-8')
    return out
