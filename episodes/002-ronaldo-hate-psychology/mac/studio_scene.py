"""Deterministic standalone Blender scene. Run with Blender, never plain Python."""
import argparse
import json
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def safe_output(root, relative):
    path = Path(relative)
    if path.is_absolute() or '..' in path.parts or '\\' in relative or ':' in relative:
        raise ValueError('Output must be a portable relative path inside the package')
    result = (root / path).resolve()
    if not result.is_relative_to(root) or result == root:
        raise ValueError('Output must stay inside the package')
    return result


def load_manifest(path):
    manifest = json.loads(path.read_text(encoding='utf-8'))
    if manifest.get('schema_version') != 1:
        raise ValueError('Unsupported manifest schema')
    for key, low, high in [('fps', 1, 60), ('frame_start', 1, 1),
                           ('frame_end', 1, 7200), ('seed', 0, 999999)]:
        if type(manifest.get(key)) is not int or not low <= manifest[key] <= high:
            raise ValueError(f'Invalid {key}')
    for key in ('resolution', 'preview_resolution'):
        dims = manifest.get(key)
        if not isinstance(dims, list) or len(dims) != 2 or any(
                type(n) is not int or not 64 <= n <= 3840 for n in dims):
            raise ValueError(f'Invalid {key}')
    safe_output(path.parent, manifest['output'])
    return manifest


def material(name, color, metallic=0, emission=0):
    result = bpy.data.materials.new(name)
    result.diffuse_color = (*color, 1)
    result.use_nodes = True
    shader = result.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = .28
    shader.inputs['Emission Color'].default_value = (*color, 1)
    shader.inputs['Emission Strength'].default_value = emission
    return result


def cube(name, location, scale, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name, obj.scale = name, scale
    obj.data.materials.append(mat)
    return obj


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


def light(name, location, energy, color, size=4):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy, data.color, data.shape, data.size = energy, color, 'DISK', size
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    aim(obj, (0, 0, 1.3))
    return obj


def figure(name, x, mat):
    """Abstract editable athlete, deliberately not a real person's likeness."""
    cube(name + ' Torso', (x, 0, 1.45), (.56, .30, .72), mat)
    for side in (-1, 1):
        leg = cube(name + f' Leg {side}', (x + side * .18, 0, .56), (.20, .24, 1.1), mat)
        leg.rotation_euler.y = side * -.08
        arm = cube(name + f' Arm {side}', (x + side * .43, 0, 1.43), (.17, .20, .66), mat)
        arm.rotation_euler.y = side * -.25
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16,
                                       radius=.23, location=(x, 0, 2.05))
    bpy.context.object.name = name + ' Head'
    bpy.context.object.data.materials.append(mat)
    bpy.ops.object.shade_smooth()


