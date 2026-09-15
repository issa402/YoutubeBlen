"""Decode the entire opening video and record cut/motion evidence on Windows."""
import argparse
import json
from pathlib import Path

import cv2


def verify(video):
    capture = cv2.VideoCapture(str(video))
    if not capture.isOpened():
        raise ValueError(f'Cannot open video: {video}')
    fps = capture.get(cv2.CAP_PROP_FPS)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    count, previous, differences = 0, None, {}
    samples = {1,178,356,357,464,571,572,646,720}
    try:
        while True:
            valid, frame = capture.read()
            if not valid:
                break
            count += 1
            if frame.shape[:2] != (height, width):
                raise ValueError(f'Frame {count} changes resolution')
            small = cv2.resize(frame, (160, 90)).astype('float32')
            if previous is not None and count in samples:
                differences[str(count)] = round(float(abs(small-previous).mean()),6)
            previous = small
    finally:
        capture.release()
    if count != 720 or abs(fps-24) > .001:
        raise ValueError(f'Expected 720 frames at 24 fps; found {count} frames at {fps} fps')
    if any(differences[str(cut)] < 5 for cut in (357,572)):
        raise ValueError('Expected hard camera cuts are not visible in decoded frames')
    return {'valid':True,'video':str(Path(video).resolve()),'decoded_frames':count,
            'fps':fps,'duration_seconds':count/fps,'resolution':[width,height],
            'cut_frames':[357,572],'sampled_frame_difference_mean':differences,
            'scope':'Every video frame decoded; Blender motion-report.json validates object and light motion.'}


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('video',type=Path)
    parser.add_argument('--report',type=Path,required=True)
    args=parser.parse_args()
    report=verify(args.video)
    args.report.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))
