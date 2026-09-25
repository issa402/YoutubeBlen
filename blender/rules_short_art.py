"""Original procedural football art; Blender 4.5+, no external assets.

Stylized anonymous athletes, never an incident reconstruction or likeness.
Coordinates: Z up, character forward -Y, pitch surface Z=0.
"""
from __future__ import annotations

import math
import random

import bpy
import bmesh
from mathutils import Vector


COLORS = {
    "ink": "09091B", "sky": "151529", "purple": "302D51",
    "violet": "595275", "blue": "437FAD", "cyan": "80D3D5",
    "white": "E8D9BD", "red": "C63F50", "orange": "F48856",
    "gold": "E8BF72", "pitch": "222A3D", "grass": "283244",
    "skin": "B78172", "skin_light": "DAA88B", "skin_dark": "694C53",
    "hair": "191725", "silver": "7A89A3",
}
MATERIALS = {}


def material(key):
    if key in MATERIALS:
        return MATERIALS[key]
    value = COLORS.get(key, key)
    srgb = tuple(int(value[i:i + 2], 16) / 255 for i in (0, 2, 4))
    rgba = tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in srgb) + (1,)
    mat = bpy.data.materials.new(key)
    mat.diffuse_color = rgba
    MATERIALS[key] = mat
    return mat


def mesh(name, vertices, faces, color, parent=None):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material(color))
    obj.parent = parent
    return obj


def empty(name, location=(0, 0, 0), parent=None):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.parent = parent
    return obj


def box(name, location, scale, color, parent=None, bevel=0):
    vertices = [(x, y, z) for z in (-.5, .5) for y in (-.5, .5) for x in (-.5, .5)]
    obj = mesh(name, vertices, [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
                               (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)], color, parent)
    obj.location = location
    obj.scale = scale
    if bevel:
        modifier = obj.modifiers.new("drawn corners", "BEVEL")
        modifier.width = bevel
        modifier.segments = 1
    return obj


def sphere(name, location, scale, color, parent=None, subdivisions=2):
    data = bpy.data.meshes.new(name)
    geometry = bmesh.new()
    bmesh.ops.create_icosphere(geometry, subdivisions=subdivisions, radius=1)
    geometry.to_mesh(data)
    geometry.free()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.parent = parent
    obj.location = location
    obj.scale = scale if hasattr(scale, "__len__") else (scale,) * 3
    obj.data.materials.append(material(color))
    return obj


def tube(name, points, radius, color, parent=None, cyclic=False):
    data = bpy.data.curves.new(name, "CURVE")
    data.dimensions = "3D"
    data.resolution_u = 1
    data.bevel_depth = radius
    data.bevel_resolution = 0
    line = data.splines.new("POLY")
    line.points.add(len(points) - 1)
    for vertex, point in zip(line.points, points):
        vertex.co = (*point, 1)
    line.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material(color))
    obj.parent = parent
    return obj


def segment(name, radius, color, parent=None, taper=0.75):
    vertices = []
    count = 8
    for z, size in ((0, radius), (1, radius * taper)):
        vertices.extend((size * math.cos(i * math.tau / count),
                         size * math.sin(i * math.tau / count), z)
                        for i in range(count))
    faces = [tuple(range(7, -1, -1)), tuple(range(8, 16))]
    faces += [(i, (i + 1) % 8, (i + 1) % 8 + 8, i + 8) for i in range(8)]
    obj = mesh(name, vertices, faces, color, parent)
    source = COLORS.get(color, color)
    shadow = "".join(f"{int(int(source[i:i + 2], 16) * .55):02X}" for i in (0, 2, 4))
    obj.data.materials.append(material(shadow))
    for face in obj.data.polygons:
        if face.index in (3, 4, 5):
            face.material_index = 1
    return obj


def place_segment(obj, start, end, frame=None):
    direction = Vector(end) - Vector(start)
    obj.location = start
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = direction.to_track_quat("Z", "Y")
    obj.scale.z = direction.length
    if frame is not None:
        for prop in ("location", "rotation_quaternion", "scale"):
            obj.keyframe_insert(prop, frame=frame)


def rod(name, start, end, radius, color, parent=None):
    obj = segment(name, radius, color, parent, taper=1)
    place_segment(obj, start, end)
    return obj


