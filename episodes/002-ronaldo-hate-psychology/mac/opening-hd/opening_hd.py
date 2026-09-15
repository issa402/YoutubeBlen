"""Native-HD original documentary opening for Blender 4.5/5.2; no assets."""
import argparse
import json
import math
import sys
import time
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sequence_spec import load_manifest, safe_output, shot_at
from hd_spec import render_fingerprint, remaining_frames, select_eevee_engine, validate_png

DIAGNOSTICS = (1, 178, 356, 357, 464, 571, 572, 646, 720)


def mat(name, rgb, metal=0, rough=.35, emission=0):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    shader = material.node_tree.nodes['Principled BSDF']
    for key, value in [('Base Color', (*rgb, 1)), ('Metallic', metal), ('Roughness', rough),
                       ('Emission Color', (*rgb, 1)), ('Emission Strength', emission)]:
        shader.inputs[key].default_value = value
    material.diffuse_color = (*rgb, 1)
    return material


def finish(obj, name, material, parent=None):
    obj.name = name
    if material:
        obj.data.materials.append(material)
    if parent:
        obj.parent = parent
    if obj.type == 'MESH':
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
    return obj


def empty(name, location, parent=None):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj.location, obj.parent = location, parent
    return obj


def box(name, pos, dims, material, bevel=.03, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    obj = bpy.context.object
    obj.scale = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        modifier = obj.modifiers.new('Rounded machined edges', 'BEVEL')
        modifier.width, modifier.segments = bevel, 3
        modifier = obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return finish(obj, name, material, parent)


def ellipsoid(name, pos, scales, material, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=1, location=pos)
    obj = bpy.context.object
    obj.scale = scales
    return finish(obj, name, material, parent)


def cylinder(name, pos, bottom, top, depth, material, parent=None):
    bpy.ops.mesh.primitive_cone_add(vertices=40, radius1=bottom, radius2=top, depth=depth, location=pos)
    obj = finish(bpy.context.object, name, material, parent)
    bevel = obj.modifiers.new('Edge softness', 'BEVEL')
    bevel.width, bevel.segments = .018, 3
    obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj


def label(name, body, pos, size, material, parent=None, align='CENTER'):
    data = bpy.data.curves.new(name, 'FONT')
    data.body, data.size, data.align_x = body, size, align
    data.extrude, data.bevel_depth, data.resolution_u = .0005, .0003, 4
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location, obj.rotation_euler = pos, (math.pi / 2, 0, 0)
    return finish(obj, name, material, parent)


def curve(name, points, radius, material, parent=None, closed=False):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions, data.resolution_u = '3D', 1
    data.bevel_depth, data.bevel_resolution = radius, 2
    spline = data.splines.new('POLY')
    spline.points.add(len(points) - 1)
    for point, position in zip(spline.points, points):
        point.co = (*position, 1)
    spline.use_cyclic_u = closed
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    return finish(obj, name, material, parent)


def keyframes(obj, attribute, values):
    for frame, value in values:
        setattr(obj, attribute, value)
        obj.keyframe_insert(attribute, frame=frame)


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


def area(name, pos, target, energy, color, size=5):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy, data.color, data.size = energy, color, size
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = pos
    aim(obj, target)
    return obj


def camera(name, start, end, poses, target, lens=48):
    bpy.ops.object.camera_add(location=poses[0])
    obj = bpy.context.object
    obj.name, obj.data.lens = name, lens
    obj.data.clip_end = 90
    for frame, pos in zip((start, end), poses):
        obj.location = pos
        aim(obj, target)
        obj.keyframe_insert('location', frame=frame)
        obj.keyframe_insert('rotation_euler', frame=frame)
    marker = bpy.context.scene.timeline_markers.new(name, frame=start)
    marker.camera = obj
    return obj


def athlete(name, pos, material, trim, start, end, phase=0, cheer=False):
    """Faceless stylized athlete, shoulder/elbow pivots and fixed shoes; +Z up, -Y forward."""
    root = empty(name, pos)
    chest = cylinder(name + ' tapered jersey', (0, 0, 1.39), .24, .37, .63, material, root)
    chest.scale.y = .58
    ellipsoid(name + ' hips', (0, 0, 1.02), (.27, .175, .20), material, root)
    ellipsoid(name + ' neck', (0, 0, 1.82), (.10, .10, .16), material, root)
    ellipsoid(name + ' faceless head', (0, -.018, 2.03), (.18, .162, .235), material, root)
    box(name + ' chest band', (0, -.207, 1.51), (.34, .019, .025), trim, .009, root)
    for side in (-1, 1):
        x = side * .167
        ellipsoid(name + f' thigh {side}', (x, 0, .805), (.138, .142, .282), material, root)
        ellipsoid(name + f' knee {side}', (x, -.007, .575), (.115, .12, .115), material, root)
        cylinder(name + f' calf {side}', (x, .007, .365), .073, .108, .38, material, root)
        ellipsoid(name + f' shoe {side}', (x, -.098, .100), (.113, .223, .1), trim, root)
        shoulder = empty(name + f' shoulder {side}', (side * .36, 0, 1.65), root)
        ellipsoid(name + f' shoulder cap {side}', (0, 0, -.02), (.135, .138, .148), material, shoulder)
        ellipsoid(name + f' upper arm {side}', (0, 0, -.195), (.105, .109, .207), material, shoulder)
        elbow = empty(name + f' elbow {side}', (0, 0, -.37), shoulder)
        ellipsoid(name + f' elbow cap {side}', (0, 0, 0), (.082, .087, .088), material, elbow)
        cylinder(name + f' forearm {side}', (0, 0, -.14), .058, .079, .28, material, elbow)
        ellipsoid(name + f' hand {side}', (0, -.015, -.332), (.064, .054, .082), material, elbow)
        values = []
        elbows = []
        for fraction in (0, .25, .5, .75, 1):
            frame = round(start + fraction * (end - start))
            pulse = math.sin(2 * math.pi * fraction + phase + side * .3)
            rotation = -side * (2.05 + .30 * pulse) if cheer else -side * (.12 + .09 * pulse)
            values.append((frame, (-.08 if cheer else 0, rotation, 0)))
            elbows.append((frame, (-.34 - .22 * pulse if cheer else -.11, 0, 0)))
        keyframes(shoulder, 'rotation_euler', values)
        keyframes(elbow, 'rotation_euler', elbows)
    return root


def football(name, position, radius, gold, seam):
    """Truncated-icosahedron seam topology projected onto a smooth sphere."""
    root = empty(name, position)
    ellipsoid(name + ' shell', (0, 0, 0), (radius,) * 3, gold, root)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1)
    temporary = bpy.context.object
    vertices = [v.co.copy() for v in temporary.data.vertices]
    triangles = [tuple(p.vertices) for p in temporary.data.polygons]
    bpy.data.objects.remove(temporary, do_unlink=True)
    paths = []
    for tri in triangles:
        a, b, c = tri
        paths.append([(a, b), (b, a), (b, c), (c, b), (c, a), (a, c)])
    seen = set()
    for face in paths:
        points = [(vertices[a] * 2 + vertices[b]).normalized() for a, b in face]
        for index, point in enumerate(points):
            other = points[(index + 1) % len(points)]
            edge = tuple(sorted((tuple(round(v, 4) for v in point), tuple(round(v, 4) for v in other))))
            if edge in seen:
                continue
            seen.add(edge)
            samples = [(point.lerp(other, i / 5).normalized() * (radius + .001)) for i in range(6)]
            curve(name + f' seam {len(seen):02}', samples, radius * .009, seam, root)
    return root


