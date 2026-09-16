"""Reference-derived shot timing, independent of Blender."""
import math
FPS=24
FRAME_END=104
SHOTS=(('messi',1,23),('mbappe',24,46),('point',47,71),('ronaldo',72,104))
PREVIEWS=(1,23,24,46,47,60,71,72,86,104)


def shot_at(frame):
    if type(frame) is not int or not 1<=frame<=FRAME_END:
        raise ValueError('frame must be an integer from 1 to 104')
    return next(name for name,start,end in SHOTS if start<=frame<=end)


def pose_at(frame):
    shot=shot_at(frame)
    return {'shot':shot,'hover':.09*math.sin((frame-1)*math.tau/48),
            'cape_phase':(frame-1)*math.tau/32,
            'point_extension':min(1,max(0,(frame-47)/12)),
            'reveal':min(1,max(0,(frame-72)/10))}
