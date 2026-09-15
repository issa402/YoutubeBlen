"""Finish the 30-second opening at source resolution with matching voice/captions."""
import hashlib
import json
import math
from pathlib import Path
import subprocess
import textwrap
import wave

from .media import ffmpeg

FPS, FRAMES, DURATION = 24, 720, 30


def _sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def _finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def validate_alignment(data, audio, script):
    """Fail on stale subtitles or truncated speech before creating an output."""
    if not isinstance(data, dict):
        raise ValueError('Alignment must be a JSON object.')
    if data.get('status') != 'aligned' or data.get('full_spoken_word_coverage') is not True:
        raise ValueError('Alignment must have succeeded and cover every supplied script word.')
    for field, path in (('source_audio_sha256', audio), ('source_text_sha256', script)):
        if data.get(field) != _sha(path):
            raise ValueError(f'Alignment fingerprint differs: {field}. Align this exact audio and text again.')
    with wave.open(str(audio), 'rb') as wav:
        duration = wav.getnframes() / wav.getframerate()
    if not 0 < duration <= DURATION:
        raise ValueError('Narration must fit the 30-second opening; speech is never truncated.')
    measured = data.get('duration_seconds')
    if not _finite(measured) or abs(measured - duration) > .025:
        raise ValueError('Alignment duration differs from the measured WAV.')
    ratios = [data.get('asr_match_ratio'), data.get('asr_precision')]
    if any(not _finite(ratio) or not .8 <= ratio <= 1 for ratio in ratios):
        raise ValueError('Caption ASR coverage must be at least 80%.')
    cues = data.get('cues')
    if not isinstance(cues, list) or not cues:
        raise ValueError('Alignment needs timed captions.')
    previous = 0
    for cue in cues:
        if not isinstance(cue, dict):
            raise ValueError('Each caption must be an object.')
        start, end, text = cue.get('start'), cue.get('end'), cue.get('text')
        if not _finite(start) or not _finite(end) or not previous <= start < end <= duration + .001:
            raise ValueError('Caption times overlap or fall outside the measured speech.')
        if not isinstance(text, str) or not text.strip():
            raise ValueError('Every caption needs its spoken text.')
        previous = end
    expected = Path(script).read_text(encoding='utf-8-sig').split()
    if ' '.join(cue['text'] for cue in cues).split() != expected:
        raise ValueError('Captions do not preserve the exact narration.')
    return duration


def _time(seconds):
    ticks = round(seconds * 100)
    return f'{ticks // 360000}:{ticks // 6000 % 60:02}:{ticks // 100 % 60:02}.{ticks % 100:02}'


def _literal(text):
    return text.translate(str.maketrans({'{': '｛', '}': '｝', '\\': '＼', '\n': ' ', '\r': ' '}))


