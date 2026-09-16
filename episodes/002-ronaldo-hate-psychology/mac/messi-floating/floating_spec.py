"""Deterministic, Blender-independent choreography for the illustrated opening."""
import math

FRAME_END = 288
FPS = 24
PREVIEWS = (1, 72, 144, 216, 288)


def pose_at(frame):
    if type(frame) is not int or not 1 <= frame <= FRAME_END:
        raise ValueError('frame must be an integer from 1 to 288')
    t = (frame - 1) / (FRAME_END - 1)
    ease = t * t * (3 - 2 * t)
    return {'height': .16 * math.sin(t * math.tau * 2) + .25 * ease,
            'cape_phase': t * math.tau * 3,
            'camera_x': -.35 + .65 * ease,
            'camera_scale': 14.4 - 1.7 * ease}
