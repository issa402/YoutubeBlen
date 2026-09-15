"""Offline Windows guide narration with measured edit timing; never voice cloning."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import wave

from .core import write_json
from .episode import read_shots
from .media import _inspect_video, _run, ffmpeg


def synthesize(manifest):
    executable = shutil.which('powershell.exe') if os.name == 'nt' else None
    if not executable:
        raise RuntimeError('Guide speech uses installed Windows voices. Run this step on Windows.')
    script = Path(__file__).resolve().parents[1] / 'tools/speak_guide.ps1'
    _run([executable, '-NoProfile', '-NonInteractive', '-File', str(script),
          '-Manifest', str(manifest)], timeout=1800)


def wave_info(path):
    with wave.open(str(path), 'rb') as audio:
        if audio.getnframes() <= 0:
            raise ValueError(f'Empty guide audio: {Path(path).name}')
        return audio.getparams(), audio.getnframes() / audio.getframerate()


def join_waves(paths, output):
    properties = [wave_info(path) for path in paths]
    if not properties:
        raise ValueError('No narration segments.')
    first = properties[0][0]
    if any((p.nchannels, p.sampwidth, p.framerate, p.comptype) !=
           (first.nchannels, first.sampwidth, first.framerate, first.comptype)
           for p, _ in properties):
        raise ValueError('Narration segments use inconsistent audio formats.')
    # Exclusive creation: preserve previous work, including partial runs.
    with Path(output).open('xb') as file, wave.open(file, 'wb') as out:
        out.setparams(first)
        for path in paths:
            with wave.open(str(path), 'rb') as incoming:
                while chunk := incoming.readframes(65536):
                    out.writeframesraw(chunk)
    return [duration for _, duration in properties]


def stamp(seconds, srt=False):
    millis = round(seconds * 1000)
    hours, millis = divmod(millis, 3600000)
    minutes, millis = divmod(millis, 60000)
    secs, millis = divmod(millis, 1000)
    return f'{hours:02d}:{minutes:02d}:{secs:02d}' + (f',{millis:03d}' if srt else '')


def chapter_title(section):
    return re.sub(r'^\d+:\d+\s*[–-]\s*\d+:\d+\s*[—-]\s*', '', section)


def create_guide(studio, episode, output, opening=False, rate=0, voice='Microsoft David Desktop'):
    if isinstance(rate, bool) or not isinstance(rate, int) or not -10 <= rate <= 10:
        raise ValueError('Voice rate must be an integer from -10 to 10.')
    if not isinstance(voice, str) or not voice.strip() or len(voice) > 200:
        raise ValueError('Choose an installed Windows voice name.')
    base = studio.require_episode(episode)
    source = base / ('script/OPENING_NARRATION.txt' if opening else 'script/MASTER_PRODUCTION_SCRIPT.md')
    if opening:
        text = source.read_text(encoding='utf-8-sig').strip()
        shots = [{'id': 'SH01', 'section': 'Opening', 'voiceover': text}]
    else:
        shots = read_shots(source)
    narration = '\n\n'.join(shot['voiceover'] for shot in shots) + '\n'
    clean_script = base / 'script/NARRATION.txt'
    if not opening and clean_script.is_file():
        clean_text = clean_script.read_text(encoding='utf-8-sig')
        if ' '.join(clean_text.split()) != ' '.join(narration.split()):
            raise ValueError('NARRATION.txt differs from the master voiceover. Reconcile the intended text before generating audio.')
    if not narration.strip() or len(narration) > 100000:
        raise ValueError('Narration needs 1–100000 characters.')
    paragraphs = [(shot, text.strip()) for shot in shots
                  for text in re.split(r'\n\s*\n', shot['voiceover']) if text.strip()]
    segments = [{'id': f'P{index:04d}', 'shot': shot['id'], 'section': shot['section'],
                 'text': text, 'audio_file': f'segment_{index:04d}.wav'}
                for index, (shot, text) in enumerate(paragraphs, start=1)]
    destination = Path(output).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    (destination / 'narration.txt').write_text(narration, encoding='utf-8')
    manifest = {'voice': voice, 'rate': rate, 'synthetic_guide': True, 'segments': segments,
                'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
    write_json(destination / 'speech-manifest.json', manifest)
    synthesize(destination / 'speech-manifest.json')
    audio = destination / 'narration-guide.wav'
    durations = join_waves([destination / s['audio_file'] for s in segments], audio)
    starts = [sum(durations[:i]) for i in range(len(durations))]
    timed = [segment | {'start_seconds': round(start, 6), 'end_seconds': round(start+duration, 6)}
             for segment, start, duration in zip(segments, starts, durations)]
    total = sum(durations)
    timeline = destination / 'timeline.json'
    write_json(timeline, manifest | {'duration_seconds': total, 'segments': timed,
        'timing_note': 'Measured paragraph audio boundaries; not word-level forced alignment.'})
    subtitles = destination / 'guide-paragraphs.srt'
    subtitles.write_text('\n\n'.join(
        f"{i}\n{stamp(s['start_seconds'], True)} --> {stamp(s['end_seconds'], True)}\n{s['text']}"
        for i, s in enumerate(timed, start=1)) + '\n', encoding='utf-8')
    chapters = [s for i, s in enumerate(timed) if i == 0 or s['shot'] != timed[i-1]['shot']]
    (destination / 'chapters.txt').write_text('\n'.join(
        f"{stamp(s['start_seconds'])} {chapter_title(s['section'])}" for s in chapters) + '\n', encoding='utf-8')
    result = {'audio': str(audio), 'narration': str(destination / 'narration.txt'),
              'timeline': str(timeline), 'subtitles': str(subtitles), 'word_count': len(narration.split()),
              'duration_seconds': round(total, 3), 'segment_count': len(segments),
              'synthetic_guide': True, 'final_voice_approved': False}
    write_json(destination / 'report.json', result)
    return result


def mux_guide(video, audio, output):
    video, audio = Path(video).resolve(), Path(audio).resolve()
    if not video.is_file() or not audio.is_file():
        raise FileNotFoundError('Both video and narration WAV are required.')
    video_info = _inspect_video(video)
    _, duration = wave_info(audio)
    hold = max(0, duration - video_info['duration_seconds'])
    target_duration = max(duration, video_info['duration_seconds'])
    destination = Path(output).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    target = destination / 'video.mp4'
    _run([ffmpeg(), '-hide_banner', '-loglevel', 'error', '-nostdin', '-n',
          '-i', str(video), '-i', str(audio), '-map', '0:v:0', '-map', '1:a:0',
          '-vf', f'tpad=stop_mode=clone:stop_duration={hold:.6f}', '-af', 'apad',
          '-t', str(target_duration), '-c:v', 'libx264', '-crf', '19', '-pix_fmt', 'yuv420p',
          '-c:a', 'aac', '-movflags', '+faststart', str(target)])
    report = {'video': str(target), 'synthetic_guide': True, 'audio_duration_seconds': duration,
              'held_last_frame_seconds': round(hold, 3), 'duration_seconds': target_duration}
    write_json(destination / 'assembly.json', report)
    return report