def environment(offset, materials):
    box(f'Stage {offset}', (offset, 0, -.16), (16, 12, .32), materials['floor'], .04)
    box(f'Back wall {offset}', (offset, 3.8, 2.6), (15, .25, 5.5), materials['wall'], .08)
    for side, color in ((-1, 'redlight'), (1, 'cyanlight')):
        box(f'Edge light {offset} {side}', (offset + side * 5.3, 3.55, 2.6), (.034, .055, 4.7), materials[color], .005)
        area(f'Color rim {offset} {side}', (offset + side * 3.7, 2.7, 3.3), (offset, 0, 1.6),
             950, (1, .085, .028) if side < 0 else (.025, .55, 1), 3)
    area(f'Key softbox {offset}', (offset - 2, -4.5, 6), (offset, 0, 1.7), 1150, (.72, .82, 1), 5)
    area(f'Top softbox {offset}', (offset + 2, .4, 6), (offset, 0, 1), 950, (1, .86, .65), 4)
    for index in range(9):
        x = offset - 6 + index * 1.5
        box(f'Architecture fin {offset} {index}', (x, 3.53, 2.6), (.035, .13, 5), materials['metal'], .008)


def notification(materials):
    box('Feed frame', (0, .25, 2.45), (6.85, .31, 4.15), materials['metal'], .16)
    box('Feed glass', (0, .044, 2.45), (6.66, .08, 3.97), materials['wall'], .12)
    label('Feed context', 'A HYPOTHETICAL FEED', (0, -.026, 4.06), .19, materials['cyanlight'])
    label('Feed title', 'THE RIVAL', (0, -.036, 3.47), .63, materials['white'])
    label('Feed premise', 'BECOMES THE MAIN CHARACTER', (0, -.036, 3.13), .22, materials['white'])
    for index, (body, color) in enumerate((('A GREAT GOAL', 'cyanlight'), ('A MISSED CHANCE', 'redlight'), ('THE REACTION', 'gold'))):
        z = 2.64 - index * .64
        card = empty(f'Card {index}', (0, -.18, z))
        box(f'Card {index} plate', (0, 0, 0), (5.75, .10, .49), materials['card'], .055, card)
        box(f'Card {index} accent', (-2.7, -.061, 0), (.035, .012, .30), materials[color], .005, card)
        label(f'Card {index} label', body, (-2.48, -.069, -.085), .255, materials['white'], card, 'LEFT')
        label(f'Card {index} number', f'0{index + 1}', (2.43, -.069, -.07), .22, materials[color], card)
        keyframes(card, 'location', [(1, (-.23 + index * .12, -.18, z)), (178, (.15 - index * .05, -.18, z)), (356, (0, -.18, z))])
    for index in range(13):
        root = empty(f'Attention pulse {index}', (-2.52 + index * .42, -.33, .62))
        bar = box(f'Attention bar {index}', (0, 0, .1), (.11, .05, .2), materials['cyanlight'], .01, root)
        keyframes(root, 'scale', [(1, (1, 1, .6 + .3 * (index % 3))), (178, (1, 1, .8 + .4 * (index % 4))), (356, (1, 1, .7))])
    return camera('notification', 1, 356, [(.5, -10.9, 3.5), (-.38, -10.6, 3.35)], (0, 0, 2.35), 48)


