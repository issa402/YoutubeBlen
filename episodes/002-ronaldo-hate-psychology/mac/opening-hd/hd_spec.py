"""Blender-independent HD render integrity and resume checks (standard library)."""
import hashlib
import json
import re
import struct
import zlib


def render_fingerprint(sources, manifest):
    digest = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode())
    for source in sources:
        digest.update(source.name.encode())
        digest.update(source.read_bytes())
    return digest.hexdigest()


def validate_png(path, resolution):
    raw = path.read_bytes()
    if raw[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError(f'Invalid PNG header: {path.name}')
    pos, compressed, dimensions, ended = 8, [], None, False
    while pos + 12 <= len(raw):
        size = struct.unpack('>I', raw[pos:pos + 4])[0]
        tag = raw[pos + 4:pos + 8]
        data = raw[pos + 8:pos + 8 + size]
        crc = raw[pos + 8 + size:pos + 12 + size]
        if len(crc) != 4 or zlib.crc32(tag + data) != struct.unpack('>I', crc)[0]:
            raise ValueError(f'Invalid PNG chunk: {path.name}')
        if tag == b'IHDR':
            dimensions = list(struct.unpack('>II', data[:8]))
            if data[8:] != bytes([8, 2, 0, 0, 0]):
                raise ValueError('Expected non-interlaced RGB 8-bit PNG')
        elif tag == b'IDAT':
            compressed.append(data)
        elif tag == b'IEND':
            ended = True
            break
        pos += size + 12
    if not ended or dimensions != list(resolution):
        raise ValueError(f'PNG dimensions or completion mismatch: {path.name}')
    try:
        decoded = zlib.decompress(b''.join(compressed))
    except zlib.error as exc:
        raise ValueError(f'Invalid PNG compressed pixels: {path.name}') from exc
    width, height = dimensions
    if len(decoded) != (width * 3 + 1) * height:
        raise ValueError(f'Incomplete PNG pixels: {path.name}')
    return dimensions


def remaining_frames(folder, ledger, fingerprint, resolution, resume, end=720):
    files = sorted(folder.glob('frame_*.png')) if folder.exists() else []
    if files and not resume:
        raise FileExistsError('Frames already exist; use --resume to verify and continue')
    if not resume:
        if ledger.exists():
            raise FileExistsError('Render state already exists; use --resume or a fresh packet')
        return list(range(1, end + 1))
    if not ledger.exists():
        raise ValueError('Resume requires a render-state.json from the same source')
    state = json.loads(ledger.read_text(encoding='utf-8'))
    if state.get('fingerprint') != fingerprint:
        raise ValueError('Scene source or render configuration changed; use a fresh packet')
    completed = state.get('completed')
    if not isinstance(completed, list) or any(type(f) is not int or not 1 <= f <= end for f in completed):
        raise ValueError('Invalid render completion ledger')
    actual = []
    for file in files:
        match = re.fullmatch(r'frame_(\d{4})\.png', file.name)
        if not match:
            raise ValueError('Unexpected frame filename')
        actual.append(int(match.group(1)))
        validate_png(file, resolution)
    if len(set(completed)) != len(completed) or sorted(completed) != sorted(actual):
        raise ValueError('Rendered files disagree with the completion ledger; preserve and inspect them')
    return [frame for frame in range(1, end + 1) if frame not in set(completed)]
