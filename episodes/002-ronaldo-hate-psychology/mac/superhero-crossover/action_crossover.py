"""Nine-shot illustrated action adaptation of the creator's longer reference.

Layered 2.5D artwork, deterministic motion, and reconstructed backgrounds.
No source footage or audio is embedded. Run with Blender's own Python.
"""
import argparse
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from reference_crossover import plate, camera, masonry, key
from crossover_sprites import sprite
from crossover_approved import approved_ronaldo
from hd_spec import select_eevee_engine

FPS = 30
END = 260
CUTS = (("strike", 1, 13), ("city tumble", 14, 32),
        ("warehouse tumble", 33, 43), ("impact cutaway", 44, 64),
        ("landing wide", 65, 109), ("hover", 110, 146),
        ("crouch", 147, 175), ("point", 176, 208),
        ("reveal", 209, END))
PREVIEWS = tuple(sorted({f for _, start, end in CUTS
                         for f in (start, (start + end) // 2, end)}))


def smooth(value):
    value = min(1.0, max(0.0, value))
    return value * value * (3 - 2 * value)


def select_asset(preferred, fallback, missing):
    if (HERE / "assets" / preferred).is_file():
        return preferred
    missing.append(preferred)
    return fallback


def artwork(name, asset, offset, width, height, deform=None):
    """Center artwork and give it bounded shape keys, without the old timing."""
    image = bpy.data.images.load(str(HERE / 'assets' / asset), check_existing=True)
    width = height * image.size[0] / image.size[1]
    obj = sprite(name, asset, offset, width, height, rig='grid' if deform else False)
    obj.data.animation_data_clear()
    for vertex in obj.data.vertices:
        vertex.co.z -= height * .5
    if deform:
        obj.shape_key_add(name="Neutral artwork")
        motion = obj.shape_key_add(name=deform)
        for point in motion.data:
            x, y, z = point.co
            u, v = x / width + .5, z / height + .5
            if deform == "Pointing reach":
                # Foreground hand is at upper left. Face at upper right stays fixed.
                weight = smooth((.63 - u) / .25) * smooth((v - .22) / .13)
                dx, dz = x - .12 * width, z - .05 * height
                angle = -.10
                rx = math.cos(angle) * dx - math.sin(angle) * dz
                rz = math.sin(angle) * dx + math.cos(angle) * dz
                point.co.x = x + (rx - dx - .035 * width) * weight
                point.co.z = z + (rz - dz + .025 * height) * weight
            elif deform == "Cape ripple":
                weight = smooth((abs(u - .5) - .17) / .16) * smooth((.7 - v) / .45)
                point.co.x += math.sin(v * 9) * .13 * weight
                point.co.z += math.cos(u * 5) * .06 * weight
            elif deform == "Landing compression":
                weight = smooth((.58 - v) / .45)
                point.co.x += (u - .5) * .07 * weight
                point.co.z += .09 * math.sin(u * math.pi) * weight
        return obj, motion
    return obj, None


def shape_key(motion, value, frame):
    if motion is not None:
        motion.value = value
        motion.keyframe_insert("value", frame=frame)


def emission_material(name, color, strength=1):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    emit = nodes.new("ShaderNodeEmission")
    emit.inputs["Color"].default_value = color
    emit.inputs["Strength"].default_value = strength
    out = nodes.new("ShaderNodeOutputMaterial")
    mat.node_tree.links.new(emit.outputs[0], out.inputs[0])
    return mat


def line(name, points, material, thickness=.025):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = thickness
    curve.resolution_u = 1
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, co in zip(spline.points, points):
        point.co = (*co, 1)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    curve.materials.append(material)
    return obj


def flash(name, offset, color, values):
    obj = plate(name, offset)
    obj.location.y = -12
    material = obj.data.materials[0]
    if hasattr(material, 'surface_render_method'):
        material.surface_render_method = 'BLENDED'
    nodes = obj.data.materials[0].node_tree.nodes
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    emit = nodes.new("ShaderNodeEmission")
    emit.inputs["Color"].default_value = color
    transparent = nodes.new("ShaderNodeBsdfTransparent")
    mix = nodes.new("ShaderNodeMixShader")
    links = obj.data.materials[0].node_tree.links
    links.new(transparent.outputs[0], mix.inputs[1])
    links.new(emit.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], out.inputs[0])
    for frame, value in values:
        key(mix.inputs[0], "default_value", value, frame)
    return obj


def punch_arm(root):
    """Native sleeve and forearm preserve the approved face and body."""
    ink=emission_material('Punch outline',(.012,.015,.02,1))
    white=emission_material('Punch white sleeve',(.78,.81,.80,1))
    red=emission_material('Punch red glove',(.55,.035,.025,1))
    upper=bpy.data.objects.new('Punch shoulder',None)
    bpy.context.collection.objects.link(upper);upper.parent=root
    upper.location=(.55,-.1,1.2)
    lower=bpy.data.objects.new('Punch elbow',None)
    bpy.context.collection.objects.link(lower);lower.parent=upper
    lower.location=(1.05,-.02,0)
    def part(name,points,mat,parent):
        mesh=bpy.data.meshes.new(name)
        mesh.from_pydata([(x,-1.05,z) for x,z in points],[],[tuple(range(len(points)))])
        mesh.update();obj=bpy.data.objects.new(name,mesh)
        bpy.context.collection.objects.link(obj);obj.parent=parent;mesh.materials.append(mat)
        outline=line(name+' contour',[(x,-1.07,z) for x,z in points+[points[0]]],ink,.024)
        outline.parent=parent
    # Cover the source's folded forearms before adding the new action sleeve.
    part('Action torso',[(-.76,1.55),(.70,1.55),(.66,.45),(.48,-.48),(-.48,-.48),(-.7,.45)],red,root)
    part('Guard upper sleeve',[(-.76,1.7),(-1.05,1.38),(-1.04,.45),(-.77,.28),(-.61,.5),(-.61,1.4)],white,root)
    part('Guard glove',[(-1.04,.51),(-.76,.43),(-.65,.06),(-.75,-.16),(-1.01,-.1),(-1.12,.11)],red,root)
    part('Action chest emblem',[(-.43,1.5),(.39,1.5),(.49,1.27),(.17,1.09),(.14,-.32),(-.05,-.32),(-.08,1.12),(-.44,1.18)],white,root)
    part('White upper sleeve',[(-.25,-.25),(.1,-.35),(1.1,-.24),(1.22,.05),(1.05,.26),(.05,.34),(-.26,.18)],white,upper)
    part('Extended red forearm',[(-.12,-.23),(1.02,-.2),(1.36,-.32),(1.72,-.26),(1.78,.14),(1.51,.31),(1.16,.27),(.96,.17),(-.14,.24)],red,lower)
    for f in range(1,14):
        t=smooth((f-1)/6)
        key(upper,'rotation_euler',(0,.6-.9*t,0),f)
        key(lower,'rotation_euler',(0,-1.8+1.8*t,0),f)


def impact_bones(root):
    """Brief non-graphic cartoon rib and spine cutaway."""
    bone=emission_material('Impact bone light',(.80,.88,1,1),1.2)
    paths=[[(0,-1.25,-1.5),(0,-1.25,1.65)]]
    for i in range(7):
        z=1.35-i*.28;w=.65+.25*math.sin(i/6*math.pi)
        for side in (-1,1):
            paths.append([(0,-1.25,z+.08),(side*w*.75,-1.25,z+.15),(side*w,-1.25,z),(side*w*.75,-1.25,z-.18),(0,-1.25,z-.16)])
    for i,points in enumerate(paths):
        obj=line('Cartoon impact bone '+str(i),points,bone,.045);obj.parent=root
        for f in (1,43,44,45,46,58,59,END):key(obj,'hide_render',not 44<=f<=58,f)

def backdrop(kind, offset, missing):
    preferred = "action-city.png" if kind in ("strike", "city tumble", "hover") else "action-warehouse.png"
    if kind == "impact cutaway":
        preferred = "action-warehouse.png"
    if kind == "reveal":
        preferred = "reference-doorway.png"
    asset = select_asset(preferred, "reference-doorway.png", missing)
    crop = (.15, .15, .85, .85) if kind in ('crouch', 'point') else (0, 0, 1, 1)
    obj = plate(kind + " reconstructed set", offset, asset, crop)
    # Slight overscan supports impact shake without exposing the edge.
    obj.scale = (1.12, 1, 1.12)
    return obj


def cape_motion(obj, start, end):
    obj.shape_key_add(name="Approved Ronaldo artwork")
    ripple = obj.shape_key_add(name="Cape edge airflow")
    for point in ripple.data:
        x, _, z = point.co
        weight = smooth((abs(x) - .8) / .65) * smooth((4.9 - z) / 2.1)
        point.co.x += .13 * math.sin(z * 2.6) * weight
        point.co.z += .04 * math.cos(z * 1.8) * weight
    for frame in range(start, end + 1):
        shape_key(ripple, .5 + .5 * math.sin((frame - start) * .22), frame)


def lightning(offset, start, end):
    mat = emission_material("Ronaldo energy blue", (.34, .7, 1, 1), 2)
    for side in (-1, 1):
        points = []
        for index in range(9):
            z = -2.8 + index * .8
            x = offset + side * (2.15 + .3 * math.sin(index * 4.3))
            points.append((x, -1.2, z))
        bolt = line("Doorway energy bolt", points, mat, .032)
        for frame in range(start, end + 1):
            active = frame - start in (0, 1, 5, 6, 10, 11, 12, 18, 19)
            key(bolt, "hide_render", not active, frame)


def build(size):
    print("PHASE: clear scene", flush=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.timeline_markers.clear()
    available = (item.identifier for item in scene.render.bl_rna.properties["engine"].enum_items)
    scene.render.engine = select_eevee_engine(available)
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.fps = FPS
    scene.render.fps_base = 1
    scene.frame_start, scene.frame_end = 1, END
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "Standard"
    if hasattr(scene, "eevee") and hasattr(scene.eevee, "taa_render_samples"):
        scene.eevee.taa_render_samples = 32
    scene.world.color = (.03, .035, .045)
    missing, characters, cams = [], [], []
    print("PHASE: reconstructed backgrounds and cameras", flush=True)
    for index, (name, start, _) in enumerate(CUTS):
        offset = index * 40
        cams.append(camera(name, offset, start))
        backdrop(name, offset, missing)
    strike_asset = select_asset("action-strike.png", "messi-omni-matched.png", missing)
    tumble_asset = select_asset("action-tumble.png", "mbappe-crouch-matched.png", missing)
    point_asset = select_asset("action-point.png", "mbappe-profile-matched.png", missing)
    print("PHASE: strike", flush=True)
    striker, cape = artwork("Messi decisive strike", strike_asset, -1, 9.6, 6.4, "Cape ripple")
    if strike_asset == 'messi-omni-matched.png':
        punch_arm(striker)
    victim, _ = artwork("Mbappe struck", tumble_asset, 2.8, 5.0, 5.0)
    characters.extend((striker, victim))
    for frame in range(1, 14):
        t = (frame - 1) / 12
        reach = smooth(t / .5)
        key(striker, "location", (-1.5 + reach * 1.0, -.5, -.1 + .12 * reach), frame)
        key(striker, "rotation_euler", (0, -.04 + .08 * reach, 0), frame)
        shape_key(cape, t, frame)
        key(victim, "location", (2.8 + 3 * smooth((t - .35) / .65), -.4, .3 + .65 * t), frame)
        key(victim, "rotation_euler", (0, -.1 - .6 * smooth((t - .35) / .65), 0), frame)
        key(cams[0], "location", (1.1 + .1 * math.sin(frame * 2) * reach, -25, 1.0 + .04 * math.cos(frame)), frame)
    cams[0].data.ortho_scale = 12.5
    flash("Strike contact flash", 0, (1, .85, .5, 1), ((1, 0), (6, 0), (7, .7), (8, .15), (10, 0), (END, 0)))
    print("PHASE: tumbling motion", flush=True)
    for shot_index in (1, 2):
        _, start, end = CUTS[shot_index]
        offset = shot_index * 40
        tumbling, _ = artwork("Mbappe airborne " + str(shot_index), tumble_asset, offset, 6.0, 6.0)
        characters.append(tumbling)
        for frame in range(start, end + 1):
            t = (frame - start) / (end - start)
            x = offset + (3.3 - 6.6 * t if shot_index == 1 else -3.2 + 5.6 * t)
            z = 1.4 - 2 * t + .9 * math.sin(t * math.pi)
            rotation = .25 + 3.8 * t if shot_index == 1 else 3.9 + 2.8 * t
            key(tumbling, "location", (x, -.8, z), frame)
            key(tumbling, "rotation_euler", (0, rotation, 0), frame)
            scale = .78 + .16 * math.sin(t * math.pi)
            key(tumbling, "scale", (scale, 1, scale), frame)
            key(cams[shot_index], "location", (offset + .15 * math.sin(frame * 1.8), -25, .06 * math.cos(frame * 1.7)), frame)
    flash("Wall contact flash", 80, (1, .87, .66, 1), ((1, 0), (42, 0), (44, .8), (45, .5), (46, 0), (END, 0)))
    print("PHASE: impact cutaway", flush=True)
    impact, _ = artwork("Mbappe impact silhouette", tumble_asset, 120, 7.0, 7.0)
    impact_bones(impact)
    impact_emit=next(n for n in impact.data.materials[0].node_tree.nodes if n.type=='EMISSION')
    for f in (1,43,44,58,59,END):
        key(impact_emit.inputs['Strength'],'default_value',.02 if 44<=f<=58 else 1.0,f)
    characters.append(impact)
    for frame in range(44, 65):
        t = (frame - 44) / 20
        key(impact, "rotation_euler", (0, -.85 + .12 * math.sin(t * math.pi), 0), frame)
        key(impact, "location", (120, -.5, -.2 - .2 * t), frame)
        key(cams[3].data, "ortho_scale", 11.5 - .6 * t, frame)
    flash("Abstract impact pulse", 120, (.07, .65, 1, 1), ((1, 0), (46, .6), (48, 0), (52, .28), (56, 0), (END, 0)))
    print("PHASE: landing and foreground arrival", flush=True)
    landed, compression = artwork("Mbappe warehouse landing", "mbappe-crouch-matched.png", 161, 2.6, 3.9, "Landing compression")
    boots, _ = artwork("Messi boots foreground", "messi-omni-matched.png", 156, 11, 16.5)
    characters.extend((landed, boots))
    for frame in range(65, 110):
        t = (frame - 65) / 44
        key(landed, "location", (161, -.2, -2.1 + .32 * math.exp(-t * 10) * math.sin(t * 18)), frame)
        shape_key(compression, math.exp(-t * 6), frame)
        descent = smooth((t - .58) / .33)
        key(boots, "location", (156, -3, 14 - 10.1 * descent), frame)
        key(cams[4].data, "ortho_scale", 16 - .25 * t, frame)
    print("PHASE: hover", flush=True)
    hovering, cape = artwork("Messi folded-arms hover", "messi-omni-matched.png", 200, 5.6, 8.4, "Cape ripple")
    characters.append(hovering)
    for frame in range(110, 147):
        t = (frame - 110) / 36
        key(hovering, "location", (200, -.6, .05 + .10 * math.sin(t * math.pi * 2)), frame)
        shape_key(cape, .5 + .5 * math.sin(t * math.pi * 3), frame)
        key(cams[5].data, "ortho_scale", 16 - .35 * smooth(t), frame)
    print("PHASE: crouch and pointing", flush=True)
    crouching, compression = artwork("Mbappe close reaction", "mbappe-crouch-matched.png", 240, 8.0, 12, "Landing compression")
    pointing, reach = artwork("Mbappe foreshortened pointing", point_asset, 280, 16.0, 10.667, "Pointing reach")
    characters.extend((crouching, pointing))
    for frame in range(147, 176):
        t = (frame - 147) / 28
        key(crouching, "location", (240, -.5, -1.9 + .07 * math.sin(t * math.pi)), frame)
        key(crouching, "rotation_euler", (0, -.018 * math.sin(t * math.pi), 0), frame)
        shape_key(compression, .1 + .1 * math.sin(t * math.pi * 2), frame)
    for frame in range(176, 209):
        t = (frame - 176) / 32
        extension = smooth((frame - 176) / 2)
        shape_key(reach, 1 - extension, frame)
        key(pointing, "location", (280 + .16 * (1 - extension), -.8, -.55 - .12 * (1 - extension)), frame)
        key(cams[7].data, "ortho_scale", 16 - .7 * extension, frame)
    flash("Pointing pink pulse", 280, (1, .1, .33, 1), ((1, 0), (191, 0), (194, .32), (197, .7), (199, .03), (201, 0), (207, .25), (209, 0), (END, 0)))
    print("PHASE: Ronaldo reveal", flush=True)
    ronaldo = approved_ronaldo(320)
    ronaldo.scale = (.90, .90, .90)
    characters.append(ronaldo)
    cape_motion(ronaldo, 209, END)
    emit = next(node for node in ronaldo.data.materials[0].node_tree.nodes if node.type == "EMISSION")
    for frame in range(209, END + 1):
        t = (frame - 209) / (END - 209)
        key(ronaldo, "location", (320, -.5, -3.2 + .035 * math.sin(t * math.pi * 3)), frame)
        key(emit.inputs["Strength"], "default_value", (.035 if frame in (209,210,211,212,213,215,216,220,221) else 1.0), frame)
        key(cams[8].data, "ortho_scale", 16 - .5 * smooth(t), frame)
    lightning(320, 209, END)
    flash("Ronaldo reveal light", 320, (.50, .78, 1, 1), ((1, 0), (208, 0), (209, .16), (210, 0), (216, .2), (218, 0), (END, 0)))
    print("PHASE: clean viewport", flush=True)
    scene.camera = cams[0]
    scene.frame_set(1)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                space = area.spaces.active
                space.region_3d.view_perspective = "CAMERA"
                space.overlay.show_overlays = False
                space.show_gizmo = False
                space.shading.type = "SOLID"
                space.shading.color_type = "TEXTURE"
    return scene, characters, sorted(set(missing))


def validate(scene, characters):
    samples = []
    for name, start, end in CUTS:
        for frame in (start, end):
            scene.frame_set(frame)
            if scene.camera.name != name:
                raise RuntimeError(f"Camera mismatch at {frame}: {scene.camera.name}")
            samples.append({"frame": frame, "camera": scene.camera.name,
                            "camera_location": list(scene.camera.location),
                            "ortho_scale": scene.camera.data.ortho_scale})
    if not scene.render.resolution_x or scene.frame_end != END:
        raise RuntimeError("Invalid render configuration")
    objects = []
    for obj in characters:
        if not obj.data.vertices or not obj.data.materials:
            raise RuntimeError(f"Incomplete character: {obj.name}")
        objects.append({"name": obj.name, "vertices": len(obj.data.vertices),
                        "shape_keys": len(obj.data.shape_keys.key_blocks) if obj.data.shape_keys else 0,
                        "has_transform_motion": obj.animation_data is not None})
    scene.frame_set(1)
    return {"camera_samples": samples, "characters": objects,
            "character_type": "Layered illustrated 2.5D meshes; not skeletal 3D characters"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--resolution", nargs=2, type=int, default=(1920, 1080))
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--preview", action="store_true")
    modes.add_argument("--render", action="store_true")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    if any(value < 64 or value > 4096 for value in args.resolution):
        parser.error("Resolution dimensions must be 64..4096")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    frames = list(range(1, END + 1)) if args.render else list(PREVIEWS) if args.preview else []
    folder = output / ("frames" if args.render else "previews")
    if frames and folder.exists() and any(folder.iterdir()):
        raise FileExistsError("Use a fresh output directory to preserve previous renders")
    scene, characters, missing = build(args.resolution)
    print("PHASE: structured scene validation", flush=True)
    inspection = validate(scene, characters)
    print("PHASE: save Blender scene", flush=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "action-crossover.blend"))
    if frames:
        folder.mkdir(exist_ok=True)
    for frame in frames:
        scene.frame_set(frame)
        scene.render.filepath = str(folder / f"frame_{frame:04}.png")
        bpy.ops.render.render(write_still=True)
        print(f"Frame {frame}/{END}", flush=True)
    report = {"frames": END, "fps": FPS, "seconds": END / FPS,
              "resolution": list(args.resolution), "cuts": CUTS, "rendered": frames,
              "render_complete": bool(args.render and len(frames) == END),
              "fallback_assets": missing, "inspection": inspection,
              "limitations": ["Backgrounds reconstructed, not source footage pixels",
                              "Articulated 2.5D pose adaptation, not exact motion capture",
                              "Stylized impact cutaway replaces source internal anatomy",
                              "No source audio"]}
    (output / "motion-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("PHASE: complete", flush=True)


if __name__ == "__main__":
    main()