def status(materials):
    x = 20.65
    cylinder('Plinth base', (x, 0, .13), 1.15, 1.15, .26, materials['metal'])
    cylinder('Plinth pedestal', (x, 0, .67), .92, .84, .86, materials['wall'])
    cylinder('Plinth luminous ring', (x, 0, 1.105), .84, .84, .025, materials['goldlight'])
    cylinder('Trophy foot', (x, 0, 1.18), .36, .28, .12, materials['gold'])
    cylinder('Trophy neck', (x, 0, 1.53), .12, .17, .64, materials['gold'])
    for side in (-1, 1):
        curve(f'Trophy cradle {side}', [(x + side * .08, 0, 1.3), (x + side * .34, 0, 1.6),
              (x + side * .40, 0, 1.90), (x + side * .3, 0, 2.03)], .055, materials['gold'])
    trophy = football('Status football', (x, 0, 2.17), .56, materials['gold'], materials['seam'])
    keyframes(trophy, 'rotation_euler', [(357, (.10, .1, 0)), (571, (.1, .1, math.pi * 1.15))])
    athlete('Ambition athlete', (18.0, .2, 0), materials['red'], materials['metal'], 357, 571)
    label('Status title', 'THE WHOLE PACKAGE', (20, 1.5, 3.6), .39, materials['white'])
    label('Status categories', 'TALENT   /   STATUS   /   SELF-BELIEF', (20, 1.49, 3.15), .20, materials['goldlight'])
    pulse = area('Trophy light', (21, -3, 4), (x, 0, 2.1), 1000, (1, .66, .26), 2.5)
    keyframes(pulse.data, 'energy', [(357, 900), (464, 1300), (571, 1050)])
    camera('status', 357, 571, [(23, -10.8, 3.7), (21.7, -10.0, 3.2)], (19.75, 0, 1.95), 48)


