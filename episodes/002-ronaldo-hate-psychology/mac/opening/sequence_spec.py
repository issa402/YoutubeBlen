"""Portable, Blender-independent contract for the 30-second opening."""
import json
from pathlib import Path

SHOTS = (('notification', 1, 356), ('status', 357, 571), ('rivalry', 572, 720))


def shot_at(frame):
    if type(frame) is not int or not 1 <= frame <= 720:
        raise ValueError('Frame must be an integer from 1 through 720')
    return next(name for name, start, end in SHOTS if start <= frame <= end)


def safe_output(root, relative):
    path = Path(relative)
    if path.is_absolute() or '..' in path.parts or '\\' in relative or ':' in relative:
        raise ValueError('Output must be a portable relative path inside the packet')
    result = (root / path).resolve()
    if result == root or not result.is_relative_to(root):
        raise ValueError('Output must stay inside the packet')
    return result


def load_manifest(path):
    manifest = json.loads(path.read_text(encoding='utf-8'))
    for key, expected in [('schema_version', 1), ('fps', 24), ('frame_start', 1), ('frame_end', 720)]:
        if type(manifest.get(key)) is not int or manifest[key] != expected:
            raise ValueError(f'{key} must be {expected}')
    for key in ('resolution', 'preview_resolution'):
        dimensions = manifest.get(key)
        if not isinstance(dimensions, list) or len(dimensions) != 2 or any(
                type(value) is not int or not 64 <= value <= 3840 for value in dimensions):
            raise ValueError(f'Invalid {key}')
    if not isinstance(manifest.get('output'), str):
        raise ValueError('output must be a string')
    safe_output(path.parent.resolve(), manifest['output'])
    return manifest
