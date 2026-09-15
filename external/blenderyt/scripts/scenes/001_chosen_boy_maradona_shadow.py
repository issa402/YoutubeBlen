#!/usr/bin/env python3
"""Cold-open beat: Messi myth / Maradona shadow visual.

Run in Blender:
  blender --python scripts/scenes/001_chosen_boy_maradona_shadow.py

Optional render:
  blender --background --python scripts/scenes/001_chosen_boy_maradona_shadow.py -- --render

This creates the 00:11-00:18 visual beat from the first video:
- a small Messi-like silhouette walks onto a dark pitch
- a massive legendary shadow grows behind him
- projectors labeled MEDIA, BARCA, ARGENTINA, LEGACY switch on
- the words THE HEIR, THE MYTH, THE BUSINESS stamp into frame

No external models are required. Everything is generated with Blender primitives.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

FRAME_START = 1
FRAME_END = 168
FPS = 24
RENDER_ANIMATION = "--render" in sys.argv
SCRIPT_NAME = "001_chosen_boy_maradona_shadow.py"


def candidate_paths() -> list[Path]:
    """Find the script path from terminal runs or Blender's text editor."""
    paths: list[Path] = []
    file_path = Path(globals().get("__file__", "")).expanduser()
    if file_path.name == SCRIPT_NAME and len(file_path.parts) > 2:
        paths.append(file_path.resolve())

    for text_block in bpy.data.texts:
        if text_block.name == SCRIPT_NAME and text_block.filepath:
            paths.append(Path(text_block.filepath).expanduser().resolve())

    cwd = Path.cwd().resolve()
    paths.extend([cwd / "scripts" / "scenes" / SCRIPT_NAME, cwd / SCRIPT_NAME])
    return paths


def project_root() -> Path:
    """Find repo root even when Blender gives odd __file__ paths."""
    for script_path in candidate_paths():
        for candidate in [script_path.parent, *script_path.parents]:
            if (candidate / "README.md").exists() and (candidate / "scripts").exists():
                return candidate
    return Path.home() / "blenderyt_outputs"


ROOT_DIR = project_root()
OUT_DIR = ROOT_DIR / "outputs" if ROOT_DIR.name != "blenderyt_outputs" else ROOT_DIR
OUT_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------------------------------------------------------
# Core scene helpers
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
    scene.render.filepath = str(OUT_DIR / "chosen_boy_maradona_shadow_")

    engines = {item.identifier for item in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}
    scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines else "BLENDER_EEVEE"

    if hasattr(scene, "eevee"):
        if hasattr(scene.eevee, "taa_render_samples"):
            scene.eevee.taa_render_samples = 64
        if hasattr(scene.eevee, "use_bloom"):
            scene.eevee.use_bloom = True
            scene.eevee.bloom_intensity = 0.13
        if hasattr(scene.eevee, "use_gtao"):
            scene.eevee.use_gtao = True
            scene.eevee.gtao_distance = 4
            scene.eevee.gtao_factor = 1.3

    scene.view_settings.view_transform = "Filmic"
    scene.view_settings.look = "Medium High Contrast"
    if hasattr(scene.render, "use_freestyle"):
        scene.render.use_freestyle = True
        try:
            scene.view_layers[0].freestyle_settings.linesets[0].linestyle.thickness = 2.2
        except Exception:
            pass


