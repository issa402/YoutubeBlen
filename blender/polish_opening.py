"""Frame and caption an existing opening without rerendering or changing its voice.

Run with the project's Python, not inside Blender. Source footage is always kept
whole. The 720p export upscales a 360p proof; it is not a new HD Blender render.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess

import cv2
import imageio_ffmpeg

FPS = 24
FRAMES = 720
DURATION = FRAMES / FPS
PICTURE = (96, 42, 1088, 612)
CHAPTERS = ((0, 356 / FPS, '01 / THE RIVAL'),
            (356 / FPS, 571 / FPS, '02 / THE WHOLE PACKAGE'),
            (571 / FPS, DURATION, '03 / YOUR VICTORY?'))


def validate_timeline(timeline):
    """Reject gaps in the contract rather than inventing missing spoken text."""
    segments = timeline.get('segments')
    duration = timeline.get('duration_seconds')
    if not isinstance(duration, (int, float)) or not math.isfinite(duration) or not 0 < duration <= DURATION:
        raise ValueError('Narration duration must be finite and within the 30-second picture.')
    if not isinstance(segments, list) or not segments:
        raise ValueError('Timeline requires measured paragraphs.')
    previous = 0.0
    for segment in segments:
        start, end = segment.get('start_seconds'), segment.get('end_seconds')
        if any(not isinstance(n, (int, float)) or not math.isfinite(n) for n in (start, end)):
            raise ValueError('Paragraph timestamps must be finite numbers.')
        if not previous <= start < end <= duration:
            raise ValueError('Paragraphs overlap or fall outside the narration.')
        if not isinstance(segment.get('text'), str) or not segment['text'].strip():
            raise ValueError('Every paragraph needs its actual spoken text.')
        previous = end
    if abs(previous - duration) > .001:
        raise ValueError('Last paragraph must end at the measured narration duration.')
    return timeline


def caption_cues(timeline):
    """Split actual text into readable phrases with explicit approximate timing."""
    validate_timeline(timeline)
    cues = []
    for paragraph in timeline['segments']:
        words = paragraph['text'].split()
        phrases, current = [], []
        for word in words:
            current = [*current, word]
            if len(current) >= 7 or re.search(r'[.!?:]$', word):
                phrases = [*phrases, ' '.join(current)]
                current = []
        if current:
            phrases = [*phrases, ' '.join(current)]
        weights = [sum(max(2, len(w)) for w in phrase.split()) for phrase in phrases]
        duration = paragraph['end_seconds'] - paragraph['start_seconds']
        offset = paragraph['start_seconds']
        for index, (phrase, weight) in enumerate(zip(phrases, weights)):
            end = (paragraph['end_seconds'] if index == len(phrases)-1 else
                   offset + duration * weight / sum(weights))
            cues = [*cues, {'start': offset, 'end': end, 'text': phrase,
                           'timing': 'approximate within measured paragraph'}]
            offset = end
    return cues


def _time(seconds):
    ticks = round(seconds * 100)
    return f'{ticks // 360000}:{ticks // 6000 % 60:02}:{ticks // 100 % 60:02}.{ticks % 100:02}'


def _literal(text):
    # Full-width braces/backslash stay visible and cannot become ASS overrides.
    return text.translate(str.maketrans({'{': '｛', '}': '｝', '\\': '＼', '\n': ' ', '\r': ' '}))


def build_ass(timeline):
    events = []

    def add(start, end, style, position, text):
        events.append(f'Dialogue: 0,{_time(start)},{_time(end)},{style},,0,0,0,,{position}{_literal(text)}')

    voice = 'SYNTHETIC GUIDE' if timeline.get('synthetic_guide') else 'FOOTBALL ESSAYS'
    add(0, DURATION, 'Brand', r'{\an7\pos(96,15)}', f'TOUCHLINE / {voice}')
    for start, end, title in CHAPTERS:
        add(start, end, 'Chapter', r'{\an9\pos(1184,15)\fad(140,100)}', title)
    for cue in caption_cues(timeline):
        add(cue['start'], cue['end'], 'Caption', r'{\an5\pos(640,683)\fad(70,50)}', cue['text'])
    header = '''[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Brand,Segoe UI,16,&H00C2B8AB,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,0,0,7,0,0,0,1
Style: Chapter,Segoe UI,16,&H00E6D1AB,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,1,0,1,0,0,9,0,0,0,1
Style: Caption,Segoe UI,29,&H00F6F3EF,&H000000FF,&H001A0F07,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    return header + '\n'.join(events) + '\n'


def _run(args, **kwargs):
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
    if result.returncode:
        raise RuntimeError(result.stderr.decode('utf-8', errors='replace')[-4000:])
    return result


def _audio_signature(path):
    result = _run([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', str(path),
                   '-map', '0:a:0', '-ac', '1', '-ar', '24000', '-f', 's16le', '-'])
    return {'sha256_pcm': hashlib.sha256(result.stdout).hexdigest(),
            'decoded_samples_24khz_mono': len(result.stdout) // 2,
            'decoded_seconds': len(result.stdout) / 48000}


def _verify_picture(path, samples=None):
    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        raise ValueError(f'Cannot read opening: {path}')
    fps = capture.get(cv2.CAP_PROP_FPS)
    dimensions = [int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))]
    count = 0
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            count += 1
            if samples and count in (1, 361, 464, 720):
                cv2.imwrite(str(samples / f'frame-{count:04}.png'), frame)
                if count == 464:
                    cv2.imwrite(str(samples / 'poster.png'), frame)
    finally:
        capture.release()
    if count != FRAMES or abs(fps - FPS) > .001:
        raise ValueError(f'Expected 720 frames at 24 fps; decoded {count} at {fps}.')
    return {'decoded_frames': count, 'fps': fps, 'duration_seconds': count/fps,
            'resolution': dimensions}


def polish(source, timeline_path, output):
    source, timeline_path, output = map(lambda p: Path(p).resolve(), (source, timeline_path, output))
    if output.exists():
        raise FileExistsError(f'Use a fresh output folder: {output}')
    timeline = validate_timeline(json.loads(timeline_path.read_text(encoding='utf-8-sig')))
    source_video = _verify_picture(source)
    source_audio = _audio_signature(source)
    if source_audio['decoded_seconds'] + 1 / 24 < timeline['duration_seconds']:
        raise ValueError('Source audio is shorter than the measured narration.')
    output.mkdir(parents=True, exist_ok=False)
    (output / 'overlay.ass').write_text(build_ass(timeline), encoding='utf-8')
    (output / 'captions.json').write_text(json.dumps(caption_cues(timeline), indent=2), encoding='utf-8')
    # Padding exposes an editorial frame; every pixel of the source remains visible.
    filters = ('scale=1088:612:flags=lanczos,eq=contrast=1.025:saturation=0.97:gamma=1.015,'
               'pad=1280:720:96:42:color=0x070D13,'
               'drawbox=x=96:y=39:w=40:h=2:color=0xE5646B:t=fill,'
               'drawbox=x=136:y=39:w=1048:h=1:color=0x23303D:t=fill,'
               'drawbox=x=96:y=655:w=1088:h=1:color=0x23303D:t=fill,ass=overlay.ass')
    command = [imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-n', '-i', str(source),
               '-map', '0:v:0', '-map', '0:a:0', '-vf', filters, '-c:v', 'libx264',
               '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'copy',
               '-movflags', '+faststart', '-metadata', 'comment=Upscaled 360p proof; synthetic guide voice; approximate phrase captions',
               'video.mp4']
    result = _run(command, cwd=output)
    (output / 'ffmpeg.log').write_bytes(result.stderr)
    video = output / 'video.mp4'
    picture = _verify_picture(video, output)
    audio = _audio_signature(video)
    if audio != source_audio:
        raise ValueError('Decoded source and output audio differ; do not use this export.')
    report = {'valid': True, 'video': str(video), 'source': str(source), 'picture': picture,
              'source_picture': source_video, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'audio_preserved_bitexact_after_decode': True, 'audio': audio,
              'measured_spoken_seconds': timeline['duration_seconds'],
              'synthetic_guide': bool(timeline.get('synthetic_guide')),
              'upscaled': source_video['resolution'][0] < 1088,
              'caption_timing': 'Approximate phrase timing within measured paragraph boundaries; not forced alignment.',
              'full_source_composition_preserved': True, 'picture_box_xywh': PICTURE,
              'poster': str(output / 'poster.png')}
    (output / 'validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--timeline', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(polish(args.source, args.timeline, args.output), indent=2))
