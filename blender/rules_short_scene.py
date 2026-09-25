"""Original anonymous football editorial animation. Blender 4.5+, no downloads.

blender -b --python blender/rules_short_scene.py -- --timeline timeline.json
  --output .studio/shorts/consistent-rules/render-v1 --preview --resolution 270 480

--build saves the editable packed scene; --render writes frame_00001.png etc.
All action is illustrative and cannot serve as an actual match replay.
Captions, source labels, and audio are assembled separately by the editor.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rules_short_art as art
import animation_compat


SCENE_IDS = ("hook", "draw", "egypt", "salah", "austria", "check", "evidence", "close")
FPS = 30
ACTORS = []
BALLS = []
CAMERAS = []
SHOTS = []
CUTS = []


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeline", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--audio", type=Path, help="Final narration/mix WAV or OGG embedded at frame one")
    for flag in ("build", "preview", "render"):
        parser.add_argument("--" + flag, action="store_true")
    parser.add_argument("--resolution", nargs=2, type=int, default=(1080, 1920))
    parser.add_argument("--frames", nargs="*", type=int)
    parser.add_argument("--start-frame", type=int)
    parser.add_argument("--end-frame", type=int)
    tail = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(tail)


def load_timeline(path):
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if data.get("fps", 30) != FPS:
        raise ValueError("Delivery requires 30 fps")
    scenes = data.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise ValueError("timeline requires nonempty scenes")
    previous, ids = 0.0, set()
    for shot in scenes:
        ident, start, end = shot.get("id"), shot.get("start"), shot.get("end")
        if ident not in SCENE_IDS or ident in ids:
            raise ValueError(f"Unknown or duplicate shot {ident!r}")
        if not all(isinstance(x, (int, float)) and math.isfinite(x) for x in (start, end)):
            raise ValueError("Shot boundaries must be finite seconds")
        if abs(start - previous) > .001 or end - start < 1:
            raise ValueError("Shots must be contiguous, begin at zero, and last at least a second")
        ids.add(ident)
        previous = end
    if abs(float(data.get("duration_seconds", previous)) - previous) > .04:
        raise ValueError("Final shot and duration disagree")
    return data


def key(obj, frame, **values):
    for prop, value in values.items():
        setattr(obj, prop, value)
        obj.keyframe_insert(prop, frame=frame)


def ease(t):
    t = min(1, max(0, t))
    return t * t * (3 - 2 * t)


def mix(a, b, t):
    return Vector(a).lerp(Vector(b), t)


def path(points, t):
    t = min(.999999, max(0, t)) * (len(points) - 1)
    index = int(t)
    return mix(points[index], points[index + 1], t - index)


def camera(name, root, position, target, lens=58, ortho=None):
    data = bpy.data.cameras.new(name)
    data.lens, data.clip_end, data.clip_start = lens, 140, .05
    if ortho:
        data.type, data.ortho_scale = "ORTHO", ortho
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.parent, obj.location = root, position
    obj.rotation_euler = (Vector(target) - Vector(position)).to_track_quat("-Z", "Y").to_euler()
    CAMERAS.append(obj)
    return obj


def move_camera(obj, frame, position, target):
    key(obj, frame, location=position,
        rotation_euler=(Vector(target) - Vector(position)).to_track_quat("-Z", "Y").to_euler())


def actor(name, root, kit="red", skin="skin_light"):
    item = art.character(name, kit, skin, root)
    ACTORS.append(item)
    return item


def moving_ball(name, root):
    obj = art.ball(name, (0, 0, .17), root)
    BALLS.append(obj)
    return obj


def kick_ball(obj, frame, t, start, destination, kick=.42, end=.68):
    progress = min(1, max(0, (t - kick) / (end - kick)))
    position = mix(start, destination, progress)
    position.z += math.sin(progress * math.pi) * 1.35
    key(obj, frame, location=position, rotation_euler=(progress * 18, progress * 6, t * 2))


def art_collection():
    before = set(bpy.data.objects)
    art.city_and_stadium(None)
    collection = bpy.data.collections.new("shared original stadium")
    for obj in set(bpy.data.objects) - before:
        for existing in tuple(obj.users_collection):
            existing.objects.unlink(obj)
        collection.objects.link(obj)
    return collection


def backdrop(root):
    image_path = Path(__file__).parent / "assets" / "rules-stadium.png"
    if not image_path.is_file():
        return
    image = bpy.data.images.load(str(image_path), check_existing=True)
    data = bpy.data.materials.new("original generated stadium illustration")
    data.use_nodes = True
    node = data.node_tree.nodes.new("ShaderNodeTexImage")
    node.image = image
    data.node_tree.nodes.active = node
    data.node_tree.links.new(node.outputs["Color"], data.node_tree.nodes.get("Principled BSDF").inputs["Base Color"])
    obj = art.mesh("painted distant atmosphere", [(-29, 29, -45), (29, 29, -45),
                    (29, 29, 58), (-29, 29, 58)], [(0, 1, 2, 3)], "sky", root)
    obj.data.materials.clear()
    obj.data.materials.append(data)
    uv = obj.data.uv_layers.new(name="original art UV")
    for loop, coord in zip(uv.data, ((0, 0), (1, 0), (1, 1), (0, 1))):
        loop.uv = coord


def stage(shot, index, environment):
    root = art.empty("stage." + shot["id"], (index * 200, 0, 0))
    instance = art.empty("stadium.instance", parent=root)
    instance.instance_type, instance.instance_collection = "COLLECTION", environment
    backdrop(root)
    return root


def sample(shot):
    first, last = shot["first_frame"], shot["last_frame"]
    frames = sorted(set(range(first, last + 1, 3)) | {last})
    for frame in frames:
        yield frame, (frame - first) / max(1, last - first), (frame - first) / FPS


def field_action(kind, seconds, t):
    """Narration-aligned local timing for the two illustrative scoring passages."""
    cues = {"egypt": (1.0946666667, 2.3946666667, 2.9946666667),
            "austria": (3.688, 4.788, None)}
    if kind not in cues:
        return t
    kick, arrival, rewind = cues[kind]
    if seconds < kick:
        return .42 * seconds / kick
    if seconds < arrival:
        return .42 + .26 * (seconds - kick) / (arrival - kick)
    if rewind is not None and seconds > rewind:
        return .68 - .52 * min(1, (seconds - rewind) / 1.0)
    return .68


def field_sequence(root, shot, kind):
    red = actor(kind + ".striker", root, "red", "skin_light")
    blue = actor(kind + ".defender", root, "blue", "skin")
    ball = moving_ball(kind + ".football", root)
    art.goal(root, (2.5, 3.7, 0), 3.8)
    cam = camera(kind + ".camera", root, (5, -5, 3.4), (.0, .3, .65), 53, 7.3)
    burst = art.ring("goal pulse", (2.55, 3.64, 1.3), .7, "orange", root, .035, "XZ")
    hand = None
    if kind == "egypt":
        clock = art.empty("review clock", (-1.5, 2.0, 2.75), root)
        art.ring("clock dial", (0, 0, 0), .65, "gold", clock, .038, "XZ")
        hand = art.tube("clock hand", [(0, -.03, 0), (0, -.03, .52)], .027, "orange", clock)
        for i in range(12):
            angle = i * math.tau / 12
            art.rod("clock marker", (.57 * math.sin(angle), 0, .57 * math.cos(angle)),
                    (.63 * math.sin(angle), 0, .63 * math.cos(angle)), .016, "white", clock)
    for frame, t, seconds in sample(shot):
        action = field_action(kind, seconds, t)
        run = min(1, action / .43)
        mode = "run" if action < .37 else "kick" if action < .53 else "stand"
        rewind_finished = kind == "egypt" and seconds > 3.995
        if rewind_finished:
            mode = "stand"
        power = math.sin(min(1, max(0, (action - .37) / .16)) * math.pi) if mode == "kick" else .8
        art.pose(red, frame, (-1.15 + 1.22 * run, -.05 + .40 * run, 0), seconds * 7.8,
                 mode, heading=2.15, intensity=power)
        art.pose(blue, frame, (.7 + .4 * run, 1.8 + .6 * run, 0), seconds * 7.2 + 1,
                 "run" if action < .52 and not rewind_finished else "stand", heading=2.3, intensity=.65)
        kick_ball(ball, frame, action, (.22, .10, .17), (2.5, 4.0, .40))
        scale = .7 + .7 * math.sin(max(0, action - .59) * 8)
        key(burst, frame, scale=(scale,) * 3)
        if hand:
            key(hand, frame, rotation_euler=(0, -action * math.tau * 3, 0))
        push = ease(t)
        move_camera(cam, frame, (5.0 - push * .6, -5.6 + push * .7, 3.4 - .35 * push),
                    (-.25 + push * .24, .7, .70))
    if kind == "egypt":
        shot["choreography_seconds"] = {"kick": shot["start"] + 1.0946666667,
            "goal": shot["start"] + 2.3946666667, "rewind": shot["start"] + 2.9946666667}
    elif kind == "austria":
        shot["choreography_seconds"] = {"kick": shot["start"] + 3.688,
            "goal": shot["start"] + 4.788}
    return cam


def bracket_sequence(root, shot):
    cam = camera("draw.camera", root, (0, -10, 3), (0, 0, 1.25), 50, 9.4)
    routes, orbs = [], []
    for side in (-1, 1):
        color = "orange" if side == -1 else "cyan"
        for row in range(4):
            z = 1.0 + row * .88
            seed = art.panel("bracket seed", (side * 1.75, -.03, z), (.84, .46), "purple", root)
            if row == 3:
                name = "SPAIN" if side < 0 else "ARGENTINA"
                data = bpy.data.curves.new("bracket label " + name, "FONT")
                data.body, data.align_x, data.align_y, data.size = name, "CENTER", "CENTER", .12
                data.extrude = 0
                label = bpy.data.objects.new(name, data)
                bpy.context.collection.objects.link(label)
                label.parent, label.location = seed, (0, -.105, 0)
                label.rotation_euler.x = math.pi / 2
                data.materials.append(art.material("white"))
            points = [(side * 1.32, -.15, z), (side * .93, -.15, z),
                      (side * .93, -.15, 1.43 + (row // 2) * 1.76),
                      (side * .50, -.15, 1.43 + (row // 2) * 1.76)]
            art.tube("bracket branch", points, .021, color, root)
        route = [(side * 1.75, -.25, 1.0), (side * .93, -.25, 1.0),
                 (side * .93, -.25, 1.43), (side * .5, -.25, 1.43),
                 (side * .5, -.25, 2.31), (side * .15, -.25, 2.31)]
        art.tube("bracket final route", route[3:], .04, color, root)
        routes.append(route)
        orbs.append(art.sphere("bracket travelling marker", route[0], .095, color, root))
    trophy = art.empty("abstract final trophy", (0, -.15, 4.05), root)
    art.rod("trophy stem", (0, 0, -.4), (0, 0, 0), .06, "gold", trophy)
    art.sphere("trophy cup", (0, 0, .07), (.22, .13, .27), "gold", trophy)
    art.ring("trophy halo", (0, .03, .05), .38, "orange", trophy, .022, "XZ")
    for frame, t, seconds in sample(shot):
        for obj, route in zip(orbs, routes):
            key(obj, frame, location=path(route, (t * 1.7) % 1))
        key(trophy, frame, rotation_euler=(0, 0, .15 * math.sin(seconds)))
        move_camera(cam, frame, (.25 * math.sin(t * 2), -10 + .5 * t, 3.1), (0, 0, 1.4))
    return cam


def possession_sequence(root, shot):
    red = actor("possession.attacker", root, "red", "skin")
    left = actor("possession.challenger.L", root, "blue", "skin_light")
    right = actor("possession.challenger.R", root, "blue", "skin_dark")
    ball = moving_ball("possession.ball", root)
    cam = camera("salah.camera", root, (4.4, -7.8, 4), (0, .5, .65), 57, 7.7)
    art.arrow("possession arrow", [(-1.7, -1.0, .045), (-.9, -1.0, .045), (.25, -.1, .045),
                                   (1.3, .25, .045)], "cyan", root, .045)
    for frame, t, seconds in sample(shot):
        move = ease(t)
        art.pose(red, frame, (-.7 + .8 * move, .45 * move, 0), seconds * 7.5, "run", heading=2.0, intensity=.66)
        art.pose(left, frame, (-1.45 + .7 * move, 1.4 - .35 * move, 0), seconds * 7.1 + .7,
                 "run", heading=.9, intensity=.5)
        art.pose(right, frame, (1.4 - .50 * move, 1.1 + .3 * move, 0), seconds * 7.4 + 1.1,
                 "run", heading=-.5, intensity=.55)
        key(ball, frame, location=(-.25 + .9 * move, -.16 + .7 * move, .18 + .03 * math.sin(seconds * 6)),
            rotation_euler=(seconds * 4, 0, seconds))
        move_camera(cam, frame, (4.3 - t, -7.4 + t * .4, 3.7), (t * .2, .5, .65))
    return cam


def monitor_feed(parent, center, size, color, name):
    screen = art.panel(name, center, size, "pitch", parent)
    w, h = size[0] * .43, size[1] * .38
    art.tube(name + ".boundary", [(-w, -.11, -h), (w, -.11, -h),
                                  (w, -.11, h), (-w, -.11, h)], .012, "silver", screen, True)
    art.tube(name + ".center", [(0, -.12, -h), (0, -.12, h)], .01, "silver", screen)
    art.ring(name + ".circle", (0, -.13, 0), h * .34, "silver", screen, .01, "XZ")
    markers = [art.sphere(name + ".player marker", (-w * .5 + i * w / 3, -.16, .1), .065,
                         color if i < 2 else "cyan", screen, 1) for i in range(4)]
    scan = art.tube(name + ".scan", [(-w, -.18, 0), (w, -.18, 0)], .012, color, screen)
    return screen, markers, scan


def review_sequence(root, shot):
    cam = camera("check.camera", root, (.4, -8, 3.4), (0, 0, 1.35), 52, 10.2)
    feeds = []
    for i, z in enumerate((1.1, 3.1)):
        feeds.append(monitor_feed(root, (0, 0, z), (3.0, 1.7), "orange" if i == 0 else "cyan", f"feed{i}"))
        art.rod("monitor support", (0, .12, z - .9), (0, .12, z + .9), .05, "ink", root)
        for j in range(3):
            art.box("status indicator", (-1.15 + j * .13, -.13, z - .70), (.07, .025, .025), "orange", root)
    for i in range(3):
        art.sphere("parallel review indicator", (-.4 + i * .4, -.12, 4.15), .075, "gold", root)
    for frame, t, seconds in sample(shot):
        for i, (_, markers, scan) in enumerate(feeds):
            for j, marker in enumerate(markers):
                key(marker, frame, location=(-.8 + j * .43 + math.sin(seconds * .9 + j) * .13,
                                            -.16, math.cos(seconds * .7 + j + i) * .32))
            key(scan, frame, location=(0, 0, math.sin(seconds * 1.5) * .55))
        move_camera(cam, frame, (.35 - .65 * t, -8 + .5 * t, 3.3), (0, 0, 1.65))
    return cam


def cultural_sequence(root, shot):
    # Cultural story beat: two supporters, shared pitch and football. No fake record,
    # screenshot, newspaper, or claim to be documentary evidence is generated.
    red = actor("culture.supporter.red", root, "red", "skin")
    blue = actor("culture.supporter.blue", root, "blue", "skin_dark")
    ball = moving_ball("culture.shared football", root)
    art.ring("shared field halo", (0, .4, .025), 1.8, "gold", root, .035)
    crown = art.empty("cultural coronation metaphor", (0, 1.4, 2.55), root)
    art.ring("crown base", (0, 0, 0), .42, "gold", crown, .05)
    for i in range(7):
        angle = i * math.tau / 7
        a, b = angle - .20, angle + .20
        art.mesh("crown point", [(.42 * math.cos(a), .42 * math.sin(a), 0),
                 (.42 * math.cos(b), .42 * math.sin(b), 0),
                 (.49 * math.cos(angle), .49 * math.sin(angle), .38)], [(0, 1, 2)], "gold", crown)
    cam = camera("evidence.camera", root, (.4, -6.8, 3.1), (0, .4, .65), 53, 7.4)
    for frame, t, seconds in sample(shot):
        art.pose(red, frame, (-.65, .4, 0), seconds, "stand", heading=-.22)
        art.pose(blue, frame, (.65, .4, 0), seconds + .8, "stand", heading=.22)
        key(ball, frame, location=(math.sin(t * math.pi) * .35, -.2, .17), rotation_euler=(0, t * 5, 0))
        key(crown, frame, rotation_euler=(0, .025 * math.sin(seconds * 1.6), seconds * .18))
        move_camera(cam, frame, (.7 - t * 1.4, -6.8 + .5 * t, 3.1), (0, .4, .65))
    return cam


def closing_sequence(root, shot):
    referee = actor("standard.referee", root, "gold", "skin_light")
    red = actor("standard.red", root, "red", "skin")
    blue = actor("standard.blue", root, "blue", "skin_dark")
    art.tube("equal field center", [(0, -2, .025), (0, 5, .025)], .035, "white", root)
    for side, color in ((-1, "orange"), (1, "cyan")):
        art.tube("equal field half", [(side * .10, -1.6, .03), (side * 3, -1.6, .03),
                                     (side * 3, 4.5, .03), (side * .10, 4.5, .03)], .032, color, root)
    art.sphere("referee.whistle", (.10, -.31, 1.74), (.045, .08, .032), "silver", referee["body"])
    cam = camera("close.camera", root, (.25, -5.6, 2.8), (0, 0, .8), 53, 7.3)
    for frame, t, seconds in sample(shot):
        art.pose(referee, frame, (0, -.45, 0), seconds, "whistle", heading=0)
        art.pose(red, frame, (-1.35, 1.6, 0), seconds + 1, "stand", heading=.2)
        art.pose(blue, frame, (1.35, 1.6, 0), seconds + 2, "stand", heading=-.2)
        move_camera(cam, frame, (.18 * math.sin(t * 2), -5.8 + .9 * t, 2.75), (0, -.15, .8))
    return cam


def configure(resolution):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.fps, scene.render.fps_base = FPS, 1.0
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.compression = 20
    scene.render.film_transparent = False
    scene.render.threads_mode, scene.render.threads = "FIXED", 4
    scene.render.use_file_extension = True
    scene.render.use_sequencer = False
    scene.world = bpy.data.worlds.new("purple night")
    scene.world.color = (.025, .020, .05)
    shade = scene.display.shading
    shade.light, shade.studio_light, shade.color_type = "FLAT", "paint.sl", "TEXTURE"
    shade.show_shadows = False
    shade.show_cavity = False
    shade.cavity_type = "BOTH"
    shade.curvature_ridge_factor, shade.curvature_valley_factor = 1.3, 1.0
    shade.cavity_ridge_factor, shade.cavity_valley_factor = 1.2, 1.2
    shade.show_specular_highlight = False
    shade.show_object_outline = True
    shade.object_outline_color = (.005, .004, .018)
    shade.background_type = "WORLD"
    scene.display.render_aa = "8"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure, scene.view_settings.gamma = 0, 1
    # Editable upgrade rig. Workbench itself uses its studio lighting.
    for name, location, color, energy in (("warm key", (-5, -4, 8), (1, .4, .2), 1100),
                                          ("cool rim", (5, 3, 7), (.2, .45, 1), 1400)):
        data = bpy.data.lights.new(name, "AREA")
        data.energy, data.color, data.shape, data.size = energy, color, "DISK", 5
        obj = bpy.data.objects.new(name, data)
        scene.collection.objects.link(obj)
        obj.location = location
    return scene


def add_cut(scene, shot, cam, frame, name):
    marker = scene.timeline_markers.new(name, frame=frame)
    marker.camera = cam
    CUTS.append({"scene": shot["id"], "name": name, "frame": frame,
                 "seconds": (frame - 1) / FPS, "camera": cam.name})


def insert_cameras(scene, root, shot):
    ident = shot["id"]
    if ident in ("hook", "egypt", "austria"):
        views = [(.34, "contact detail", (4.6, -3.3, 2.9), (.25, .75, .75), 6.1),
                 (.66, "goal reverse", (-2.2, -5.8, 3.9), (1.05, 1.5, .7), 7.7)]
    elif ident == "salah":
        views = [(.40, "possession reverse", (-4.3, -6, 3.8), (0, .65, .7), 7.3),
                 (.73, "possession high", (1.5, -5.8, 5), (0, .8, .65), 7.0)]
    elif ident == "draw":
        views = [(.52, "route emphasis", (.9, -10, 3.2), (0, 0, 1.4), 9.0)]
    elif ident == "check":
        views = [(.52, "parallel threshold", (-1.1, -8, 3.3), (0, 0, 1.65), 9.8)]
    elif ident == "evidence":
        views = [(.48, "rivalry reverse", (-1.5, -6.5, 3.2), (0, .5, .75), 7.0)]
    else:
        views = [(.38, "whistle detail", (.55, -5.7, 3.1), (0, .1, .8), 6.5),
                 (.73, "equal pitch", (-.4, -6.0, 4), (0, .8, .65), 7.8)]
    for fraction, label, position, target, scale in views:
        cam = camera(ident + "." + label, root, position, target, ortho=scale)
        for frame, t, _ in sample(shot):
            move_camera(cam, frame, Vector(position) + Vector((.3 * t, .2 * t, -.08 * t)), target)
        first = shot["first_frame"] + round((shot["last_frame"] - shot["first_frame"]) * fraction)
        add_cut(scene, shot, cam, first, ident + "." + label)


def embed_audio(scene, path):
    if path is None:
        return []
    if not path.is_file() or path.suffix.lower() not in (".wav", ".ogg"):
        raise ValueError("--audio requires an existing WAV or OGG")
    editor = scene.sequence_editor_create()
    strips = editor.strips if hasattr(editor, "strips") else editor.sequences
    strip = strips.new_sound("Final synchronized narration", str(path.resolve()), channel=1, frame_start=1)
    strip.sound.pack()
    strip.volume = 1.0
    scene.sync_mode = "AUDIO_SYNC"
    if abs(strip.frame_final_duration - scene.frame_end) > 2:
        raise ValueError("Narration duration does not match timeline within two frames")
    return [{"name": strip.name, "frame_start": strip.frame_start,
             "frame_duration": strip.frame_final_duration, "packed": bool(strip.sound.packed_file),
             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}]


def linear_interpolation():
    for obj in bpy.data.objects:
        if not obj.animation_data or not obj.animation_data.action:
            continue
        for curve in animation_compat.iter_action_curves(obj.animation_data.action):
            for point in curve.keyframe_points:
                point.interpolation = "LINEAR"


def inspect(scene, shots):
    report = {"fps": FPS, "frame_start": 1, "frame_end": scene.frame_end,
              "resolution": [scene.render.resolution_x, scene.render.resolution_y],
              "engine": scene.render.engine, "cuts": CUTS, "scenes": shots, "actors": [], "balls": [],
              "camera_motion": [], "assets_external": [], "editorial_status": "ILLUSTRATIVE",
              "limits": ["Anonymous illustrations, not exact incident replays",
                         "Segment articulation; no skin-weighted rig or full foot locking",
                         "Workbench flat authored cel lighting; area lights do not affect Workbench",
                         "No factual captions or copied reference footage in Blender"]}
    for item in ACTORS:
        root = item["root"]
        shot = next(s for s in shots if root.parent.name == "stage." + s["id"])
        frames = sorted({shot["first_frame"], (shot["first_frame"] + shot["last_frame"]) // 2, shot["last_frame"]})
        states = []
        for frame in frames:
            scene.frame_set(frame)
            feet = {}
            for side in ("L", "R"):
                foot = item[f"boot.{side}"]
                feet[side] = round(min((foot.matrix_world @ Vector(corner)).z for corner in foot.bound_box), 5)
            states.append({"frame": frame, "root_world": [round(v, 4) for v in root.matrix_world.translation],
                           "heading_z": round(root.rotation_euler.z, 4), "boot_min_z": feet,
                           "right_shin_rotation": [round(v, 4) for v in item["shin.R"].rotation_quaternion]})
        report["actors"].append({"name": root.name, "forward_local": "-Y", "states": states})
    for obj in BALLS:
        shot = next(s for s in shots if obj.parent.name == "stage." + s["id"])
        states = []
        for frame in (shot["first_frame"], (shot["first_frame"] + shot["last_frame"]) // 2, shot["last_frame"]):
            scene.frame_set(frame)
            states.append({"frame": frame, "location": [round(x, 4) for x in obj.location]})
        report["balls"].append({"name": obj.name, "states": states})
    for cam in CAMERAS:
        shot = next(s for s in shots if cam.parent.name == "stage." + s["id"])
        scene.frame_set(shot["first_frame"])
        start = cam.location.copy()
        scene.frame_set(shot["last_frame"])
        distance = (cam.location - start).length
        if distance < .05:
            raise RuntimeError(f"Camera {cam.name} does not move")
        report["camera_motion"].append({"name": cam.name, "translation_meters": round(distance, 4)})
    report["inventory"] = {kind: sum(obj.type == kind for obj in bpy.data.objects)
                           for kind in ("MESH", "CURVE", "EMPTY", "CAMERA", "LIGHT", "ARMATURE")}
    report["assets_external"] = [img.filepath for img in bpy.data.images if img.source == "FILE" and not img.packed_file]
    if report["assets_external"]:
        raise RuntimeError("Scene must pack image assets")
    penetrations = [(item["name"], state["frame"], state["boot_min_z"]) for item in report["actors"]
                    for state in item["states"] if min(state["boot_min_z"].values()) < -.025]
    if penetrations:
        raise RuntimeError(f"Feet penetrate ground: {penetrations}")
    return report


def main():
    options = arguments()
    timeline = load_timeline(options.timeline)
    if min(options.resolution) < 64 or max(options.resolution) > 7680:
        raise ValueError("Resolution must be between 64 and 7680 pixels")
    output = options.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    asset = Path(__file__).parent / "assets" / "rules-stadium.png"
    fingerprint = hashlib.sha256(options.timeline.read_bytes() + Path(__file__).read_bytes()
                                 + Path(art.__file__).read_bytes() + Path(animation_compat.__file__).read_bytes()
                                 + (asset.read_bytes() if asset.is_file() else b"")
                                 + json.dumps(list(options.resolution)).encode("ascii")
                                 + (options.audio.read_bytes() if options.audio else b"")).hexdigest()
    manifest = output / "build-manifest.json"
    if manifest.exists() and json.loads(manifest.read_text()).get("fingerprint") != fingerprint:
        raise ValueError("Source/timing changed; choose a fresh output directory")
    scene = configure(options.resolution)
    print("Building original stadium", flush=True)
    environment = art_collection()
    for index, source in enumerate(timeline["scenes"]):
        shot = {**source, "first_frame": round(source["start"] * FPS) + 1, "last_frame": round(source["end"] * FPS)}
        SHOTS.append(shot)
        root = stage(shot, index, environment)
        ident = shot["id"]
        if ident in ("hook", "egypt", "austria"):
            cam = field_sequence(root, shot, ident)
        elif ident == "draw":
            cam = bracket_sequence(root, shot)
        elif ident == "salah":
            cam = possession_sequence(root, shot)
        elif ident == "check":
            cam = review_sequence(root, shot)
        elif ident == "evidence":
            cam = cultural_sequence(root, shot)
        else:
            cam = closing_sequence(root, shot)
        add_cut(scene, shot, cam, shot["first_frame"], ident)
        insert_cameras(scene, root, shot)
        shot["camera"] = cam.name
        print("Built shot " + ident, flush=True)
    scene.frame_start, scene.frame_end = 1, SHOTS[-1]["last_frame"]
    scene.camera = CAMERAS[0]
    scene.render.filepath = str(output / "frame_")
    audio_report = embed_audio(scene, options.audio)
    linear_interpolation()
    bpy.ops.file.pack_all()
    report = inspect(scene, SHOTS)
    report["audio"] = audio_report
    (output / "motion-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    manifest.write_text(json.dumps({"fingerprint": fingerprint, "timeline": timeline,
        "source_files": [Path(__file__).name, Path(art.__file__).name, Path(animation_compat.__file__).name],
        "resolution": list(options.resolution)}, indent=2), encoding="utf-8")
    scene.frame_set(1)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.spaces.active.region_3d.view_perspective = "CAMERA"
                area.spaces.active.overlay.show_overlays = False
                area.spaces.active.show_gizmo = False
                # Rendered mode may reset to Solid when a blend is reopened.
                # Store the authored Workbench settings in Solid mode as well.
                viewport = area.spaces.active.shading
                viewport.type = "SOLID"
                for prop in ("light", "color_type", "show_shadows", "show_cavity",
                             "show_specular_highlight", "show_object_outline",
                             "object_outline_color", "background_type"):
                    setattr(viewport, prop, getattr(scene.display.shading, prop))
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "consistent-rules.blend"))
    if options.preview:
        preview = output / "preview"
        preview.mkdir(exist_ok=True)
        frames = options.frames or sorted({min(scene.frame_end, cut["frame"] + 15) for cut in CUTS})
        for frame in frames:
            if not 1 <= frame <= scene.frame_end:
                raise ValueError(f"Preview frame {frame} outside timeline")
            scene.frame_set(frame)
            scene.render.filepath = str(preview / f"frame_{frame:05d}.png")
            bpy.ops.render.render(write_still=True)
    if options.render:
        start, end = options.start_frame or 1, options.end_frame or scene.frame_end
        if not 1 <= start <= end <= scene.frame_end:
            raise ValueError("Invalid bounded render range")
        for frame in range(start, end + 1):
            scene.frame_set(frame)
            scene.render.filepath = str(output / f"frame_{frame:05d}.png")
            bpy.ops.render.render(write_still=True)
    print("RULES_SHORT_COMPLETE " + json.dumps({"output": str(output), "frames": scene.frame_end,
                                               "actors": len(ACTORS), "cameras": len(CAMERAS)}))


if __name__ == "__main__":
    main()