def build(manifest):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.render.fps = manifest['fps']
    scene.frame_start, scene.frame_end = manifest['frame_start'], manifest['frame_end']
    scene.render.resolution_x, scene.render.resolution_y = manifest['resolution']
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.world.color = (.008, .012, .022)
    gold = material('Brushed Gold', (.8, .42, .09), .85)
    dark = material('Graphite', (.018, .025, .04), .45)
    grass = material('Pitch', (.014, .075, .06))
    white = material('Pitch Lines', (.5, .8, .7), emission=.2)
    blue = material('Broadcast Cyan', (.025, .5, .9), emission=3)
    red_kit = material('Red Athlete', (.55, .025, .035), metallic=.3)
    cyan_kit = material('Cyan Athlete', (.025, .35, .55), metallic=.3)
    figure('Red Competitor', -2, red_kit)
    figure('Cyan Competitor', 2, cyan_kit)
    cube('Pitch', (0, 0, -.08), (13, 10, .15), grass)
    for y in (-4.4, 4.4):
        cube('Touchline', (0, y, .01), (12, .035, .015), white)
    for x in (-6, 0, 6):
        cube('Field Line', (x, 0, .01), (.035, 8.8, .015), white)
    cube('Trophy Plinth', (0, 0, .35), (1.6, 1.6, .7), dark)
    bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=.38, radius2=.18,
                                    depth=1.25, location=(0, 0, 1.3))
    bpy.context.object.name = 'Trophy Stem'
    bpy.context.object.data.materials.append(gold)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24,
                                       radius=.57, location=(0, 0, 2.1))
    bpy.context.object.name = 'Trophy Globe'
    bpy.context.object.data.materials.append(gold)
    bpy.ops.object.shade_smooth()
    rng = random.Random(manifest['seed'])
    for index in range(9):
        angle = math.pi * (.06 + index / 10)
        x, y = 3.5 * math.cos(angle), 3.5 * math.sin(angle)
        panel = cube(f'Broadcast Screen {index:02}', (x, y, 1.8), (1.0, .10, 1.3), dark)
        panel.rotation_euler.z = angle - math.pi / 2
        face = cube(f'Screen Glow {index:02}', (x, y-.08, 1.8), (.85, .11, 1.04), blue)
        face.rotation_euler.z = panel.rotation_euler.z
        flash = light(f'Flash {index:02}', (x, y, 2.8), 0, (.4, .7, 1), .3)
        for frame in range(1, scene.frame_end + 1, 6):
            flash.data.energy = 260 if rng.random() > .72 else 0
            flash.data.keyframe_insert('energy', frame=frame)
    light('Key', (3, -4, 6), 1500, (1, .75, .4))
    light('Rim', (-4, 2, 5), 1800, (.15, .55, 1))
    light('Fill', (-3, -4, 3), 650, (.6, .75, 1))
    light('Red Spotlight', (-3, -2, 5), 1100, (1, .06, .03), 1)
    light('Cyan Spotlight', (3, -2, 5), 1100, (.03, .6, 1), 1)
    bpy.ops.object.camera_add(location=(6, -10, 5))
    camera = bpy.context.object
    camera.name, camera.data.lens = 'Studio Camera', 48
    scene.camera = camera
    # Three viewpoints describe a shallow orbit; both competitors stay in shot.
    for frame, pos in [(1, (3, -11, 4.8)),
                       (max(1, scene.frame_end // 2), (0, -11.4, 4.2)),
                       (scene.frame_end, (-3, -11, 3.8))]:
        camera.location = pos
        aim(camera, (0, .2, 1.3))
        camera.keyframe_insert('location', frame=frame)
        camera.keyframe_insert('rotation_euler', frame=frame)
    scene.frame_set(1)
    return scene


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--preview', action='store_true')
    mode.add_argument('--render', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    path = Path(args.manifest).resolve()
    manifest = load_manifest(path)
    root = path.parent
    scene = build(manifest)
    required = ('Trophy Globe', 'Trophy Stem', 'Pitch', 'Studio Camera', 'Key', 'Rim',
                'Red Competitor Head', 'Cyan Competitor Head')
    missing = [name for name in required if name not in bpy.data.objects]
    if missing or scene.camera is None:
        raise RuntimeError(f'Scene validation failed: {missing}')
    outputs = safe_output(root, manifest['output'])
    outputs.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(outputs / 'frame_')
    report = {'valid': True, 'blender_version': bpy.app.version_string,
              'missing_objects': missing, 'external_assets': [],
              'frame_range': [scene.frame_start, scene.frame_end],
              'resolution': manifest['resolution'], 'fps': scene.render.fps,
              'rendered_resolution': manifest['preview_resolution'] if args.preview else manifest['resolution'],
              'rendered_frames': [],
              'render_complete': False, 'mode': 'preview' if args.preview else 'full' if args.render else 'build'}
    validation = safe_output(root, 'validation.json')
    validation.write_text(json.dumps(report, indent=2), encoding='utf-8')
    bpy.ops.wm.save_as_mainfile(filepath=str(safe_output(root, 'scene.blend')))
    if args.preview:
        preview = safe_output(root, 'previews')
        preview.mkdir(exist_ok=True)
        scene.render.resolution_x, scene.render.resolution_y = manifest['preview_resolution']
        for frame in sorted({1, max(1, scene.frame_end // 2), scene.frame_end}):
            scene.frame_set(frame)
            scene.render.filepath = str(preview / f'frame_{frame:04}.png')
            bpy.ops.render.render(write_still=True)
            report['rendered_frames'].append(frame)
    elif args.render:
        bpy.ops.render.render(animation=True)
        report['rendered_frames'] = list(range(scene.frame_start, scene.frame_end + 1))
    report['render_complete'] = bool(args.preview or args.render)
    validation.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
