#!/usr/bin/env python3
"""Stylized CR7 slide tackle animation built with Blender Python.

Run in Blender on macOS:
  /Applications/Blender.app/Contents/MacOS/Blender --python scripts/01_cr7_slide_tackle_siu.py

Optional render animation:
  /Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/01_cr7_slide_tackle_siu.py -- --render

This scene uses simple primitives only: no downloaded models required.
It creates a stadium, pitch, two stylized football figures, a slide tackle,
impact burst, Messi knockback, and CR7 celebration pose.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

FRAME_START = 1
FRAME_END = 180
FPS = 24
RENDER_ANIMATION = "--render" in sys.argv


def candidate_paths() -> list[Path]:
    """Collect real paths from terminal runs and Blender's Scripting tab."""
    paths: list[Path] = []

    script_name = "01_cr7_slide_tackle_siu.py"
    script_path = Path(globals().get("__file__", "")).expanduser()
    if script_path.name == script_name and len(script_path.parts) > 2:
        paths.append(script_path.resolve())

    for text_block in bpy.data.texts:
        if text_block.name == script_name and text_block.filepath:
            paths.append(Path(text_block.filepath).expanduser().resolve())

    current_text = getattr(getattr(bpy.context, "space_data", None), "text", None)
    if current_text and current_text.filepath:
        paths.append(Path(current_text.filepath).expanduser().resolve())

    cwd = Path.cwd().resolve()
    paths.extend([cwd / "scripts" / script_name, cwd / script_name])
    return paths


def project_root() -> Path:
    """Find the repo root, even when Blender sets __file__ to /script.py."""
    for script_path in candidate_paths():
        candidates = [script_path.parent, *script_path.parents]
        for candidate in candidates:
            if (candidate / "scripts" / "01_cr7_slide_tackle_siu.py").exists():
                return candidate

    return Path.home() / "blenderyt_outputs"


ROOT_DIR = project_root()
OUT_DIR = ROOT_DIR / "outputs" if ROOT_DIR.name != "blenderyt_outputs" else ROOT_DIR
OUT_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------------------------------------------------------
# Scene basics
# -----------------------------------------------------------------------------

def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def set_scene() -> None:
    scene = bpy.context.scene
    scene.frame_start = FRAME_START
    scene.frame_end = FRAME_END
    scene.frame_set(FRAME_START)
    scene.render.fps = FPS
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    engines = {item.identifier for item in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}
    scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines else "BLENDER_EEVEE"
    if hasattr(scene, "eevee"):
        scene.eevee.taa_render_samples = 64
        if hasattr(scene.eevee, "use_bloom"):
            scene.eevee.use_bloom = True
            scene.eevee.bloom_intensity = 0.08
        if hasattr(scene.eevee, "use_gtao"):
            scene.eevee.use_gtao = True
            scene.eevee.gtao_distance = 4
            scene.eevee.gtao_factor = 1.2
    scene.view_settings.view_transform = "Filmic"
    scene.view_settings.look = "Medium High Contrast"
    scene.render.filepath = str(OUT_DIR / "cr7_slide_tackle_siu_")


def make_mat(name: str, color: tuple[float, float, float, float], roughness: float = 0.45, metallic: float = 0.0) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = color
    if color[3] < 1:
        if hasattr(mat, "blend_method"):
            mat.blend_method = "BLEND"
        if hasattr(mat, "use_screen_refraction"):
            mat.use_screen_refraction = True
        if hasattr(mat, "show_transparent_back"):
            mat.show_transparent_back = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Alpha"].default_value = color[3]
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def assign(obj: bpy.types.Object, mat: bpy.types.Material) -> bpy.types.Object:
    obj.data.materials.append(mat)
    return obj


def key(obj: bpy.types.Object, frame: int, loc: bool = True, rot: bool = True, scale: bool = False) -> None:
    if loc:
        obj.keyframe_insert(data_path="location", frame=frame)
    if rot:
        obj.keyframe_insert(data_path="rotation_euler", frame=frame)
    if scale:
        obj.keyframe_insert(data_path="scale", frame=frame)


def set_interp(obj: bpy.types.Object) -> None:
    """Set smooth keyframes when Blender exposes F-curves; otherwise keep defaults."""
    action = getattr(getattr(obj, "animation_data", None), "action", None)
    if not action:
        return

    for fcurve in getattr(action, "fcurves", []):
        for point in getattr(fcurve, "keyframe_points", []):
            point.interpolation = "BEZIER"


