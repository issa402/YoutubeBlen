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
from mathutils import Vector, Quaternion

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from reference_crossover import plate, camera, masonry, key
from crossover_sprites import sprite
from crossover_approved import approved_ronaldo
from hd_spec import select_eevee_engine
from action_motion import throw_pose, ANKLE
from action_art import throw_arm, debris, speed_lines

FPS = 30
END = 260
CUTS = (("throw", 1, 13), ("city tumble", 14, 32),
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
                # New profile: head on LEFT, pointing arm on RIGHT.
                weight = smooth((u - .44) / .13) * smooth((v - .18) / .16)
                dx, dz = x + .05 * width, z - .02 * height
                angle = -.48
                rx = math.cos(angle) * dx - math.sin(angle) * dz
                rz = math.sin(angle) * dx + math.cos(angle) * dz
                point.co.x = x + (rx - dx) * weight
                point.co.z = z + (rz - dz) * weight
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
    obj.scale = (1.4, 1, 1.4)
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


def impact_bones(root):
    """Brief non-graphic cartoon rib and spine cutaway."""
    bone=emission_material('Impact bone light',(.80,.88,1,1),1.2)
    paths=[[(.10,-1.25,-.65),(.10,-1.25,1.65)]]
    for i in range(8):
        z=1.48-i*.215;w=.49+.22*math.sin(i/7*math.pi)
        for side in (-1,1):
            paths.append([(.10+side*w*math.sin(a),-1.25,z-.17*(1-math.cos(a)))
                          for a in [j*math.pi/12 for j in range(13)]])
    for i,points in enumerate(paths):
        obj=line('Cartoon impact bone '+str(i),points,bone,.022);obj.parent=root
        for f in (1,43,44,45,46,58,59,END):key(obj,'hide_render',not 44<=f<=58,f)

def backdrop(kind, offset, missing):
    preferred = "action-city.png" if kind in ("throw", "city tumble", "hover") else "action-warehouse.png"
    if kind == "impact cutaway":
        preferred = "action-warehouse.png"
    if kind == "reveal":
        preferred = "reference-doorway.png"
    asset = select_asset(preferred, "reference-doorway.png", missing)
    crop = (.15, .15, .85, .85) if kind in ('crouch', 'point') else (0, 0, 1, 1)
    obj = plate(kind + " reconstructed set", offset, asset, crop)
    # Slight overscan supports impact shake without exposing the edge.
    obj.scale = (1.4, 1, 1.4) if kind in ('point','reveal','city tumble','warehouse tumble') else (1.12,1,1.12)
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
    tumble_asset = select_asset("action-tumble.png", "mbappe-crouch-matched.png", missing)
    point_asset = "action-point-right.png"
    reaction_asset = "action-defeated.png"
    print("PHASE: ankle grip, swing and release", flush=True)
    thrower, cape = artwork("Messi ankle throw", "messi-omni-matched.png", -2.05, 4.3, 6.4, "Cape ripple")
    thrower.location.y = -.45
    throw_arm()
    victim, _ = artwork("Mbappe held ankle", tumble_asset, 0, 3.34, 5.0)
    characters.extend((thrower, victim))
    for frame in range(1,14):
        pose = throw_pose(frame)
        x,z = pose.center
        key(victim, 'location', (x,-.6,z),frame)
        key(victim, 'rotation_euler', (0,pose.angle,0),frame)
        key(victim, 'scale', (pose.scale,1,pose.scale),frame)
        shape_key(cape, smooth((frame-3)/10),frame)
        key(cams[0], 'location', (-1.8+.25*smooth((frame-7)/6),-25,1.1),frame)
        key(cams[0].data,'ortho_scale',10.6-.3*smooth((frame-7)/6),frame)
    speed_lines(0, 10, 13, towards_camera=True)
    print("PHASE: flight toward warehouse", flush=True)
    for shot_index in (1,2):
        _,start,end = CUTS[shot_index]
        offset=shot_index*40
        flying,_=artwork("Mbappe thrown flight "+str(shot_index),tumble_asset,offset,6,6)
        characters.append(flying)
        speed_lines(offset,start,end, towards_camera=shot_index==1)
        base_camera_rotation=cams[shot_index].rotation_euler.to_quaternion()
        for frame in range(start,end+1):
            t=(frame-start)/(end-start)
            # First camera faces the outgoing throw: close foreground recedes
            # toward warehouse. Next camera follows it into the wall.
            if shot_index==1:
                x=offset-1.4+2.5*t
                z=.6-.3*t
                scale=1.65*(1-t)**2+.34
                rotation=.49-3.04*t
            else:
                x=offset-2.4+3.4*t
                z=.55-.4*t
                scale=.65+.25*t
                rotation=-2.55-3.73*t
            key(flying,'location',(x,-.8,z),frame)
            key(flying,'rotation_euler',(0,rotation,0),frame)
            key(flying,'scale',(scale,1,scale),frame)
            key(cams[shot_index],'location',(offset+.5*t,-25,.2),frame)
            roll=(.10+.18*t) if shot_index==1 else (.28-.28*t)
            key(cams[shot_index],'rotation_euler',(base_camera_rotation @ Quaternion((0,0,1),roll)).to_euler(),frame)
    flash("Wall contact flash",80,(1,.87,.66,1),((1,0),(41,0),(43,.75),(44,0),(END,0)))
    print("PHASE: impact cutaway", flush=True)
    impact, _ = artwork("Mbappe impact silhouette", tumble_asset, 120, 7.0, 7.0)
    impact_bones(impact)
    debris(120)
    impact_emit=next(n for n in impact.data.materials[0].node_tree.nodes if n.type=='EMISSION')
    for f in (1,43,44,58,59,END):
        key(impact_emit.inputs['Strength'],'default_value',.02 if 44<=f<=58 else 1.0,f)
    characters.append(impact)
    for frame in range(44, 65):
        t = (frame - 44) / 20
        key(impact, "rotation_euler", (0, -.10 + .06 * math.sin(t * math.pi), 0), frame)
        key(impact, "location", (120, -.5, -.2 - .2 * t), frame)
        key(impact, "scale", (1+.10*math.exp(-t*8),1,1-.10*math.exp(-t*8)),frame)
        shake=.15*math.exp(-t*6)
        key(cams[3],"location",(120+shake*math.sin(frame*2.1),-25,.70+shake*math.cos(frame*1.5)),frame)
        key(cams[3].data, "ortho_scale", 6.2 - .3 * t, frame)
    flash("Abstract impact pulse", 120, (.07, .65, 1, 1), ((1, 0), (46, .6), (48, 0), (52, .28), (56, 0), (END, 0)))
    print("PHASE: wall recoil, drop and hovering arrival", flush=True)
    pinned,_=artwork("Mbappe wall recoil",tumble_asset,161,2.6,3.9)
    landed,compression=artwork("Mbappe defeated landing",reaction_asset,161,2.6,3.9,"Landing compression")
    approaching,cape=artwork("Messi hovering arrival","messi-omni-matched.png",156.7,4,6.0,"Cape ripple")
    characters.extend((pinned,landed,approaching))
    for frame in range(65,110):
        t=(frame-65)/44
        fall=smooth((frame-71)/10)
        key(pinned,'location',(161,-.3,-.05-2.0*fall),frame)
        key(pinned,'rotation_euler',(0,-.12*fall,0),frame)
        key(pinned,'hide_render',frame>=80,frame)
        key(landed,'hide_render',frame<80,frame)
        key(landed,'location',(161,-.35,-2.3+.09*math.exp(-max(0,frame-80)/5)),frame)
        shape_key(compression,math.exp(-max(0,frame-80)/5),frame)
        descent=smooth((frame-89)/15)
        key(approaching,'location',(156.5+.6*descent,-1.2,8-7.35*descent+.05*math.sin(frame*.28)),frame)
        shape_key(cape,.5+.5*math.sin(frame*.25),frame)
        key(cams[4].data,'ortho_scale',16-.5*t,frame)
    print("PHASE: hover", flush=True)
    hovering, cape = artwork("Messi folded-arms hover", "messi-omni-matched.png", 200, 5.6, 8.4, "Cape ripple")
    characters.append(hovering)
    for frame in range(110, 147):
        t = (frame - 110) / 36
        key(hovering, "location", (200, -.6, .05 + .10 * math.sin(t * math.pi * 2)), frame)
        shape_key(cape, .5 + .5 * math.sin(t * math.pi * 3), frame)
        key(cams[5].data, "ortho_scale", 16 - .35 * smooth(t), frame)
    print("PHASE: crouch and pointing", flush=True)
    crouching, compression = artwork("Mbappe close reaction", reaction_asset, 240, 8.0, 11, "Landing compression")
    pointing, reach = artwork("Mbappe defeated points right", point_asset, 280, 16.0, 8.0, "Pointing reach")
    characters.extend((crouching, pointing))
    for frame in range(147, 176):
        t = (frame - 147) / 28
        key(crouching, "location", (240, -.5, -1.9 + .07 * math.sin(t * math.pi)), frame)
        key(crouching, "rotation_euler", (0, -.018 * math.sin(t * math.pi), 0), frame)
        shape_key(compression, .1 + .1 * math.sin(t * math.pi * 2), frame)
    for frame in range(176, 209):
        t = (frame - 176) / 32
        extension = smooth((frame - 176) / 7)
        shape_key(reach, 1 - extension, frame)
        key(pointing, "location", (280, -.8, -.90 + .04 * math.sin(t * math.pi)), frame)
        key(cams[7].data, "ortho_scale", 16 - .3 * extension, frame)
        # Follow the indicated direction; next shot catches the same rightward pan.
        key(cams[7], "location", (280+2.0*smooth((frame-201)/7),-25,0),frame)
    flash("Pointing pink pulse", 280, (1, .1, .33, 1), ((1,0),(200,0),(205,.10),(208,.26),(209,0),(END,0)))
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
        key(cams[8].data, "ortho_scale", 16 - .9 * smooth(t), frame)
        key(cams[8], "location", (320-2.0*(1-smooth((frame-209)/8)),-25,0),frame)
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
    contacts=[]
    victim=bpy.data.objects['Mbappe held ankle']
    for frame in range(1,11):
        scene.frame_set(frame)
        pose=throw_pose(frame)
        actual=victim.matrix_world @ Vector((ANKLE[0],-1,ANKLE[1]))
        error=math.hypot(actual.x-pose.grip[0],actual.z-pose.grip[1])
        palm=bpy.data.objects['Ankle grip palm'].matrix_world.translation
        visible_error=math.hypot(actual.x-palm.x,actual.z-palm.z)
        if max(error,visible_error)>1e-4:
            raise RuntimeError(f"Ankle detached at frame {frame}: {error}")
        contacts.append({"frame":frame,"ankle_grip_error":error,"visible_palm_error":visible_error})
    pointing=bpy.data.objects['Mbappe defeated points right']
    neutral=pointing.data.shape_keys.key_blocks[0]
    lowered=pointing.data.shape_keys.key_blocks[1]
    width=max(v.co.x for v in neutral.data)-min(v.co.x for v in neutral.data)
    height=max(v.co.z for v in neutral.data)-min(v.co.z for v in neutral.data)
    head_indices=[i for i,v in enumerate(neutral.data) if .23<v.co.x/width+.5<.42 and v.co.z/height+.5>.62]
    head_drift=max((neutral.data[i].co-lowered.data[i].co).length for i in head_indices)
    if head_drift>1e-6:
        raise RuntimeError('Pointing arm deformation changed the head')
    point_samples=[]
    for frame in (183,192,201,208):
        scene.frame_set(frame)
        finger=pointing.matrix_world @ Vector((width*.45,-1,height*.025))
        head=pointing.matrix_world @ Vector((-width*.17,-1,height*.25))
        camera_right=scene.camera.location.x+scene.camera.data.ortho_scale*.5
        if finger.x<=head.x or finger.x>=camera_right:
            raise RuntimeError(f'Pointing direction/framing invalid at {frame}')
        point_samples.append({'frame':frame,'finger_x':finger.x,'head_x':head.x,'camera_right':camera_right})
    scene.frame_set(1)
    return {"right_point_samples":point_samples,"point_head_drift":head_drift,"grip_contacts":contacts,"camera_samples": samples, "characters": objects,
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
                              "Overhead ankle throw and right-point staging; 2.5D adaptation, not exact motion capture",
                              "Stylized impact cutaway replaces source internal anatomy",
                              "No source audio"]}
    (output / "motion-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("PHASE: complete", flush=True)


if __name__ == "__main__":
    main()
