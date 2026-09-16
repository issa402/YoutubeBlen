"""Reference-derived shot timing, independent of Blender."""
import math
FPS=24
FRAME_END=192
SHOTS=(('messi',1,44),('mbappe',45,87),('point',88,132),('ronaldo',133,192))
PREVIEWS=(1,44,45,87,88,112,132,133,160,192)


def shot_at(frame):
    if type(frame) is not int or not 1<=frame<=FRAME_END:
        raise ValueError('frame must be an integer from 1 to 192')
    return next(name for name,start,end in SHOTS if start<=frame<=end)


def pose_at(frame):
    shot=shot_at(frame)
    return {'shot':shot,'hover':.09*math.sin((frame-1)*math.tau/48),
            'cape_phase':(frame-1)*math.tau/32,
            'point_extension':min(1,max(0,(frame-88)/24)),
            'reveal':min(1,max(0,(frame-133)/18))}