def build_ass(alignment, width, height):
    """Small chapter labels and legible, source-timed captions on full-bleed 3D."""
    scale = height / 1080
    font, small = round(46 * scale), round(24 * scale)
    margin, bottom = round(64 * scale), round(height - 74 * scale)
    header = f'''[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Brand,Segoe UI,{small},&H00DDD8D2,&H000000FF,&H001B1009,&H80000000,0,0,0,0,100,100,1,0,1,1,1,7,0,0,0,1
Style: Caption,Segoe UI,{font},&H00F8F6F3,&H000000FF,&H00150C06,&H80000000,-1,0,0,0,100,100,0,0,1,2,1,2,{margin},{margin},0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    events = []

    def add(start, end, style, tags, text):
        events.append(f'Dialogue: 0,{_time(start)},{_time(end)},{style},,0,0,0,,{tags}{text}')

    add(0, DURATION, 'Brand', f'{{\\an7\\pos({margin},{round(34*scale)})}}', 'TOUCHLINE / FOOTBALL ESSAYS')
    for start, end, title in ((0, 356/FPS, '01 / THE RIVAL'),
                              (356/FPS, 571/FPS, '02 / THE WHOLE PACKAGE'),
                              (571/FPS, DURATION, '03 / YOUR VICTORY?')):
        add(start, end, 'Brand', f'{{\\an9\\pos({width-margin},{round(34*scale)})}}', title)
    for cue in alignment['cues']:
        lines = textwrap.wrap(_literal(cue['text']), width=46, break_long_words=False, break_on_hyphens=False)
        if len(lines) > 2 or any(len(line) > 46 for line in lines):
            raise ValueError('Caption is too long for two readable lines; shorten the cue grouping.')
        add(cue['start'], cue['end'], 'Caption', f'{{\\pos({width//2},{bottom})}}', r'\N'.join(lines))
    return header + '\n'.join(events) + '\n'


def _run(command, **kwargs):
    result = subprocess.run(command, capture_output=True, timeout=1800, shell=False, **kwargs)
    if result.returncode:
        raise RuntimeError(result.stderr.decode('utf-8', errors='replace')[-4000:])
    return result


def inspect_picture(path, samples=None):
    import cv2
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    size = [int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))]
    count = 0
    try:
        while cap.isOpened():
            valid, frame = cap.read()
            if not valid:
                break
            count += 1
            if samples and count in (1, 178, 356, 357, 464, 571, 572, 646, 720):
                target = Path(samples) / f'frame-{count:04}.png'
                if not cv2.imwrite(str(target), frame):
                    raise RuntimeError(f'Could not save preview: {target}')
                if count == 464:
                    cv2.imwrite(str(Path(samples) / 'poster.png'), frame)
    finally:
        cap.release()
    if count != FRAMES or not math.isfinite(fps) or abs(fps - FPS) > .001:
        raise ValueError(f'Opening requires 720 decoded frames at 24 fps; found {count} at {fps}.')
    if size not in ([1280, 720], [1920, 1080]):
        raise ValueError(f'Opening requires an HD source at 1280x720 or 1920x1080; found {size}.')
    return {'decoded_frames': count, 'fps': fps, 'duration_seconds': count/fps, 'resolution': size}


def finish(video, audio, alignment, script, output):
    video, audio, alignment, script, output = [Path(p).resolve() for p in (video, audio, alignment, script, output)]
    if output.exists():
        raise FileExistsError(f'Use a fresh output folder: {output}')
    data = json.loads(alignment.read_text(encoding='utf-8-sig'))
    duration = validate_alignment(data, audio, script)
    picture = inspect_picture(video)
    ass = build_ass(data, *picture['resolution'])
    output.mkdir(parents=True, exist_ok=False)
    (output / 'overlay.ass').write_text(ass, encoding='utf-8')
    command = [ffmpeg(), '-hide_banner', '-nostdin', '-n', '-i', str(video), '-i', str(audio),
               '-map', '0:v:0', '-map', '1:a:0', '-vf', 'ass=overlay.ass',
               '-af', f'apad=whole_dur={DURATION}', '-t', str(DURATION),
               '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-threads', '2',
               '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart',
               '-metadata', 'comment=Original Blender animation; stock synthetic voice; ASR-estimated caption timing', 'video.mp4']
    result = _run(command, cwd=output)
    (output / 'ffmpeg.log').write_bytes(result.stderr)
    final = output / 'video.mp4'
    checked = inspect_picture(final, output)
    pcm = _run([ffmpeg(), '-v', 'error', '-i', str(final), '-map', '0:a:0',
                '-ac', '1', '-ar', '24000', '-f', 's16le', '-']).stdout
    decoded_seconds = len(pcm) / 48000
    if checked != picture or not DURATION - .01 <= decoded_seconds <= DURATION + .1:
        raise ValueError('Finished picture or audio duration differs from the expected opening.')
    report = {'valid': True, 'video': str(final), 'poster': str(output / 'poster.png'),
              'picture': checked, 'source_picture': picture, 'picture_resized': False,
              'source_video_sha256': _sha(video), 'source_audio_sha256': _sha(audio),
              'source_text_sha256': _sha(script), 'alignment_sha256': _sha(alignment),
              'source_audio_seconds': duration, 'speech_truncated': False,
              'audio': {'decoded_seconds': decoded_seconds, 'codec': 'AAC', 'reencoded': True},
              'caption_timing': 'ASR word anchors with marked interpolation; estimated, not manually verified.',
              'caption_asr_match_ratio': data['asr_match_ratio'], 'synthetic_voice': True}
    (output / 'validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report