def ring(name, location, radius, color, parent=None, thickness=0.03,
         plane="XY", count=64):
    points = []
    for i in range(count):
        x, y = radius * math.cos(math.tau * i / count), radius * math.sin(math.tau * i / count)
        points.append((x, y, 0) if plane == "XY" else (x, 0, y))
    obj = tube(name, points, thickness, color, parent, cyclic=True)
    obj.location = location
    return obj


def ball(name, location, parent=None, radius=0.16):
    root = empty(name, location, parent)
    sphere(name + ".leather", (0, 0, 0), radius, "white", root)
    # Twelve dark pentagonal panels on a faceted original football.
    phi = (1 + math.sqrt(5)) / 2
    axes = [(0, a, b * phi) for a in (-1, 1) for b in (-1, 1)]
    axes += [(a, b * phi, 0) for a in (-1, 1) for b in (-1, 1)]
    axes += [(b * phi, 0, a) for a in (-1, 1) for b in (-1, 1)]
    for i, axis in enumerate(axes):
        normal = Vector(axis).normalized()
        tangent = normal.cross(Vector((0.11, 0.13, 1))).normalized()
        bitangent = normal.cross(tangent)
        vertices = [normal * radius * 1.002]
        vertices += [normal * radius * .94 + radius * .32 * (
            math.cos(j * math.tau / 5) * tangent + math.sin(j * math.tau / 5) * bitangent)
                     for j in range(5)]
        mesh(f"{name}.panel{i}", vertices,
             [(0, j + 1, (j + 1) % 5 + 1) for j in range(5)], "ink", root)
    return root


def character(name, kit="red", skin="skin_light", parent=None):
    root = empty(name, parent=parent)
    root["forward_axis"] = "-Y"
    root["editorial_status"] = "Original anonymous illustration; not a replay"
    parts = {"root": root}
    parts["body"] = empty(name + ".body", parent=root)
    body = parts["body"]
    # Tailored athletic torso, broad shoulders, tapered waist; no block mannequin.
    vertices = [(-.23, -.14, 1.04), (.23, -.14, 1.04), (.23, .13, 1.04), (-.23, .13, 1.04),
                (-.38, -.19, 1.62), (.38, -.19, 1.62), (.32, .15, 1.62), (-.32, .15, 1.62)]
    torso = mesh(name + ".jersey", vertices,
                 [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7), (0, 3, 2, 1)], kit, body)
    torso.data.materials.append(material("ink"))
    torso.data.materials.append(material("orange" if kit == "red" else "cyan"))
    torso.data.polygons[2].material_index = 1
    torso.data.polygons[1].material_index = 2
    mesh(name + ".shirt-fold", [(-.12, -.195, 1.45), (.28, -.195, 1.55), (.20, -.164, 1.18)], [(0, 1, 2)], "ink", body)
    tube(name + ".collar", [(-.15, -.19, 1.64), (0, -.23, 1.54), (.15, -.19, 1.64)], .022, "white", body)
    mesh(name + ".chest-mark", [(-.24, -.198, 1.46), (-.17, -.198, 1.46), (-.17, -.198, 1.53), (-.24, -.198, 1.53)], [(0, 1, 2, 3)], "gold", body)
    sphere(name + ".hips", (0, 0, 1.01), (.255, .18, .19), "ink", body)
    rod(name + ".neck", (0, 0, 1.57), (0, 0, 1.76), .10, skin, body)
    head = empty(name + ".head", (0, -.035, 1.83), body)
    parts["head"] = head
    vertices = [(-.145, -.14, -.12), (0, -.18, -.22), (.145, -.14, -.12),
                (-.18, -.14, .14), (.18, -.14, .14), (-.15, .13, -.10),
                (.15, .13, -.10), (-.17, .13, .15), (.17, .13, .15)]
    mesh(name + ".face", vertices, [(0, 1, 2, 4, 3), (0, 3, 7, 5), (2, 6, 8, 4),
                                   (5, 7, 8, 6), (3, 4, 8, 7), (0, 5, 6, 2, 1)], skin, head)
    mesh(name + ".face-shadow", [(0, -.182, -.22), (.146, -.143, -.12), (.181, -.143, .14),
                                       (.06, -.163, .14), (.025, -.182, -.09)], [(0, 1, 2, 3, 4)], "skin_dark", head)
    sphere(name + ".hair", (0, .005, .14), (.19, .17, .13), "hair", head)
    mesh(name + ".hair-quiff", [(-.18, -.15, .13), (-.17, -.11, .30), (.10, -.12, .26),
                                (.19, -.10, .18), (.04, -.16, .15)], [(0, 1, 2, 3, 4)], "hair", head)
    for side in (-1, 1):
        x = side * .082
        tube(name + f".brow{side}", [(x - .043, -.165, .055), (x + .036, -.168, .036)], .013, "ink", head)
        box(name + f".eye{side}", (x, -.166, .014), (.045, .016, .012), "white", head)
    mesh(name + ".nose", [(0, -.16, .035), (-.027, -.218, -.05), (.026, -.218, -.048)], [(0, 1, 2)], "skin_light", head)
    tube(name + ".mouth", [(-.042, -.178, -.112), (.042, -.178, -.112)], .007, "ink", head)
    for side, x in (("L", -.20), ("R", .20)):
        for part, radius, color in (("thigh", .135, "ink"), ("shin", .09, kit),
                                    ("upperarm", .115, kit), ("forearm", .075, skin)):
            parts[f"{part}.{side}"] = segment(f"{name}.{part}.{side}", radius, color, body)
        parts[f"knee.{side}"] = sphere(f"{name}.knee.{side}", (x, 0, .55), .095, skin, body)
        parts[f"hand.{side}"] = sphere(f"{name}.hand.{side}", (x, 0, 1), (.07, .052, .09), skin, body)
        parts[f"boot.{side}"] = sphere(f"{name}.boot.{side}", (x, -.08, .085), (.108, .20, .085), "white", body)
    return parts