def rivalry(materials):
    for side, color in ((-1, 'red'), (1, 'cyan')):
        for index in range(3):
            x = 40 + side * (1.48 + index * 1.00)
            athlete(f'{color} supporter {index}', (x, index * .22, 0), materials[color], materials['metal'],
                    572, 720, phase=index * 1.2, cheer=True)
        box(f'{color} camp line', (40 + side * 2.5, 1.5, .018), (3.9, .065, .035), materials[color + 'light'], .008)
    ball = football('Attention football', (37.5, -.3, 3.03), .20, materials['gold'], materials['seam'])
    keyframes(ball, 'location', [(572, (37.5, -.3, 3.03)), (646, (40, -.1, 3.18)), (720, (42.5, -.3, 3.03))])
    keyframes(ball, 'rotation_euler', [(572, (0, 0, 0)), (720, (math.pi * 2, math.pi, 0))])
    label('Rivalry title', 'WHO ARE YOU REALLY WATCHING?', (40, 1.7, 3.93), .33, materials['white'])
    camera('rivalry', 572, 720, [(40.4, -12.9, 4.3), (39.5, -12.45, 3.9)], (40, 0, 2.03), 46)


def build(manifest):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    engine_ids = {item.identifier for item in scene.render.bl_rna.properties['engine'].enum_items}
    scene.render.engine = select_eevee_engine(engine_ids)
    scene.eevee.taa_render_samples = manifest.get('samples', 16)
    scene.render.fps, scene.frame_start, scene.frame_end = 24, 1, 720
    scene.render.resolution_x, scene.render.resolution_y = manifest['resolution']
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode, scene.render.image_settings.color_depth = 'RGB', '8'
    scene.render.image_settings.compression = 20
    scene.render.film_transparent = False
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.007, .012, .025, 1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .3
    scene.view_settings.view_transform = 'AgX'
    materials = {'floor': mat('Graphite floor', (.018, .024, .036), .45, .30),
        'wall': mat('Midnight panels', (.008, .014, .024), .20, .40),
        'metal': mat('Brushed titanium', (.095, .12, .15), .72, .27),
        'card': mat('Feed card face', (.027, .045, .07), .08, .42),
        'white': mat('Warm white typography', (.90, .94, 1), emission=.65),
        'red': mat('Crimson jersey', (.52, .013, .025), .25, .28),
        'cyan': mat('Cobalt jersey', (.009, .32, .58), .28, .28),
        'gold': mat('Champagne gold', (.84, .43, .08), .86, .23),
        'seam': mat('Inset bronze seam', (.07, .025, .003), .6, .35),
        'redlight': mat('Coral light', (1, .09, .047), emission=1.6),
        'cyanlight': mat('Ice blue light', (.035, .60, 1), emission=1.5),
        'goldlight': mat('Gold light', (1, .58, .17), emission=1.1)}
    for offset in (0, 20, 40):
        environment(offset, materials)
    first = notification(materials)
    status(materials)
    rivalry(materials)
    scene.camera = first
    scene.frame_set(1)
    return scene


