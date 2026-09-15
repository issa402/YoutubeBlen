"""Offline script-preserving captions anchored to Whisper word timestamps.

This is approximate ASR alignment, not phoneme-level forced alignment. The
supplied script is the text authority; recognition supplies only timing anchors.
"""
from difflib import SequenceMatcher
import hashlib
import html
import json
import math
from pathlib import Path
import re
import unicodedata
import wave

from .media import ROOT, _timestamp

MIN_MATCH_RATIO = .8
ARTIFACTS = ('alignment.json', 'captions.srt', 'captions.vtt')


def _speech_model(model: str):
    from faster_whisper import WhisperModel
    return WhisperModel(model, device='cpu', compute_type='int8', cpu_threads=2,
                        download_root=str(ROOT / '.studio' / 'models'), local_files_only=True)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _normalized(word: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFKC', word).casefold() if c.isalnum())


def _inputs(audio, text_path, output, model):
    if model not in ('tiny', 'base', 'small'):
        raise ValueError('Caption model must be tiny, base or small, already cached locally')
    source, script, destination = Path(audio).resolve(), Path(text_path).resolve(), Path(output).resolve()
    for path in (source, script):
        if not path.is_file():
            raise FileNotFoundError(f'Caption input not found: {path}')
    text = script.read_text(encoding='utf-8-sig')
    tokens = text.split()
    if not tokens or len(tokens) > 6000 or len(text) > 60000:
        raise ValueError('Caption script must contain 1–6000 words and at most 60000 characters')
    if any(unicodedata.category(c) == 'Cc' and c not in '\r\n\t' for c in text):
        raise ValueError('Caption script contains unsupported control characters')
    try:
        with wave.open(str(source), 'rb') as handle:
            duration = handle.getnframes() / handle.getframerate()
            if handle.getcomptype() != 'NONE' or not .01 <= duration <= 3600:
                raise ValueError('Caption audio must be an uncompressed WAV lasting at most one hour')
    except (wave.Error, EOFError) as exc:
        raise ValueError('Caption audio must be a readable uncompressed WAV') from exc
    if any((destination / name).exists() for name in ARTIFACTS):
        raise FileExistsError(f'Caption artifact exists; choose a fresh output directory: {destination}')
    destination.mkdir(parents=True, exist_ok=True)
    return source, script, destination, tokens, duration


def _recognize(audio: Path, model: str) -> list[dict]:
    segments, _ = _speech_model(model).transcribe(
        str(audio), beam_size=5, language='en', word_timestamps=True,
        vad_filter=False, condition_on_previous_text=False)
    records = []
    for segment in segments:
        for word in segment.words or ():
            # Ignore punctuation-only recognizer records, never script tokens.
            if _normalized(word.word):
                records.append({'text': word.word.strip(), 'start': float(word.start),
                                'end': float(word.end)})
    return records


def _validate_asr(records: list[dict], duration: float) -> None:
    previous_end = 0.0
    for index, word in enumerate(records):
        start, end = word['start'], word['end']
        if (not math.isfinite(start) or not math.isfinite(end) or start < 0 or end <= start
                or end > duration + .001 or start + .001 < previous_end):
            raise ValueError(f'Invalid ASR word timing at index {index}: {start}–{end}')
        previous_end = end


def _matching(tokens: list[str], records: list[dict]) -> dict[int, int]:
    matcher = SequenceMatcher(None, [_normalized(w) for w in tokens],
                              [_normalized(w['text']) for w in records], autojunk=False)
    return {block.a + offset: block.b + offset
            for block in matcher.get_matching_blocks() for offset in range(block.size)
            if _normalized(tokens[block.a + offset])}


def _interpolate(words: list[dict], start: int, end: int, duration: float) -> list[dict]:
    """Fill one unmatched run; borrowing anchor time is explicitly relabeled."""
    left = words[start - 1] if start else None
    right = words[end] if end < len(words) else None
    lower = left['end'] if left else 0.0
    upper = right['start'] if right else duration
    updated = list(words)
    if upper - lower < .04 * (end - start):
        if left:
            lower = (left['start'] + left['end']) / 2
            updated[start - 1] = {**left, 'end': lower, 'timing_method': 'interpolated'}
        if right:
            upper = (right['start'] + right['end']) / 2
            updated[end] = {**right, 'start': upper, 'timing_method': 'interpolated'}
    weights = [max(1, len(_normalized(w['text']))) for w in words[start:end]]
    if upper - lower < .001 * len(weights):
        raise ValueError('Invalid interpolation timing: no room for unmatched script words')
    boundaries = [lower]
    for weight in weights:
        boundaries.append(boundaries[-1] + (upper - lower) * weight / sum(weights))
    for offset, index in enumerate(range(start, end)):
        updated[index] = {**words[index], 'start': boundaries[offset],
                          'end': upper if index == end - 1 else boundaries[offset + 1]}
    return updated


def _word_timings(tokens, records, matches, duration) -> list[dict]:
    words = [{'index': i, 'text': token, 'start': records[matches[i]]['start'] if i in matches else None,
              'end': records[matches[i]]['end'] if i in matches else None,
              'timing_method': 'matched' if i in matches else 'interpolated',
              'asr_index': matches.get(i)} for i, token in enumerate(tokens)]
    index = 0
    while index < len(words):
        if index in matches:
            index += 1
            continue
        end = index + 1
        while end < len(words) and end not in matches:
            end += 1
        words = _interpolate(words, index, end, duration)
        index = end
    _validate_asr(words, duration)
    return words


def _ass_text(text: str) -> str:
    # Fullwidth glyphs prevent ASS override blocks/newline commands. Raw text is
    # separately preserved; adding a backslash does not reliably escape braces.
    return text.translate(str.maketrans({'{': '｛', '}': '｝', '\\': '＼'}))


def _phrase_spans(words: list[dict], lower: int, upper: int) -> list[tuple[int, int]]:
    """Balance short phrases with punctuation; avoid a dangling one-word tail."""
    if upper - lower <= 6:
        return [(lower, upper)]
    costs, following = {upper: 0.0}, {}
    weak_ends = {'a', 'an', 'the', 'to', 'your', 'my', 'his', 'her', 'their', 'of', 'and', 'or'}
    for start in range(upper - 1, lower - 1, -1):
        candidates = []
        for end in range(start + 2, min(start + 6, upper) + 1):
            if end not in costs:
                continue
            size = end - start
            punctuation = bool(re.search(r'[,;:]["\u201d\u2019\')]*$', words[end - 1]['text']))
            penalty = .25 * (size - 5) ** 2
            if size < 4 and not punctuation:
                penalty += 2 * (4 - size)
            if end < upper and _normalized(words[end - 1]['text']) in weak_ends:
                penalty += 7
            if punctuation:
                penalty -= 3
            candidates.append((costs[end] + penalty, end))
        if candidates:
            costs[start], following[start] = min(candidates)
    spans, start = [], lower
    while start < upper:
        end = following[start]
        spans.append((start, end))
        start = end
    return spans


def _cues(words: list[dict]) -> list[dict]:
    spans, sentence_start = [], 0
    for index, word in enumerate(words):
        if re.search(r'[.!?]["\u201d\u2019\')]*$', word['text']) or index == len(words) - 1:
            spans.extend(_phrase_spans(words, sentence_start, index + 1))
            sentence_start = index + 1
    cues = []
    for start, end in spans:
        text = ' '.join(w['text'] for w in words[start:end])
        cues.append({'text': text, 'ass_text': _ass_text(text), 'start': words[start]['start'],
                     'end': words[end - 1]['end'], 'word_start': start, 'word_end': end,
                     'timing': 'ASR anchors with interpolation' if any(
                         w['timing_method'] == 'interpolated' for w in words[start:end])
                         else 'ASR word timestamps'})
    return cues


def _json_safe(value):
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return repr(value)
    return value


def _write_report(path: Path, report: dict) -> None:
    with path.open('x', encoding='utf-8') as handle:
        json.dump(_json_safe(report), handle, indent=2, ensure_ascii=False, allow_nan=False)


def _write_subtitles(output: Path, cues: list[dict]) -> None:
    for name, is_vtt in (('captions.srt', False), ('captions.vtt', True)):
        with (output / name).open('x', encoding='utf-8') as handle:
            if is_vtt:
                handle.write('WEBVTT\n\n')
            for index, cue in enumerate(cues, 1):
                start, end = _timestamp(cue['start']), _timestamp(cue['end'])
                if is_vtt:
                    start, end = start.replace(',', '.'), end.replace(',', '.')
                handle.write(f"{index}\n{start} --> {end}\n{html.escape(cue['text'], quote=False)}\n\n")


def align(audio, text_path, output, model: str = 'tiny') -> dict:
    """Align an exact English script to a WAV, using a cached local ASR model.

    Returns the same dictionary saved in alignment.json. Any recognition/timing
    failure leaves diagnostics in that file and raises ValueError. Existing
    artifacts are never overwritten. Coverage describes supplied-text coverage,
    not independent verification that every word was actually spoken.
    """
    source, script, destination, tokens, duration = _inputs(audio, text_path, output, model)
    report = {'status': 'failed', 'input_audio': str(source), 'input_text': str(script),
              'source_audio_sha256': _sha256(source), 'source_text_sha256': _sha256(script),
              'model': model, 'duration_seconds': duration, 'script_word_count': len(tokens),
              'matched_word_count': 0, 'asr_match_ratio': 0.0, 'asr_precision': 0.0,
              'minimum_match_ratio': MIN_MATCH_RATIO, 'full_spoken_word_coverage': False,
              'coverage_meaning': 'Every supplied script token emitted, not proof of actual spoken coverage',
              'timing_method': 'Approximate ASR word anchors and interpolated unmatched script words; not forced alignment',
              'words': [], 'cues': [], 'asr_words': [], 'warnings': [],
              'json': str(destination / 'alignment.json'),
              'srt': str(destination / 'captions.srt'), 'vtt': str(destination / 'captions.vtt')}
    try:
        records = _recognize(source, model)
        report = {**report, 'asr_words': records}
        _validate_asr(records, duration)
        matches = _matching(tokens, records)
        ratio, precision = len(matches) / len(tokens), len(matches) / max(1, len(records))
        report = {**report, 'matched_word_count': len(matches),
                  'asr_match_ratio': ratio, 'asr_precision': precision}
        if ratio < MIN_MATCH_RATIO or precision < MIN_MATCH_RATIO:
            raise ValueError(f'Insufficient ASR coverage: script match {ratio:.1%}, ASR precision {precision:.1%}; '
                             'check the audio/script pair or use a better already-cached model')
        words = _word_timings(tokens, records, matches, duration)
        cues = _cues(words)
        complete = ' '.join(c['text'] for c in cues) == ' '.join(tokens)
        if not complete:
            raise ValueError('Internal caption coverage mismatch')
        interpolated = sum(w['timing_method'] == 'interpolated' for w in words)
        warnings = [f'{interpolated} script words have interpolated or adjusted timing; listen and review them.'] if interpolated else []
        report = {**report, 'status': 'aligned', 'words': words, 'cues': cues,
                  'interpolated_word_count': interpolated, 'full_spoken_word_coverage': complete,
                  'warnings': warnings}
    except Exception as exc:
        _write_report(destination / 'alignment.json', {**report, 'status': 'failed', 'error': str(exc)})
        raise ValueError(f'Caption alignment failed: {exc}. Diagnostics: {destination / "alignment.json"}') from exc
    _write_subtitles(destination, cues)
    _write_report(destination / 'alignment.json', report)
    return report