def pose(actor, frame, location, phase, mode="run", heading=math.pi / 2,
         intensity=1.0):
    root, body = actor["root"], actor["body"]
    root.location = location
    root.rotation_euler.z = heading
    root.keyframe_insert("location", frame=frame)
    root.keyframe_insert("rotation_euler", frame=frame)
    bob = .045 * abs(math.sin(phase * 2)) * intensity if mode == "run" else .01 * math.sin(phase)
    body.location.z = bob
    body.rotation_euler.x = -.1 * intensity if mode == "run" else -.02
    body.keyframe_insert("location", frame=frame)
    body.keyframe_insert("rotation_euler", frame=frame)
    for i, side in enumerate(("L", "R")):
        x = -.20 if i == 0 else .20
        swing = math.sin(phase + i * math.pi) * intensity
        hip = (x, 0, 1.01)
        # Ankles clear the floor; flexion remains within natural limb lengths.
        ankle = (x, -.38 * swing, .105 + .30 * max(0, -swing))
        knee = (x, -.17 - .18 * swing, .58 + .13 * max(0, -swing))
        shoulder = (x * 1.7, -.01, 1.53)
        elbow = (x * 2.15, .30 * swing, 1.22)
        hand = (x * 2.0, -.21 + .35 * swing, 1.07 + .08 * swing)
        if mode == "kick" and i == 1:
            ankle = (x, -.76 * intensity, .17 + .48 * intensity)
            knee = (x, -.38 * intensity, .58 + .12 * intensity)
            elbow = (x * 2.4, .15, 1.3)
            hand = (x * 3.0, .0, 1.28)
        if mode in ("stand", "whistle"):
            ankle, knee = (x, 0, .10), (x, -.025, .56)
            elbow, hand = (x * 2.15, -.01, 1.25), (x * 2.05, -.07, 1.03)
        if mode == "whistle" and i == 1:
            elbow, hand = (.48, -.17, 1.38), (.10, -.28, 1.74)
        for part, a, b in (("thigh", hip, knee), ("shin", knee, ankle),
                            ("upperarm", shoulder, elbow), ("forearm", elbow, hand)):
            place_segment(actor[f"{part}.{side}"], a, b, frame)
        for part, point in (("knee", knee), ("hand", hand), ("boot", (ankle[0], ankle[1] - .07, ankle[2]))):
            obj = actor[f"{part}.{side}"]
            obj.location = point
            obj.keyframe_insert("location", frame=frame)