def inspect(scene, manifest):
    samples = []
    foot_objects = [obj for obj in scene.objects if ' shoe ' in obj.name]
    for frame in DIAGNOSTICS:
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        card = bpy.data.objects['Card 0']
        text = bpy.data.objects['Card 0 label']
        feet = {obj.name: [round((obj.matrix_world @ Vector(corner)).z, 6) for corner in obj.bound_box]
                for obj in foot_objects}
        samples.append({'frame': frame, 'camera': scene.camera.name, 'shot': shot_at(frame),
            'camera_location': list(scene.camera.location),
            'card_world': list(card.matrix_world.translation),
            'label_parent': text.parent.name,
            'label_local': list(text.location),
            'label_world': list(text.matrix_world.translation),
            'trophy_rotation': list(bpy.data.objects['Status football'].rotation_euler),
            'ball_world': list(bpy.data.objects['Attention football'].matrix_world.translation),
            'shoulder_rotation': list(bpy.data.objects['cyan supporter 1 shoulder 1'].rotation_euler),
            'elbow_rotation': list(bpy.data.objects['cyan supporter 1 elbow 1'].rotation_euler),
            'cheering_elbow_outside_shoulder': all(side * (
                bpy.data.objects[f'cyan supporter 1 elbow {side}'].matrix_world.translation.x
                - bpy.data.objects[f'cyan supporter 1 shoulder {side}'].matrix_world.translation.x) > .1
                for side in (-1, 1)),
            'ground_clearance': {name: min(values) for name, values in feet.items()}})
    assert all(s['camera'] == s['shot'] for s in samples), 'Camera cut mismatch'
    assert min(min(s['ground_clearance'].values()) for s in samples) >= -.002, 'Shoe ground penetration'
    assert len({json.dumps(s['ground_clearance']) for s in samples}) == 1, 'Planted shoe height changed'
    assert all(s['label_parent'] == 'Card 0' for s in samples), 'Card label detached'
    assert all(s['cheering_elbow_outside_shoulder'] for s in samples), 'Cheering arms rotate inward'
    assert len({json.dumps(s['label_local']) for s in samples}) == 1, 'Card label slides locally'
    for key in ('camera_location', 'card_world', 'label_world', 'trophy_rotation', 'ball_world', 'shoulder_rotation', 'elbow_rotation'):
        assert len({json.dumps(s[key]) for s in samples}) > 1, f'Missing {key} motion'
    assert [scene.render.resolution_x, scene.render.resolution_y] == manifest['resolution']
    assert scene.render.resolution_percentage == 100 and scene.frame_end == 720 and scene.render.fps == 24
    scene.frame_set(1)
    return {'valid': True, 'blender_version': bpy.app.version_string, 'native_resolution': manifest['resolution'],
        'fps': 24, 'frame_range': [1, 720], 'cuts': [1, 357, 572], 'render_complete': False,
        'external_assets': [], 'world_up': '+Z', 'character_forward': '-Y', 'ground_z': 0,
        'character_type': 'original faceless stylized athletes; articulated object hierarchy, no real likenesses',
        'motion_samples': samples, 'inventory': {kind: sum(o.type == kind for o in scene.objects)
        for kind in ('MESH', 'FONT', 'CURVE', 'EMPTY', 'CAMERA', 'LIGHT', 'ARMATURE')}}


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', required=True)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--preview', action='store_true')
    modes.add_argument('--render', action='store_true')
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    path = Path(args.manifest).resolve()
    manifest = load_manifest(path)
    if type(manifest.get('samples', 16)) is not int or not 1 <= manifest.get('samples', 16) <= 128:
        raise ValueError('samples must be an integer from 1 through 128')
    if args.resume and not args.render:
        raise ValueError('--resume requires --render')
    fingerprint = render_fingerprint([Path(__file__), Path(__file__).with_name('hd_spec.py'),
                                      Path(__file__).with_name('sequence_spec.py')], manifest)
    folder = safe_output(path.parent, manifest['output'])
    ledger = safe_output(path.parent, 'render-state.json')
    todo = remaining_frames(folder, ledger, fingerprint, manifest['resolution'], args.resume) if args.render else []
    scene = build(manifest)
    report = inspect(scene, manifest)
    report['fingerprint'] = fingerprint
    report_path = safe_output(path.parent, 'motion-report.json')
    write_json(report_path, report)
    bpy.ops.wm.save_as_mainfile(filepath=str(safe_output(path.parent, 'opening-hd.blend')))
    if args.preview:
        folder = safe_output(path.parent, 'previews')
        todo = DIAGNOSTICS
        if folder.exists() and any(folder.iterdir()):
            raise FileExistsError('Preview folder contains files; preserve it and use a fresh packet')
    completed = sorted(set(range(1, 721)) - set(todo)) if args.render else []
    folder.mkdir(parents=True, exist_ok=True)
    began = time.monotonic()
    for frame in todo:
        output = folder / f'frame_{frame:04}.png'
        if output.exists():
            raise FileExistsError(f'Refusing to overwrite {output}')
        scene.frame_set(frame)
        scene.render.filepath = str(output)
        bpy.ops.render.render(write_still=True)
        validate_png(output, manifest['resolution'])
        completed.append(frame)
        if args.render:
            write_json(ledger, {'fingerprint': fingerprint, 'completed': sorted(completed),
                               'resolution': manifest['resolution'], 'fps': 24})
        print(json.dumps({'frame_complete': frame, 'elapsed_seconds': round(time.monotonic() - began, 2)}), flush=True)
    report.update({'render_complete': args.render and len(completed) == 720,
                   'preview_complete': args.preview and len(completed) == 9,
                   'rendered_frames': sorted(completed), 'elapsed_seconds': round(time.monotonic() - began, 2)})
    write_json(report_path, report)
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