# -----------------------------------------------------------------------------
# Geometry helpers
# -----------------------------------------------------------------------------

def add_cube(name: str, location, scale, mat: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(obj, mat)
    return obj


def add_uv_sphere(name: str, location, scale, mat: bpy.types.Material, segments: int = 32) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=16, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    assign(obj, mat)
    return obj


def add_cylinder(name: str, location, radius: float, depth: float, mat: bpy.types.Material, rotation=(0, 0, 0), vertices: int = 32) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    assign(obj, mat)
    return obj


def add_cone(name: str, location, radius1: float, radius2: float, depth: float, mat: bpy.types.Material, rotation=(0, 0, 0), vertices: int = 32) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius1, radius2=radius2, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    assign(obj, mat)
    return obj


def add_torus(name: str, location, major_radius: float, minor_radius: float, mat: bpy.types.Material, rotation=(0, 0, 0)) -> bpy.types.Object:
    bpy.ops.mesh.primitive_torus_add(major_radius=major_radius, minor_radius=minor_radius, major_segments=72, minor_segments=12, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    assign(obj, mat)
    return obj


def add_text(name: str, text: str, location, size: float, mat: bpy.types.Material, rotation=(math.radians(75), 0, 0)) -> bpy.types.Object:
    bpy.ops.object.text_add(location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.body = text
    obj.data.align_x = "CENTER"
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.extrude = 0.025
    assign(obj, mat)
    return obj


def parent_all(parent: bpy.types.Object, children: list[bpy.types.Object]) -> None:
    for child in children:
        child.parent = parent


def hide_key(obj: bpy.types.Object, frame: int, hidden: bool) -> None:
    obj.hide_viewport = hidden
    obj.hide_render = hidden
    obj.keyframe_insert(data_path="hide_viewport", frame=frame)
    obj.keyframe_insert(data_path="hide_render", frame=frame)


# -----------------------------------------------------------------------------
# Environment
# -----------------------------------------------------------------------------

def build_stadium(mats: dict[str, bpy.types.Material]) -> None:
    pitch = add_cube("Pitch deep green turf", (0, 0, -0.04), (20, 12, 0.08), mats["pitch"])
    line_mat = mats["line"]
    add_cube("Center line", (0, 0, 0.011), (0.045, 11.5, 0.02), line_mat)
    add_cube("Sideline left", (0, -5.8, 0.012), (20, 0.04, 0.02), line_mat)
    add_cube("Sideline right", (0, 5.8, 0.012), (20, 0.04, 0.02), line_mat)
    add_cube("End line near", (-9.8, 0, 0.012), (0.04, 11.5, 0.02), line_mat)
    add_cube("End line far", (9.8, 0, 0.012), (0.04, 11.5, 0.02), line_mat)

    # Stadium tiers as curved-looking stepped blocks.
    for side_y, label in [(-7.4, "A"), (7.4, "B")]:
        for tier in range(4):
            z = 0.35 + tier * 0.35
            width = 21.5 + tier * 1.3
            depth = 0.55
            block = add_cube(f"Stand {label} tier {tier+1}", (0, side_y + (tier * 0.35 if side_y > 0 else -tier * 0.35), z), (width, depth, 0.25), mats["stand"])
            block.rotation_euler[0] = math.radians(4 if side_y < 0 else -4)

    # Abstract crowd dots.
    crowd_colors = [mats["crowd_red"], mats["crowd_blue"], mats["crowd_gold"], mats["crowd_white"]]
    for side_y in [-7.15, 7.15]:
        for i in range(56):
            x = -9 + (i % 28) * 0.67
            row = i // 28
            z = 0.65 + row * 0.35
            y = side_y + (row * 0.25 if side_y > 0 else -row * 0.25)
            add_uv_sphere(f"Crowd dot {side_y} {i}", (x, y, z), (0.07, 0.07, 0.07), crowd_colors[i % len(crowd_colors)], segments=12)

    # LED board/banners make the stadium feel produced, not empty.
    for i, x in enumerate([-6.8, -3.2, 0.4, 4.0, 7.2]):
        board_mat = mats["crowd_red"] if i % 2 == 0 else mats["crowd_blue"]
        add_cube(f"Pitch LED board {i}", (x, -5.45, 0.28), (2.4, 0.08, 0.42), board_mat)

    add_text("Stadium Ronaldo banner", "RONALDO 7", (-4.8, -5.55, 0.58), 0.28, mats["gold"], rotation=(math.radians(78), 0, 0))
    add_text("Stadium Messi banner", "MESSI 10", (3.5, -5.55, 0.58), 0.28, mats["white"], rotation=(math.radians(78), 0, 0))

    # Goal silhouettes.
    for x in [-9.4, 9.4]:
        add_cube(f"Goal back {x}", (x, 0, 0.85), (0.06, 2.6, 1.7), mats["goal"])
        add_cube(f"Goal top {x}", (x, 0, 1.7), (0.08, 2.8, 0.06), mats["goal"])


def build_lighting_camera(mats: dict[str, bpy.types.Material]) -> bpy.types.Object:
    bpy.ops.object.light_add(type="AREA", location=(-3.5, -5, 7))
    key_light = bpy.context.object
    key_light.name = "Large stadium key light"
    key_light.data.energy = 850
    key_light.data.size = 6

    bpy.ops.object.light_add(type="AREA", location=(5, 4, 5))
    rim = bpy.context.object
    rim.name = "Cool rim light"
    rim.data.energy = 300
    rim.data.color = (0.55, 0.68, 1.0)
    rim.data.size = 5

    bpy.ops.object.camera_add(location=(-8.2, -8.2, 4.1), rotation=(math.radians(63), 0, math.radians(-43)))
    cam = bpy.context.object
    cam.name = "Cinematic tracking camera"
    cam.data.lens = 34
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = 5.6
    bpy.context.scene.camera = cam

    cam.location = (-8.2, -8.2, 4.1)
    cam.rotation_euler = (math.radians(63), 0, math.radians(-43))
    key(cam, 1)
    cam.location = (-4.2, -6.8, 3.4)
    cam.rotation_euler = (math.radians(61), 0, math.radians(-32))
    key(cam, 58)
    cam.location = (0.0, -7.4, 3.2)
    cam.rotation_euler = (math.radians(62), 0, math.radians(0))
    key(cam, 92)
    cam.location = (4.8, -6.2, 3.6)
    cam.rotation_euler = (math.radians(61), 0, math.radians(32))
    key(cam, 150)
    set_interp(cam)
    return cam


# -----------------------------------------------------------------------------
# Character construction
# -----------------------------------------------------------------------------

def make_player(name: str, mats: dict[str, bpy.types.Material], jersey: bpy.types.Material, shorts: bpy.types.Material, number: str, base_pose: str = "standing") -> bpy.types.Object:
    root = bpy.data.objects.new(f"{name} root", None)
    bpy.context.collection.objects.link(root)

    is_cr7 = "CR7" in name
    is_messi = "Messi" in name
    skin = mats["skin_cr7"] if is_cr7 else mats["skin_messi"]
    hair = mats["cr7_hair"] if is_cr7 else mats["messi_hair"]
    beard = mats["messi_beard"]
    black = mats["black"]
    white = mats["white"]
    sock = mats["cr7_sock"] if is_cr7 else mats["messi_sock"]
    boot = mats["boot_gold"] if is_cr7 else mats["boot_blue"]
    accent = mats["gold"] if is_cr7 else mats["argentina_sky"]
    display_name = "RONALDO" if is_cr7 else "MESSI"

    parts = []

    # Athletic body: wider shoulders, tapered torso, real socks/boots, and clear jersey identity.
    torso = add_cylinder(f"{name} torso", (0, -0.01, 1.28), 0.30, 0.86, jersey, vertices=48)
    torso.scale.x = 0.76
    chest = add_cube(f"{name} chest badge", (0, -0.255, 1.38), (0.18, 0.028, 0.16), accent)
    waist = add_cylinder(f"{name} waist", (0, 0, 0.83), 0.25, 0.24, shorts, vertices=48)
    collar = add_torus(f"{name} collar", (0, -0.01, 1.72), 0.165, 0.018, white, rotation=(math.radians(90), 0, 0))
    parts += [torso, chest, waist, collar]

    head = add_uv_sphere(f"{name} head", (0, -0.015, 1.9), (0.22, 0.20, 0.26), skin, segments=32)
    neck = add_cylinder(f"{name} neck", (0, 0, 1.64), 0.085, 0.18, skin, vertices=24)
    left_eye = add_uv_sphere(f"{name} left eye", (-0.07, -0.185, 1.93), (0.024, 0.012, 0.024), black, segments=12)
    right_eye = add_uv_sphere(f"{name} right eye", (0.07, -0.185, 1.93), (0.024, 0.012, 0.024), black, segments=12)
    brow = add_cube(f"{name} brow", (0, -0.198, 2.005), (0.18, 0.018, 0.018), hair)
    parts += [head, neck, left_eye, right_eye, brow]

    if is_cr7:
        hair_cap = add_uv_sphere(f"{name} sharp dark hair cap", (0, -0.02, 2.08), (0.205, 0.18, 0.085), hair, segments=24)
        quiff = add_cone(f"{name} front quiff", (0.03, -0.15, 2.17), 0.09, 0.015, 0.22, hair, rotation=(math.radians(62), 0, math.radians(-14)), vertices=20)
        jaw = add_cube(f"{name} sharp jaw shadow", (0, -0.19, 1.79), (0.18, 0.022, 0.035), mats["jaw_shadow"])
        parts += [hair_cap, quiff, jaw]
    else:
        hair_cap = add_uv_sphere(f"{name} rounded dark hair", (0, -0.01, 2.065), (0.22, 0.19, 0.09), hair, segments=24)
        side_hair_l = add_uv_sphere(f"{name} left side hair", (-0.18, -0.03, 1.95), (0.06, 0.04, 0.11), hair, segments=16)
        side_hair_r = add_uv_sphere(f"{name} right side hair", (0.18, -0.03, 1.95), (0.06, 0.04, 0.11), hair, segments=16)
        beard_mask = add_cube(f"{name} short beard", (0, -0.205, 1.79), (0.23, 0.024, 0.12), beard)
        parts += [hair_cap, side_hair_l, side_hair_r, beard_mask]

    # Segmented limbs make the poses read better than single sticks.
    left_sleeve = add_cylinder(f"{name} left sleeve", (-0.36, 0, 1.47), 0.075, 0.28, jersey, rotation=(0, math.radians(78), 0), vertices=24)
    right_sleeve = add_cylinder(f"{name} right sleeve", (0.36, 0, 1.47), 0.075, 0.28, jersey, rotation=(0, math.radians(-78), 0), vertices=24)
    left_arm = add_cylinder(f"{name} left forearm", (-0.54, 0, 1.18), 0.052, 0.54, skin, rotation=(0, math.radians(26), 0), vertices=24)
    right_arm = add_cylinder(f"{name} right forearm", (0.54, 0, 1.18), 0.052, 0.54, skin, rotation=(0, math.radians(-26), 0), vertices=24)
    left_hand = add_uv_sphere(f"{name} left hand", (-0.66, 0, 0.91), (0.07, 0.065, 0.07), skin, segments=16)
    right_hand = add_uv_sphere(f"{name} right hand", (0.66, 0, 0.91), (0.07, 0.065, 0.07), skin, segments=16)
    parts += [left_sleeve, right_sleeve, left_arm, right_arm, left_hand, right_hand]

    left_thigh = add_cylinder(f"{name} left thigh", (-0.13, 0, 0.58), 0.075, 0.50, skin, vertices=24)
    right_thigh = add_cylinder(f"{name} right thigh", (0.13, 0, 0.58), 0.075, 0.50, skin, vertices=24)
    left_sock = add_cylinder(f"{name} left sock", (-0.13, 0, 0.24), 0.069, 0.34, sock, vertices=24)
    right_sock = add_cylinder(f"{name} right sock", (0.13, 0, 0.24), 0.069, 0.34, sock, vertices=24)
    left_boot = add_cube(f"{name} left boot", (-0.13, -0.08, 0.045), (0.19, 0.42, 0.09), boot)
    right_boot = add_cube(f"{name} right boot", (0.13, -0.08, 0.045), (0.19, 0.42, 0.09), boot)
    parts += [left_thigh, right_thigh, left_sock, right_sock, left_boot, right_boot]

    for side, x in [("left", -0.13), ("right", 0.13)]:
        parts.append(add_cube(f"{name} {side} sock stripe", (x, -0.072, 0.37), (0.12, 0.018, 0.035), accent))

    label = add_text(f"{name} jersey number", number, (0, -0.32, 1.29), 0.29, white, rotation=(math.radians(90), 0, 0))
    name_tag = add_text(f"{name} name tag", display_name, (0, -0.326, 1.52), 0.105, white, rotation=(math.radians(90), 0, 0))
    parts += [label, name_tag]

    parent_all(root, parts)

    if base_pose == "celebrate":
        left_sleeve.rotation_euler = (0, math.radians(-58), math.radians(-15))
        right_sleeve.rotation_euler = (0, math.radians(58), math.radians(15))
        left_arm.rotation_euler = (0, math.radians(-77), math.radians(-10))
        right_arm.rotation_euler = (0, math.radians(77), math.radians(10))
        left_hand.location = (-0.86, -0.02, 1.7)
        right_hand.location = (0.86, -0.02, 1.7)
        left_thigh.rotation_euler = (math.radians(5), 0, math.radians(-5))
        right_thigh.rotation_euler = (math.radians(-5), 0, math.radians(5))

    return root

# -----------------------------------------------------------------------------
# Motion beats
# -----------------------------------------------------------------------------

def animate_cr7_slide(cr7: bpy.types.Object) -> None:
    cr7.location = (-9.0, -0.45, 0.0)
    cr7.rotation_euler = (0, 0, math.radians(86))
    key(cr7, 1)

    cr7.location = (-5.7, -0.2, 0.0)
    cr7.rotation_euler = (0, 0, math.radians(86))
    key(cr7, 32)

    cr7.location = (-2.3, 0.0, 0.02)
    cr7.rotation_euler = (math.radians(20), 0, math.radians(87))
    key(cr7, 54)

    cr7.location = (-0.35, 0.05, 0.02)
    cr7.rotation_euler = (math.radians(80), 0, math.radians(91))
    key(cr7, 74)

    cr7.location = (0.6, 0.16, 0.02)
    cr7.rotation_euler = (math.radians(78), 0, math.radians(91))
    key(cr7, 96)
    set_interp(cr7)


def animate_messi(messi: bpy.types.Object) -> None:
    messi.location = (0.8, 0.05, 0.0)
    messi.rotation_euler = (0, 0, math.radians(-88))
    key(messi, 1)
    key(messi, 58)

    messi.location = (1.15, 0.22, 0.25)
    messi.rotation_euler = (math.radians(-26), math.radians(12), math.radians(-92))
    key(messi, 78)

    messi.location = (2.35, 0.55, 0.9)
    messi.rotation_euler = (math.radians(-70), math.radians(5), math.radians(-124))
    key(messi, 98)

    messi.location = (3.6, 0.88, 0.12)
    messi.rotation_euler = (math.radians(-90), math.radians(0), math.radians(-138))
    key(messi, 126)
    set_interp(messi)


def animate_celebration(cr7_slide: bpy.types.Object, cr7_celebrate: bpy.types.Object) -> None:
    # Hide celebration version until impact sequence finishes.
    hide_key(cr7_celebrate, 1, True)
    hide_key(cr7_celebrate, 108, True)
    hide_key(cr7_celebrate, 112, False)

    hide_key(cr7_slide, 1, False)
    hide_key(cr7_slide, 108, False)
    hide_key(cr7_slide, 112, True)

    cr7_celebrate.location = (2.2, -0.2, 0.0)
    cr7_celebrate.rotation_euler = (0, 0, math.radians(78))
    key(cr7_celebrate, 112)

    cr7_celebrate.location = (2.5, -0.2, 0.8)
    cr7_celebrate.rotation_euler = (0, 0, math.radians(78))
    key(cr7_celebrate, 132)

    cr7_celebrate.location = (2.8, -0.2, 0.0)
    cr7_celebrate.rotation_euler = (0, 0, math.radians(258))
    key(cr7_celebrate, 154)

    cr7_celebrate.location = (3.05, -0.2, 0.0)
    cr7_celebrate.rotation_euler = (0, 0, math.radians(258))
    key(cr7_celebrate, 180)
    set_interp(cr7_celebrate)


def pose_part(name: str, frame: int, rotation=None, location=None, scale=None) -> None:
    obj = bpy.data.objects.get(name)
    if not obj:
        return
    if rotation is not None:
        obj.rotation_euler = rotation
        obj.keyframe_insert(data_path="rotation_euler", frame=frame)
    if location is not None:
        obj.location = location
        obj.keyframe_insert(data_path="location", frame=frame)
    if scale is not None:
        obj.scale = scale
        obj.keyframe_insert(data_path="scale", frame=frame)
    set_interp(obj)


def animate_character_details() -> None:
    # CR7 body language: sprint arms, body drop, slide extension.
    for prefix in ["CR7 slide"]:
        pose_part(f"{prefix} left forearm", 1, rotation=(0, math.radians(38), math.radians(8)))
        pose_part(f"{prefix} right forearm", 1, rotation=(0, math.radians(-42), math.radians(-8)))
        pose_part(f"{prefix} left forearm", 54, rotation=(0, math.radians(-72), math.radians(-18)))
        pose_part(f"{prefix} right forearm", 54, rotation=(0, math.radians(52), math.radians(16)))
        pose_part(f"{prefix} left thigh", 74, rotation=(math.radians(88), 0, math.radians(-8)))
        pose_part(f"{prefix} right thigh", 74, rotation=(math.radians(-54), 0, math.radians(8)))
        pose_part(f"{prefix} left boot", 74, location=(-0.28, -0.30, 0.05), rotation=(0, 0, math.radians(-7)))
        pose_part(f"{prefix} right boot", 74, location=(0.28, 0.14, 0.05), rotation=(0, 0, math.radians(8)))
        pose_part(f"{prefix} sharp dark hair cap", 54, scale=(0.22, 0.19, 0.09))
        pose_part(f"{prefix} front quiff", 74, rotation=(math.radians(77), 0, math.radians(-22)))

    # Messi reacts: arms open and body curls during the launch.
    prefix = "Messi"
    pose_part(f"{prefix} left forearm", 58, rotation=(0, math.radians(25), math.radians(4)))
    pose_part(f"{prefix} right forearm", 58, rotation=(0, math.radians(-25), math.radians(-4)))
    pose_part(f"{prefix} left forearm", 78, rotation=(math.radians(35), math.radians(-70), math.radians(-36)))
    pose_part(f"{prefix} right forearm", 78, rotation=(math.radians(-35), math.radians(70), math.radians(36)))
    pose_part(f"{prefix} left thigh", 98, rotation=(math.radians(-50), 0, math.radians(-26)))
    pose_part(f"{prefix} right thigh", 98, rotation=(math.radians(62), 0, math.radians(34)))
    pose_part(f"{prefix} rounded dark hair", 98, scale=(0.24, 0.20, 0.10))

    # Siu pose: arms wide on landing, slight head lift.
    prefix = "CR7 celebrate"
    pose_part(f"{prefix} left forearm", 112, rotation=(0, math.radians(-60), math.radians(-18)))
    pose_part(f"{prefix} right forearm", 112, rotation=(0, math.radians(60), math.radians(18)))
    pose_part(f"{prefix} left forearm", 154, rotation=(0, math.radians(-88), math.radians(-10)))
    pose_part(f"{prefix} right forearm", 154, rotation=(0, math.radians(88), math.radians(10)))
    pose_part(f"{prefix} head", 154, rotation=(math.radians(-10), 0, 0))


def build_effects(mats: dict[str, bpy.types.Material]) -> None:
    # Entrance glow so CR7 does not just appear from a blank edge.
    portal = add_torus("CR7 entrance tunnel glow", (-8.65, -0.45, 1.0), 0.78, 0.035, mats["portal"], rotation=(math.radians(90), 0, 0))
    portal.scale = (0.2, 0.2, 0.2)
    key(portal, 1, loc=False, rot=False, scale=True)
    portal.scale = (1.15, 1.15, 1.15)
    key(portal, 18, loc=False, rot=False, scale=True)
    portal.scale = (0.05, 0.05, 0.05)
    key(portal, 48, loc=False, rot=False, scale=True)

    for i in range(5):
        ring = add_torus(f"CR7 entrance ripple {i}", (-8.65 + i * 0.09, -0.45, 1.0), 0.38 + i * 0.16, 0.012, mats["trail"], rotation=(math.radians(90), 0, 0))
        ring.scale = (0.01, 0.01, 0.01)
        key(ring, 1 + i * 3, loc=False, rot=False, scale=True)
        ring.scale = (1.0, 1.0, 1.0)
        key(ring, 22 + i * 3, loc=False, rot=False, scale=True)
        ring.scale = (0.01, 0.01, 0.01)
        key(ring, 42 + i * 3, loc=False, rot=False, scale=True)

    # Football starts near Messi, pops during the impact, then spins out.
    ball = add_uv_sphere("Football with spin", (0.55, -0.24, 0.22), (0.13, 0.13, 0.13), mats["white"], segments=32)
    for i, (dx, dz) in enumerate([(0, 0.12), (0.1, 0), (-0.1, 0), (0.06, -0.09), (-0.06, -0.09)]):
        patch = add_cube(f"Football black patch {i}", (0.55 + dx, -0.36, 0.22 + dz), (0.055, 0.012, 0.055), mats["black"])
        patch.parent = ball
    ball.location = (0.55, -0.24, 0.22)
    ball.rotation_euler = (0, 0, 0)
    key(ball, 1)
    key(ball, 68)
    ball.location = (1.1, 0.2, 0.55)
    ball.rotation_euler = (math.radians(260), math.radians(180), math.radians(90))
    key(ball, 84)
    ball.location = (2.8, 1.05, 0.42)
    ball.rotation_euler = (math.radians(720), math.radians(380), math.radians(210))
    key(ball, 122)
    set_interp(ball)

    for i in range(7):
        dust = add_uv_sphere(f"Slide grass dust {i}", (-0.8 + i * 0.28, -0.05 + i * 0.035, 0.08), (0.08, 0.035, 0.035), mats["dust"], segments=12)
        dust.scale = (0.01, 0.01, 0.01)
        key(dust, 52 + i, loc=False, rot=False, scale=True)
        dust.scale = (1.6, 0.7, 0.5)
        key(dust, 76 + i, loc=False, rot=False, scale=True)
        dust.scale = (0.01, 0.01, 0.01)
        key(dust, 106 + i, loc=False, rot=False, scale=True)

    # Speed streaks behind CR7.
    for i in range(12):
        x = -8.2 + i * 0.62
        streak = add_cube(f"CR7 speed streak {i}", (x, -0.52, 0.34 + (i % 3) * 0.045), (0.95, 0.035, 0.035), mats["trail"])
        streak.rotation_euler[2] = math.radians(6)
        hide_key(streak, 1, False)
        hide_key(streak, 74, False)
        hide_key(streak, 96, True)

    # Impact burst at tackle frame.
    for i in range(14):
        angle = (math.tau / 14) * i
        spark = add_cube(f"Impact shard {i}", (0.63 + math.cos(angle) * 0.16, 0.16 + math.sin(angle) * 0.16, 0.38), (0.05, 0.32, 0.05), mats["impact"])
        spark.rotation_euler = (math.radians(90), 0, angle)
        spark.scale = (0.2, 0.2, 0.2)
        key(spark, 68, loc=False, rot=False, scale=True)
        spark.scale = (1.3, 1.3, 1.3)
        key(spark, 82, loc=False, rot=False, scale=True)
        spark.scale = (0.01, 0.01, 0.01)
        key(spark, 102, loc=False, rot=False, scale=True)
        hide_key(spark, 1, True)
        hide_key(spark, 66, True)
        hide_key(spark, 68, False)
        hide_key(spark, 104, True)

    add_text("SUI celebration text", "SIIIU", (3.25, -0.75, 2.0), 0.55, mats["gold"], rotation=(math.radians(68), 0, math.radians(18)))
    text_obj = bpy.data.objects["SUI celebration text"]
    text_obj.scale = (0.01, 0.01, 0.01)
    key(text_obj, 112, loc=False, rot=False, scale=True)
    text_obj.scale = (1, 1, 1)
    key(text_obj, 152, loc=False, rot=False, scale=True)


def finish_timeline() -> None:
    scene = bpy.context.scene
    scene.timeline_markers.clear()
    for name, frame in [
        ("CR7 enters", 1),
        ("Slide starts", 54),
        ("Impact", 74),
        ("Messi launch", 98),
        ("Siu jump", 132),
        ("Siu landing", 154),
    ]:
        scene.timeline_markers.new(name, frame=frame)

    scene.frame_start = FRAME_START
    scene.frame_end = FRAME_END
    scene.frame_set(FRAME_START)

    for area in bpy.context.screen.areas if bpy.context.screen else []:
        if area.type == "VIEW_3D":
            region = next((r for r in area.regions if r.type == "WINDOW"), None)
            space = next((s for s in area.spaces if s.type == "VIEW_3D"), None)
            if region and space:
                override = {"area": area, "region": region, "space_data": space}
                with bpy.context.temp_override(**override):
                    bpy.ops.view3d.view_camera()
            break

    if not RENDER_ANIMATION and bpy.context.screen:
        try:
            bpy.ops.screen.animation_play()
        except RuntimeError:
            pass


def build_scene() -> None:
    clear_scene()
    set_scene()

    mats = {
        "pitch": make_mat("Pitch green", (0.03, 0.28, 0.09, 1)),
        "line": make_mat("Painted white line", (0.95, 0.95, 0.88, 1)),
        "stand": make_mat("Concrete stand", (0.12, 0.13, 0.16, 1)),
        "crowd_red": make_mat("Crowd red", (0.75, 0.08, 0.08, 1)),
        "crowd_blue": make_mat("Crowd blue", (0.05, 0.18, 0.82, 1)),
        "crowd_gold": make_mat("Crowd gold", (1.0, 0.74, 0.18, 1)),
        "crowd_white": make_mat("Crowd white", (0.9, 0.9, 0.9, 1)),
        "goal": make_mat("Goal metal", (0.88, 0.9, 0.92, 1), metallic=0.25),
        "skin": make_mat("Stylized skin", (0.78, 0.52, 0.34, 1)),
        "skin_cr7": make_mat("CR7 warmer skin", (0.77, 0.51, 0.34, 1)),
        "skin_messi": make_mat("Messi lighter skin", (0.82, 0.58, 0.40, 1)),
        "black": make_mat("Black detail", (0.01, 0.01, 0.012, 1)),
        "white": make_mat("White detail", (1, 1, 1, 1)),
        "jaw_shadow": make_mat("CR7 jaw shadow", (0.18, 0.10, 0.06, 1)),
        "cr7_hair": make_mat("CR7 dark quiff hair", (0.018, 0.014, 0.012, 1)),
        "messi_hair": make_mat("Messi brown hair", (0.11, 0.055, 0.025, 1)),
        "messi_beard": make_mat("Messi beard", (0.13, 0.065, 0.03, 1)),
        "boot": make_mat("Boot black", (0.01, 0.012, 0.015, 1)),
        "boot_gold": make_mat("CR7 gold boots", (1.0, 0.72, 0.10, 1), metallic=0.15),
        "boot_blue": make_mat("Messi blue boots", (0.05, 0.42, 1.0, 1), metallic=0.1),
        "cr7_red": make_mat("CR7 red jersey", (0.82, 0.02, 0.04, 1)),
        "cr7_white": make_mat("CR7 white shorts", (0.92, 0.92, 0.88, 1)),
        "cr7_sock": make_mat("CR7 black socks", (0.02, 0.02, 0.025, 1)),
        "messi_blue": make_mat("Messi blue jersey", (0.02, 0.16, 0.72, 1)),
        "messi_dark": make_mat("Messi dark shorts", (0.015, 0.02, 0.08, 1)),
        "messi_sock": make_mat("Messi white socks", (0.92, 0.95, 1.0, 1)),
        "argentina_sky": make_mat("Argentina sky accent", (0.40, 0.78, 1.0, 1)),
        "trail": make_mat("Motion trail", (1.0, 0.95, 0.25, 0.38)),
        "trail_blue": make_mat("Blue spin trail", (0.25, 0.68, 1.0, 0.38)),
        "impact": make_mat("Impact neon", (1.0, 0.68, 0.04, 1)),
        "portal": make_mat("Entrance tunnel glow", (0.9, 0.08, 0.05, 0.45)),
        "dust": make_mat("Grass dust", (0.82, 0.9, 0.52, 0.42)),
        "gold": make_mat("Siu gold", (1.0, 0.75, 0.08, 1), metallic=0.2),
    }

    build_stadium(mats)
    camera = build_lighting_camera(mats)

    cr7_slide = make_player("CR7 slide", mats, mats["cr7_red"], mats["cr7_white"], "7")
    cr7_celebrate = make_player("CR7 celebrate", mats, mats["cr7_red"], mats["cr7_white"], "7", base_pose="celebrate")
    messi = make_player("Messi", mats, mats["messi_blue"], mats["messi_dark"], "10")

    animate_cr7_slide(cr7_slide)
    animate_messi(messi)
    animate_celebration(cr7_slide, cr7_celebrate)
    animate_character_details()
    build_effects(mats)

    # Character name plates.
    cr7_label = add_text("CR7 name plate", "CR7", (-3.8, -1.0, 0.04), 0.32, mats["gold"], rotation=(math.radians(90), 0, 0))
    messi_label = add_text("Messi name plate", "MESSI", (1.4, 1.05, 0.04), 0.26, mats["white"], rotation=(math.radians(90), 0, 0))

    # Focus camera depth of field near action.
    empty = bpy.data.objects.new("Camera focus action point", None)
    bpy.context.collection.objects.link(empty)
    empty.location = (0.7, 0.1, 0.65)
    camera.data.dof.focus_object = empty

    finish_timeline()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_DIR / "cr7_slide_tackle_siu.blend"))

    if RENDER_ANIMATION:
        bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    build_scene()
