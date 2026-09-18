"""Native cel-art overlays and secondary motion for the action sequence.

No image files are modified. All new marks are editable Blender geometry.
"""
import math
import bpy
from action_motion import throw_pose
from reference_crossover import key


def material(name, color):
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    nodes = result.node_tree.nodes
    nodes.clear()
    emit = nodes.new('ShaderNodeEmission')
    emit.inputs['Color'].default_value = color
    out = nodes.new('ShaderNodeOutputMaterial')
    result.node_tree.links.new(emit.outputs[0], out.inputs[0])
    return result


def contour(name, points, mat, depth=.025):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions = '3D'
    data.bevel_depth = depth
    data.resolution_u = 1
    spline = data.splines.new('POLY')
    spline.points.add(len(points)-1)
    for p, value in zip(spline.points, points):
        p.co = (*value, 1)
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    data.materials.append(mat)
    return obj


def polygon(name, points, mat, ink=None, y=-2.0):
    data = bpy.data.meshes.new(name)
    data.from_pydata([(x, y, z) for x, z in points], [], [tuple(range(len(points)))])
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    data.materials.append(mat)
    if ink:
        edge = contour(name+' ink', [(x, y-.02, z) for x, z in points+[points[0]]], ink)
        edge.parent = obj
    return obj


def capsule(name, length, radius, mat, ink):
    points = []
    for center, angles in ((length, range(-90, 91, 15)), (0, range(90, 271, 15))):
        points += [(center+radius*math.cos(math.radians(a)), radius*math.sin(math.radians(a))) for a in angles]
    return polygon(name, points, mat, ink)


def throw_arm():
    """Two linked cel sleeves; glove and tracked ankle share one grip target."""
    ink = material('Throw ink', (.012,.015,.021,1))
    white = material('Throw sleeve ivory', (.77,.81,.82,1))
    shade = material('Throw sleeve shadow', (.43,.50,.55,1))
    red = material('Throw glove crimson', (.56,.035,.026,1))
    # Cover only the old folded forearms; keep the approved head/cape/legs.
    torso = polygon('Unfolded chest', [(-2.83,1.62),(-1.27,1.62),(-1.35,.20),(-1.62,-.42),(-2.50,-.42),(-2.77,.20)], white, ink, -1.6)
    polygon('Crimson chest inset', [(-2.58,1.50),(-1.57,1.50),(-1.50,1.15),(-1.87,.98),(-1.87,-.42),(-2.27,-.42),(-2.27,.98),(-2.66,1.15)], red, None, -1.65)
    polygon('White central stripe', [(-2.12,1.55),(-2.0,1.55),(-2.0,-.40),(-2.12,-.40)], white, None, -1.67)
    # Guard arm rests alongside torso, rather than remaining folded across it.
    guard = capsule('Guard white sleeve', .95, .25, white, ink)
    guard.location = (-2.90, .1, 1.35)
    guard.rotation_euler.y = 1.45
    guard_glove = capsule('Guard lowered glove', .70, .21, red, ink)
    guard_glove.location = (-2.77, .07, .42)
    guard_glove.rotation_euler.y = 1.0
    upper = capsule('Throw upper sleeve', 1, .245, white, ink)
    forearm = capsule('Throw forearm glove', 1, .22, red, ink)
    # Rounded knuckles wrap the ankle. Fingers open after release.
    palm = polygon('Ankle grip palm', [(-.22,-.17),(.10,-.25),(.30,-.12),(.30,.13),(.15,.25),(-.20,.20)], red, ink, -2.35)
    fingers = []
    for i in range(3):
        finger = capsule('Grip finger '+str(i), .31, .075, red, ink)
        fingers.append(finger)
    for frame in range(1, 14):
        pose = throw_pose(frame)
        shoulder, elbow, grip = pose.shoulder, pose.elbow, pose.grip
        for obj, a, b in ((upper, shoulder, elbow), (forearm, elbow, grip)):
            dx, dz = b[0]-a[0], b[1]-a[1]
            key(obj, 'location', (a[0], 0, a[1]), frame)
            key(obj, 'rotation_euler', (0, -math.atan2(dz, dx), 0), frame)
            key(obj, 'scale', (math.hypot(dx,dz), 1, 1), frame)
        key(palm, 'location', (grip[0], 0, grip[1]), frame)
        for i, finger in enumerate(fingers):
            key(finger, 'location', (grip[0]-.06, -.4-i*.01, grip[1]-.13+i*.12), frame)
            key(finger, 'rotation_euler', (0, (.15 if pose.held else -.9-i*.32), 0), frame)
    return upper, forearm, palm


def debris(offset, start=44, end=64):
    """Small deterministic shards scatter from the contact, then fall."""
    dark = material('Impact concrete charcoal', (.13,.19,.23,1))
    light = material('Impact concrete lit', (.34,.43,.47,1))
    for i in range(18):
        phase = i * 2.39996
        shard = polygon('Wall chip '+str(i), [(-.06,-.09),(.10,-.04),(.045,.09)], light if i%3 else dark, y=-1.8)
        for f in range(start, end+1):
            t = (f-start)/(end-start)
            radius = (.8+(i%4)*.3)*t*3
            key(shard,'location',(offset+math.cos(phase)*radius,0,math.sin(phase)*radius-2*t*t),f)
            key(shard,'rotation_euler',(0,phase+t*(i%5),0),f)
            key(shard,'scale',((1-t)*1.5,1,(1-t)*1.5),f)


def speed_lines(offset, start, end, towards_camera=False):
    ink = material('Air streak pale', (.56,.71,.80,1))
    for i in range(10):
        z = -3.7+i*.78
        x = -7.6+(i%3)*.45
        points = [(x,-1.8,z),(x+1.1,-1.8,z+.12)]
        if towards_camera:
            theta = i*math.tau/10
            points = [(math.cos(theta)*r,-1.8,math.sin(theta)*r*.6) for r in (4.2,7.5)]
        obj = contour('Air streak '+str(i),points,ink,.012)
        for f in (1,max(1,start-1),end+1):
            key(obj,'hide_render',True,f)
        for f in range(start,end+1):
            phase=((f-start+i*2)%9)/9
            key(obj,'location',(offset+(0 if towards_camera else phase*12),0,0),f)
            key(obj,'hide_render',(f+i)%4==0,f)