def city_and_stadium(parent, seed=31):
    rng = random.Random(seed)
    box("field", (0, 0, -.14), (34, 30, .25), "pitch", parent)
    for y in range(-12, 16, 3):
        box("mown stripe", (0, y, -.006), (30, 1.5, .012), "grass", parent)
    tube("touchline", [(-9, -8, .016), (9, -8, .016), (9, 12, .016), (-9, 12, .016)], .022, "silver", parent, True)
    tube("halfway", [(-9, 1, .021), (9, 1, .021)], .02, "silver", parent)
    ring("center circle", (0, 1, .02), 2.6, "silver", parent, .023)
    for row in range(5):
        radius, z = 15 + row * .9, .4 + row * .55
        pts = [(radius * math.cos(a), 1 + radius * math.sin(a), z)
               for a in [i * math.pi / 48 for i in range(49)]]
        tube("stadium tier", pts, .06, "purple", parent)
        for i in range(35):
            angle = i * math.pi / 34
            sphere("crowd glint", (radius * math.cos(angle), 1 + radius * math.sin(angle), z + .24),
                   (.055, .04, .065), "orange" if rng.random() < .15 else "violet", parent, 1)
    # Stylized fractured skyline: polygon crowns, inset facade strips, slanted roofs.
    for i in range(19):
        x, y, height = (i - 9) * 2.3, 22 + rng.uniform(-1, 4), rng.uniform(5, 13)
        width = rng.uniform(1.2, 2)
        verts = [(x + a * width, y + b, z) for z in (0, height) for a, b in ((-.5, -.8), (.5, -.8), (.5, .8), (-.5, .8))]
        verts[4] = (verts[4][0], verts[4][1], height + rng.uniform(-1, 1.2))
        mesh("city silhouette", verts, [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7)],
             "purple" if i % 3 else "violet", parent)
        for floor in range(1, int(height)):
            tube("city facade", [(x - width * .45, y - .815, floor), (x + width * .45, y - .815, floor)], .022, "ink", parent)
            for column in (-.28, 0, .28):
                box("lit window", (x + column * width, y - .825, floor + .25),
                    (.09, .018, .32), "orange" if rng.random() < .15 else "silver", parent)
    for x in (-10, 10):
        rod("floodlight pole", (x, 8, 0), (x, 8, 8), .09, "ink", parent)
        box("floodlight housing", (x, 8, 8.2), (2.2, .3, .8), "ink", parent)
        for dx in (-.75, -.25, .25, .75):
            for dz in (-.18, .18):
                box("floodlight lamp", (x + dx, 7.82, 8.2 + dz), (.32, .04, .22), "gold", parent)
    return parent


def goal(parent, location=(3.2, 5.0, 0), width=4.2):
    root = empty("goal", location, parent)
    tube("goal frame", [(-width / 2, 0, 0), (-width / 2, 0, 2.5),
                        (width / 2, 0, 2.5), (width / 2, 0, 0)], .055, "white", root)
    for x in range(15):
        px = -width / 2 + width * x / 14
        tube("goal net vertical", [(px, 0, 2.5), (px, 1.25, 2.3), (px, 1.25, .02)], .009, "silver", root)
    for i in range(9):
        z = i * 2.3 / 8
        tube("goal net horizontal", [(-width / 2, 1.25, z), (width / 2, 1.25, z)], .009, "silver", root)
    return root


def panel(name, center, size, color, parent=None):
    root = empty(name, center, parent)
    box(name + ".case", (0, 0, 0), (size[0], .12, size[1]), "ink", root, .06)
    box(name + ".screen", (0, -.072, 0), (size[0] - .12, .03, size[1] - .12), color, root)
    return root


def arrow(name, points, color, parent=None, width=.035):
    obj = tube(name, points, width, color, parent)
    tip, prev = Vector(points[-1]), Vector(points[-2])
    direction = (tip - prev).normalized()
    side = Vector((-direction.y, direction.x, 0))
    if side.length < .1:
        side = Vector((1, 0, 0))
    mesh(name + ".head", [tip, tip - direction * .27 + side * .16,
                           tip - direction * .27 - side * .16], [(0, 1, 2)], color, parent)
    return obj