def make_mat(
    name: str,
    color: tuple[float, float, float, float],
    emission: tuple[float, float, float, float] | None = None,
    strength: float = 0.0,
    roughness: float = 0.55,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = color

    if color[3] < 1:
        if hasattr(mat, "blend_method"):
            mat.blend_method = "BLEND"
        if hasattr(mat, "show_transparent_back"):
            mat.show_transparent_back = False

    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Alpha"].default_value = color[3]
        bsdf.inputs["Roughness"].default_value = roughness
        if emission and "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = emission
            bsdf.inputs["Emission Strength"].default_value = strength
        elif emission and "Emission" in bsdf.inputs:
            bsdf.inputs["Emission"].default_value = emission

    return mat


def assign(obj: bpy.types.Object, mat: bpy.types.Material) -> bpy.types.Object:
    obj.data.materials.append(mat)
    return obj


def key(obj: bpy.types.Object, frame: int, loc: bool = True, rot: bool = True, scale: bool = True) -> None:
    if loc:
        obj.keyframe_insert(data_path="location", frame=frame)
    if rot:
        obj.keyframe_insert(data_path="rotation_euler", frame=frame)
    if scale:
        obj.keyframe_insert(data_path="scale", frame=frame)


def iter_action_fcurves(action):
    """Yield F-curves across Blender action API versions."""
    fcurves = getattr(action, "fcurves", None)
    if fcurves is not None:
        yield from fcurves
        return

    for layer in getattr(action, "layers", []):
        for strip in getattr(layer, "strips", []):
            channelbag = getattr(strip, "channelbag", None)
            if channelbag is None:
                continue
            yield from getattr(channelbag, "fcurves", [])


def set_interp(obj: bpy.types.Object, interpolation: str = "BEZIER") -> None:
    action = getattr(getattr(obj, "animation_data", None), "action", None)
    if not action:
        return

    for fcurve in iter_action_fcurves(action):
        for point in getattr(fcurve, "keyframe_points", []):
            point.interpolation = interpolation


def animate_visibility(obj: bpy.types.Object, visible_frame: int, hidden_before: bool = True) -> None:
    obj.hide_viewport = hidden_before
    obj.hide_render = hidden_before
    obj.keyframe_insert(data_path="hide_viewport", frame=max(FRAME_START, visible_frame - 1))
    obj.keyframe_insert(data_path="hide_render", frame=max(FRAME_START, visible_frame - 1))

    obj.hide_viewport = False
    obj.hide_render = False
    obj.keyframe_insert(data_path="hide_viewport", frame=visible_frame)
    obj.keyframe_insert(data_path="hide_render", frame=visible_frame)


def add_cube(name: str, location, scale, mat: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return assign(obj, mat)


def add_sphere(name: str, location, scale, mat: bpy.types.Material, segments: int = 32) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=16, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    return assign(obj, mat)


def add_cylinder(name: str, location, radius: float, depth: float, mat: bpy.types.Material, rotation=(0, 0, 0), vertices: int = 32) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    return assign(obj, mat)


def add_text(
    name: str,
    body: str,
    location,
    size: float,
    mat: bpy.types.Material,
    rotation=(math.radians(70), 0, 0),
    align="CENTER",
) -> bpy.types.Object:
    bpy.ops.object.text_add(location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.body = body
    obj.data.align_x = align
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.extrude = 0.018
    return assign(obj, mat)


def parent_all(parent: bpy.types.Object, children: list[bpy.types.Object]) -> None:
    for child in children:
        child.parent = parent


# -----------------------------------------------------------------------------
# Scene objects
# -----------------------------------------------------------------------------

def build_materials() -> dict[str, bpy.types.Material]:
    return {
        "black": make_mat("ink black", (0.015, 0.014, 0.017, 1)),
        "pitch": make_mat("deep pitch green", (0.02, 0.13, 0.075, 1)),
        "line": make_mat("chalk white", (0.92, 0.9, 0.82, 1), emission=(0.9, 0.86, 0.65, 1), strength=0.12),
        "arg_blue": make_mat("argentina blue glow", (0.11, 0.48, 0.92, 1), emission=(0.08, 0.35, 0.9, 1), strength=0.9),
        "barca_red": make_mat("barca red glow", (0.72, 0.03, 0.12, 1), emission=(0.72, 0.03, 0.1, 1), strength=0.85),
        "barca_blue": make_mat("barca blue glow", (0.03, 0.07, 0.45, 1), emission=(0.02, 0.05, 0.5, 1), strength=0.8),
        "gold": make_mat("myth gold", (1.0, 0.68, 0.12, 1), emission=(1.0, 0.45, 0.08, 1), strength=0.7),
        "paper": make_mat("warm evidence paper", (0.86, 0.76, 0.55, 1)),
        "red_light": make_mat("alarm red", (1.0, 0.05, 0.03, 1), emission=(1.0, 0.0, 0.0, 1), strength=1.4),
        "beam_blue": make_mat("transparent blue beam", (0.15, 0.55, 1.0, 0.28), emission=(0.12, 0.45, 1.0, 1), strength=0.5),
        "beam_red": make_mat("transparent red beam", (1.0, 0.08, 0.08, 0.24), emission=(1.0, 0.02, 0.02, 1), strength=0.5),
        "shadow": make_mat("giant myth shadow", (0.0, 0.0, 0.0, 0.55)),
        "white_glow": make_mat("white glow", (1.0, 0.96, 0.78, 1), emission=(1.0, 0.9, 0.58, 1), strength=0.9),
    }


def build_pitch(mats: dict[str, bpy.types.Material]) -> None:
    add_cube("Dark pitch floor", (0, 0, -0.05), (18, 10, 0.1), mats["pitch"])
    add_cube("Center chalk line", (0, 0, 0.015), (0.05, 9.2, 0.03), mats["line"])
    add_cube("Left touchline", (0, -4.6, 0.018), (18, 0.045, 0.03), mats["line"])
    add_cube("Right touchline", (0, 4.6, 0.018), (18, 0.045, 0.03), mats["line"])
    add_cube("Back evidence wall", (3.1, 4.85, 2.4), (14.2, 0.16, 4.8), mats["black"])

    for x in [-5.4, -2.7, 0, 2.7, 5.4]:
        add_cube(f"floor light strip {x}", (x, -4.2, 0.03), (1.1, 0.055, 0.025), mats["gold"])


def make_simple_player(name: str, mats: dict[str, bpy.types.Material], location=(-2.2, 0, 0)) -> bpy.types.Object:
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    root.location = location

    skin = mats["white_glow"]
    kit = mats["arg_blue"]
    dark = mats["black"]

    parts = [
        add_sphere(f"{name} head", (0, 0, 1.9), (0.22, 0.19, 0.24), skin, segments=24),
        add_cube(f"{name} torso", (0, 0, 1.28), (0.5, 0.24, 0.82), kit),
        add_cylinder(f"{name} left leg", (-0.16, 0, 0.56), 0.07, 0.9, kit, rotation=(0.0, math.radians(8), 0)),
        add_cylinder(f"{name} right leg", (0.16, 0, 0.56), 0.07, 0.9, kit, rotation=(0.0, math.radians(-8), 0)),
        add_cylinder(f"{name} left arm", (-0.36, 0, 1.25), 0.045, 0.72, kit, rotation=(0.0, math.radians(24), 0)),
        add_cylinder(f"{name} right arm", (0.36, 0, 1.25), 0.045, 0.72, kit, rotation=(0.0, math.radians(-24), 0)),
        add_cube(f"{name} hair", (0, 0, 2.12), (0.34, 0.22, 0.13), dark),
        add_text(f"{name} shirt number", "10", (0, -0.135, 1.35), 0.28, mats["white_glow"], rotation=(math.radians(90), 0, 0)),
    ]
    parent_all(root, parts)
    return root


def make_giant_shadow(name: str, mats: dict[str, bpy.types.Material]) -> bpy.types.Object:
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    root.location = (0.85, 4.73, 1.8)
    root.rotation_euler = (math.radians(90), 0, 0)
    root.scale = (0.25, 0.25, 0.25)

    mat = mats["shadow"]
    parts = [
        add_sphere(f"{name} head shadow", (0, 0, 0.85), (0.38, 0.08, 0.38), mat, segments=24),
        add_cube(f"{name} chest shadow", (0, 0, 0.1), (0.74, 0.05, 1.0), mat),
        add_cylinder(f"{name} left arm shadow", (-0.55, 0, 0.18), 0.06, 1.05, mat, rotation=(0, math.radians(25), 0)),
        add_cylinder(f"{name} right arm shadow", (0.55, 0, 0.18), 0.06, 1.05, mat, rotation=(0, math.radians(-25), 0)),
        add_cylinder(f"{name} left leg shadow", (-0.23, 0, -0.85), 0.08, 1.1, mat, rotation=(0, math.radians(9), 0)),
        add_cylinder(f"{name} right leg shadow", (0.23, 0, -0.85), 0.08, 1.1, mat, rotation=(0, math.radians(-9), 0)),
    ]
    parent_all(root, parts)
    return root


def make_projector(name: str, label: str, location, target, mat_body, mat_beam) -> bpy.types.Object:
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    root.location = location

    body = add_cylinder(f"{name} body", (0, 0, 0), 0.18, 0.36, mat_body, rotation=(math.radians(90), 0, 0), vertices=24)
    lens = add_sphere(f"{name} lens", (0, -0.2, 0), (0.15, 0.04, 0.15), mat_beam, segments=16)
    beam = add_cylinder(f"{name} beam", (0, -1.25, 0), 0.11, 2.45, mat_beam, rotation=(math.radians(90), 0, 0), vertices=32)
    beam.scale.x = 1.6
    beam.scale.z = 0.7
    text = add_text(f"{name} label", label, (0, 0.35, 0.32), 0.18, mat_body, rotation=(math.radians(70), 0, 0))

    parent_all(root, [body, lens, beam, text])

    direction = Vector(target) - Vector(location)
    root.rotation_euler = direction.to_track_quat("-Y", "Z").to_euler()
    return root


def build_projectors(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    specs = [
        ("Projector MEDIA", "MEDIA", (-5.4, -3.5, 1.1), (0.6, 4.8, 2.6), mats["gold"], mats["beam_blue"]),
        ("Projector BARCA", "BARCA", (-2.2, -3.8, 0.95), (0.8, 4.8, 2.2), mats["barca_red"], mats["beam_red"]),
        ("Projector ARGENTINA", "ARGENTINA", (2.0, -3.8, 1.0), (0.9, 4.8, 2.5), mats["arg_blue"], mats["beam_blue"]),
        ("Projector LEGACY", "LEGACY", (5.3, -3.4, 1.15), (0.9, 4.8, 2.9), mats["white_glow"], mats["beam_blue"]),
    ]
    projectors = [make_projector(*spec) for spec in specs]
    for i, projector in enumerate(projectors):
        animate_visibility(projector, 22 + i * 16)
        projector.scale = (0.8, 0.8, 0.8)
        key(projector, 22 + i * 16, loc=False, rot=False, scale=True)
        projector.scale = (1.04, 1.04, 1.04)
        key(projector, 27 + i * 16, loc=False, rot=False, scale=True)
        set_interp(projector)
    return projectors


def build_evidence_cards(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    cards = []
    labels = [
        ("THE HEIR", (-4.4, 4.64, 3.25), mats["gold"], 76),
        ("THE MYTH", (-1.25, 4.63, 3.55), mats["arg_blue"], 94),
        ("THE BUSINESS", (2.5, 4.62, 3.15), mats["barca_red"], 112),
        ("THE SEQUEL", (5.2, 4.61, 2.72), mats["white_glow"], 130),
    ]
    for label, loc, text_mat, frame in labels:
        card = add_cube(f"Evidence card {label}", loc, (2.4, 0.06, 0.74), mats["paper"])
        text = add_text(f"Evidence text {label}", label, (loc[0], loc[1] - 0.055, loc[2] + 0.02), 0.24, text_mat, rotation=(math.radians(90), 0, 0))
        for obj in [card, text]:
            animate_visibility(obj, frame)
            obj.scale = (1.35, 1.35, 1.35)
            key(obj, frame, loc=False, rot=False, scale=True)
            obj.scale = (1.0, 1.0, 1.0)
            key(obj, frame + 8, loc=False, rot=False, scale=True)
            set_interp(obj)
            cards.append(obj)
    return cards


def build_maradona_shadow_scene(mats: dict[str, bpy.types.Material]) -> None:
    player = make_simple_player("Chosen boy silhouette", mats, location=(-3.2, -0.25, 0))
    shadow = make_giant_shadow("Legend shadow", mats)

    # Player walks into frame and becomes small against the projected myth.
    player.location = (-4.0, -0.35, 0)
    key(player, 1)
    player.location = (-2.25, -0.08, 0)
    player.rotation_euler[2] = math.radians(-3)
    key(player, 58)
    player.location = (-1.85, -0.02, 0)
    player.rotation_euler[2] = math.radians(0)
    key(player, 116)
    set_interp(player)

    # Shadow starts small, then grows past the player, selling the mythology idea.
    shadow.scale = (0.08, 0.08, 0.08)
    key(shadow, 1)
    shadow.scale = (1.45, 1.45, 1.45)
    shadow.location = (0.8, 4.72, 1.95)
    key(shadow, 86)
    shadow.scale = (1.92, 1.92, 1.92)
    shadow.location = (0.88, 4.72, 2.12)
    key(shadow, 150)
    set_interp(shadow)

    build_projectors(mats)
    build_evidence_cards(mats)

    # Myth language appears in timed layers.
    intro = add_text("Narration caption 1", "NOT JUST ANOTHER GENIUS", (-2.2, -4.28, 0.18), 0.33, mats["white_glow"], rotation=(math.radians(78), 0, 0))
    myth = add_text("Narration caption 2", "THE ROLE WAS WAITING", (1.4, -4.28, 0.18), 0.33, mats["gold"], rotation=(math.radians(78), 0, 0))
    chosen = add_text("Chosen stamp", "CHOSEN", (-1.8, 4.55, 1.34), 0.62, mats["red_light"], rotation=(math.radians(90), 0, 0))
    sequel = add_text("Sequel line", "THE SEQUEL WAS TOO PERFECT TO IGNORE", (1.55, 4.52, 0.72), 0.28, mats["white_glow"], rotation=(math.radians(90), 0, 0))

    for obj, frame in [(intro, 18), (myth, 54), (chosen, 104), (sequel, 138)]:
        animate_visibility(obj, frame)
        obj.scale = (1.25, 1.25, 1.25)
        key(obj, frame, loc=False, rot=False, scale=True)
        obj.scale = (1.0, 1.0, 1.0)
        key(obj, frame + 8, loc=False, rot=False, scale=True)
        set_interp(obj)

    # Background color bars sell the Barcelona / Argentina visual split.
    left = add_cube("Barcelona red light wall", (-4.7, 4.7, 2.3), (2.4, 0.04, 4.3), mats["barca_red"])
    mid = add_cube("Barcelona blue light wall", (-2.5, 4.69, 2.3), (2.0, 0.04, 4.3), mats["barca_blue"])
    right = add_cube("Argentina blue light wall", (5.2, 4.68, 2.3), (2.7, 0.04, 4.3), mats["arg_blue"])
    for obj, frame in [(left, 42), (mid, 58), (right, 74)]:
        obj.scale.z = 0.01
        key(obj, frame, loc=False, rot=False, scale=True)
        obj.scale.z = 1.0
        key(obj, frame + 20, loc=False, rot=False, scale=True)
        set_interp(obj)


def add_camera_and_lights(mats: dict[str, bpy.types.Material]) -> None:
    bpy.ops.object.light_add(type="AREA", location=(-2.5, -3.8, 5.3))
    key_light = bpy.context.object
    key_light.name = "large cold stadium softbox"
    key_light.data.energy = 720
    key_light.data.size = 5.5

    bpy.ops.object.light_add(type="POINT", location=(-1.9, -1.2, 2.0))
    player_light = bpy.context.object
    player_light.name = "chosen boy rim light"
    player_light.data.energy = 180
    player_light.data.color = (0.65, 0.82, 1.0)

    for x in [-5.6, 0.0, 5.6]:
        bpy.ops.object.light_add(type="POINT", location=(x, 3.8, 3.2))
        flash = bpy.context.object
        flash.name = f"camera flash {x}"
        flash.data.energy = 0
        flash.data.color = (1.0, 0.78, 0.42)
        flash.keyframe_insert(data_path="data.energy", frame=1)
        for frame in [34, 66, 98, 124, 148]:
            flash.data.energy = 650
            flash.keyframe_insert(data_path="data.energy", frame=frame)
            flash.data.energy = 0
            flash.keyframe_insert(data_path="data.energy", frame=frame + 3)

    bpy.ops.object.camera_add(location=(-4.4, -7.2, 2.15), rotation=(math.radians(72), 0, math.radians(-31)))
    camera = bpy.context.object
    bpy.context.scene.camera = camera
    camera.data.lens = 32
    camera.data.dof.use_dof = True
    camera.data.dof.focus_distance = 7.2
    camera.data.dof.aperture_fstop = 4.0

    camera.location = (-4.4, -7.2, 2.15)
    camera.rotation_euler = (math.radians(72), 0, math.radians(-31))
    key(camera, 1, scale=False)
    camera.location = (-2.6, -6.15, 2.25)
    camera.rotation_euler = (math.radians(72), 0, math.radians(-22))
    key(camera, 70, scale=False)
    camera.location = (-1.2, -5.25, 2.65)
    camera.rotation_euler = (math.radians(69), 0, math.radians(-13))
    key(camera, 138, scale=False)
    camera.location = (-0.5, -4.85, 2.9)
    camera.rotation_euler = (math.radians(67), 0, math.radians(-8))
    key(camera, 168, scale=False)
    set_interp(camera)


def add_timeline_markers() -> None:
    markers = [
        (1, "00:11 player enters"),
        (22, "MEDIA projector on"),
        (54, "role was waiting"),
        (86, "shadow dominates"),
        (104, "CHOSEN stamp"),
        (138, "sequel line"),
        (168, "beat end"),
    ]
    for frame, name in markers:
        bpy.context.scene.timeline_markers.new(name, frame=frame)


def main() -> None:
    clear_scene()
    set_scene()
    mats = build_materials()
    build_pitch(mats)
    build_maradona_shadow_scene(mats)
    add_camera_and_lights(mats)
    add_timeline_markers()

    blend_path = OUT_DIR / "chosen_boy_maradona_shadow.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    print(f"Saved Blender file to {blend_path}")

    if RENDER_ANIMATION:
        bpy.ops.render.render(animation=True)
        print(f"Rendered frames to {OUT_DIR}")


if __name__ == "__main__":
    main()
