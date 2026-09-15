"""Original three-shot documentary opening; Blender 4.5, no external assets."""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sequence_spec import SHOTS, load_manifest, safe_output, shot_at


def material(name, color, metallic=0, emission=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    for key, value in [('Base Color', (*color, 1)), ('Metallic', metallic),
                       ('Roughness', .32), ('Emission Color', (*color, 1)),
                       ('Emission Strength', emission)]:
        shader.inputs[key].default_value = value
    return mat


def cube(name, location, scale, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name, obj.scale = name, scale
    obj.data.materials.append(mat)
    if bevel:
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        modifier = obj.modifiers.new('Soft edges', 'BEVEL')
        modifier.width, modifier.segments = bevel, 3
    return obj


def sphere(name, location, radius, mat):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=radius, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def text(name, body, location, size, mat, align='CENTER'):
    data = bpy.data.curves.new(name, 'FONT')
    data.body, data.align_x, data.size, data.extrude = body, align, size, .002
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location, obj.rotation_euler = location, (math.pi/2, 0, 0)
    obj.data.materials.append(mat)
    return obj


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


def light(name, location, target, energy, color, size=5):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy, data.color, data.shape, data.size = energy, color, 'DISK', size
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    aim(obj, target)
    return obj


def animate(obj, attribute, frames):
    for frame, value in frames:
        setattr(obj, attribute, value)
        obj.keyframe_insert(attribute, frame=frame)


def person(name, x, y, mat, scene_start, scene_end, cheering=False):
    cube(name+' torso', (x, y, 1.08), (.55, .3, .66), mat, .07)
    sphere(name+' head', (x, y, 1.65), .205, mat)
    for side in (-1, 1):
        cube(name+f' foot {side}', (x+side*.17, y-.06, .105), (.22, .34, .21), mat, .025)
        cube(name+f' leg {side}', (x+side*.17, y, .48), (.19, .24, .64), mat, .04)
        arm = cube(name+f' arm {side}', (x+side*.43, y, 1.12), (.18, .23, .64), mat, .04)
        amplitude = .65 if cheering else .12
        animate(arm, 'rotation_euler', [(scene_start, (0, side*amplitude, 0)),
                ((scene_start+scene_end)//2, (0, side*(amplitude+.6), 0)),
                (scene_end, (0, side*amplitude, 0))])


def camera(name, start, end, positions, target):
    bpy.ops.object.camera_add(location=positions[0])
    obj = bpy.context.object
    obj.name, obj.data.lens = name, 45
    for frame, pos in zip((start, end), positions):
        obj.location = pos
        aim(obj, target)
        obj.keyframe_insert('location', frame=frame)
        obj.keyframe_insert('rotation_euler', frame=frame)
    marker = bpy.context.scene.timeline_markers.new(name, frame=start)
    marker.camera = obj
    return obj


def build(manifest):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.eevee.taa_render_samples = 16
    scene.render.fps = manifest['fps']
    scene.frame_start, scene.frame_end = 1, 720
    scene.render.resolution_x, scene.render.resolution_y = manifest['resolution']
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.film_transparent = False
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.006,.009,.018,1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .25
    scene.view_settings.view_transform = 'AgX'
    mats = {'dark': material('Obsidian', (.012, .018, .03), .35),
            'white': material('Typography', (.85, .92, 1), emission=.4),
            'red': material('Rival red', (.65, .025, .045), .35),
            'cyan': material('Fan cyan', (.018, .46, .72), .35),
            'gold': material('Status gold', (.84, .49, .09), .75),
            'glow': material('Cyan emission', (.015, .5, .8), emission=2),
            'redglow': material('Red emission', (.9, .025, .015), emission=2)}
    for offset in (0, 20, 40):
        cube(f'Stage {offset}', (offset, 0, -.12), (14, 12, .24), mats['dark'])
        light(f'Key {offset}', (offset+3, -4, 6), (offset, 0, 1.5), 1200, (.6, .8, 1))
        light(f'Rim {offset}', (offset-3, 3, 5), (offset, 0, 1.8), 1400, (.12, .5, 1))

    # Shot 1: a clearly invented feed, cards slide and reaction bars rise.
    cube('Feed housing', (0, .2, 2.0), (5.8, .35, 3.7), mats['dark'], .12)
    text('Feed kicker', 'A HYPOTHETICAL FEED', (0, -.025, 3.35), .20, mats['cyan'])
    text('Feed header', 'THE RIVAL', (0, -.03, 2.9), .58, mats['white'])
    text('Feed subheading', 'BECOMES THE MAIN CHARACTER', (0, -.04, 2.51), .185, mats['white'])
    for index, (label, color) in enumerate((('A GREAT GOAL', 'cyan'), ('A MISSED CHANCE', 'red'), ('THE REACTION', 'gold'))):
        z = 1.95-index*.56
        panel = cube(f'Notification card {index}', (0, -.13, z), (4.8, .13, .45), mats[color], .05)
        animate(panel, 'location', [(1, (-.6+index*.25, -.13, z)),
                                   (178, (.15, -.13, z)), (356, (0, -.13, z))])
        text(f'Card title {index}', label, (0, -.24, z-.06), .19, mats['white'])
    for index in range(7):
        bar = cube(f'Reaction bar {index}', (-2.1+index*.7, -.5, .25), (.32, .32, .3), mats['glow'])
        animate(bar, 'scale', [(1, (.32,.32,.2)), (178, (.32,.32,.25+index*.055)), (356, (.32,.32,.2))])
    first = camera('notification', 1, 356, [(.55,-9,3.4),(-.35,-8.6,3.0)], (0,0,1.9))

    # Shot 2: trophy rotation, pulsing gold light and subtle athlete gestures.
    cube('Status plinth', (20, .2, .45), (2.2, 2, .9), mats['dark'], .08)
    cube('Status luminous trim', (20, -.82, .82), (2.1, .025, .035), mats['glow'])
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=.4, radius2=.2, depth=1.1, location=(20,.2,1.4))
    bpy.context.object.name = 'Trophy stem'
    bpy.context.object.data.materials.append(mats['gold'])
    globe = sphere('Rotating trophy', (20,.2,2.25), .56, mats['gold'])
    animate(globe, 'rotation_euler', [(357,(.1,0,0)), (571,(.1,0,math.pi*1.4))])
    person('Ambition silhouette', 17.85, .35, mats['red'], 357,571)
    text('Status title', 'THE WHOLE PACKAGE', (20, .8, 3.55), .37, mats['white'])
    text('Status labels', 'TALENT  /  STATUS  /  SELF-BELIEF', (20,-1.1,.13), .20, mats['gold'])
    spot = light('Gold pulse', (20,-3,5),(20,0,2),900,(1,.52,.12),2)
    animate(spot.data,'energy',[(357,400),(410,1700),(465,750),(520,1700),(571,900)])
    status_camera = camera('status',357,571,[(23.9,-10.4,4),(22.4,-9.7,3.5)],(19.5,0,1.85))
    status_camera.data.lens = 42

    # Shot 3: two symbolic camps; cheering arms and ball cross the divide.
    for side, color in ((-1,'red'),(1,'cyan')):
        for index in range(3):
            person(f'{color} supporter {index}',40+side*(1.15+index*.85), index*.18,
                   mats[color],572,720,cheering=True)
        cube(f'{color} floor strip',(40+side*2,1.15,.01),(3,.06,.02),mats['redglow' if side<0 else 'glow'])
    moving_ball = sphere('Attention ball',(37,0,2.7),.23,mats['gold'])
    animate(moving_ball,'location',[(572,(37,0,2.7)),(646,(40,0,3.2)),(720,(43,0,2.7))])
    animate(moving_ball,'rotation_euler',[(572,(0,0,0)),(720,(math.pi*2,math.pi,0))])
    text('Rivalry title','WHO ARE YOU REALLY WATCHING?',(40,1.6,3.65),.30,mats['white'])
    text('Rivalry footer','WHEN THEIR FAILURE FEELS LIKE YOUR VICTORY',(40,-1.0,.17),.155,mats['gold'])
    camera('rivalry',572,720,[(40.5,-11.4,4.4),(39.3,-10.3,3.7)],(40,0,1.7))
    scene.camera = first
    scene.frame_set(1)
    return scene


def inspect(scene, manifest):
    samples = []
    for frame in (1,178,356,357,464,571,572,646,720):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        foot_objects = [o for o in scene.objects if ' foot ' in o.name]
        foot_floor = min((o.matrix_world @ Vector(corner)).z for o in foot_objects for corner in o.bound_box)
        samples.append({'frame':frame,'shot':shot_at(frame),'camera':scene.camera.name,
            'camera_location':list(scene.camera.location),
            'trophy_rotation':list(bpy.data.objects['Rotating trophy'].rotation_euler),
            'attention_ball':list(bpy.data.objects['Attention ball'].location),
            'notification_card':list(bpy.data.objects['Notification card 0'].location),
            'gold_light_energy':bpy.data.objects['Gold pulse'].data.energy,
            'supporter_arm_rotation':list(bpy.data.objects['cyan supporter 1 arm 1'].rotation_euler),
            'lowest_foot_world_z':round(foot_floor,6)})
    assert all(s['camera']==s['shot'] for s in samples),'Timeline camera cut failed'
    assert min(s['lowest_foot_world_z'] for s in samples)>=-.015,'Feet penetrate floor'
    for key in ('camera_location','trophy_rotation','attention_ball','notification_card','gold_light_energy','supporter_arm_rotation'):
        assert len({json.dumps(s[key]) for s in samples})>1,f'No motion in {key}'
    assert scene.frame_end==720 and scene.render.fps==24
    assert len([o for o in scene.objects if o.type=='CAMERA'])==3
    scene.frame_set(1)
    return {'valid':True,'blender_version':bpy.app.version_string,'duration_seconds':30,
        'fps':24,'frame_range':[1,720],'cuts':[1,357,572],
        'external_assets':[],'character_type':'generic geometric silhouettes; no armatures or real likenesses',
        'world_up':'+Z','character_forward':'-Y','ground_z':0,
        'inventory':{kind:sum(o.type==kind for o in scene.objects) for kind in ('MESH','FONT','CAMERA','LIGHT','ARMATURE')},
        'samples':samples,'render_complete':False,'rendered_frames':[],
        'configured_resolution':manifest['resolution']}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--manifest',required=True)
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--preview',action='store_true')
    mode.add_argument('--render',action='store_true')
    parser.add_argument('--lowres',action='store_true',help='Use manifest preview resolution for all frames')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    path=Path(args.manifest).resolve()
    manifest=load_manifest(path)
    scene=build(manifest)
    report=inspect(scene,manifest)
    root=path.parent
    output=safe_output(root,manifest['output'])
    if args.render and output.exists() and any(output.glob('frame_*.png')):
        raise FileExistsError('Frame output exists; use a fresh packet or preserve/remove previous output explicitly')
    output.mkdir(parents=True,exist_ok=True)
    scene.render.filepath=str(output/'frame_')
    validation=safe_output(root,'motion-report.json')
    validation.write_text(json.dumps(report,indent=2),encoding='utf-8')
    bpy.ops.wm.save_as_mainfile(filepath=str(safe_output(root,'opening-sequence.blend')))
    if args.preview or args.lowres:
        scene.render.resolution_x,scene.render.resolution_y=manifest['preview_resolution']
    report['rendered_resolution']=[scene.render.resolution_x,scene.render.resolution_y]
    if args.preview:
        folder=safe_output(root,'previews')
        folder.mkdir(exist_ok=True)
        for frame in (1,178,356,357,464,571,572,646,720):
            scene.frame_set(frame)
            scene.render.filepath=str(folder/f'frame_{frame:04}.png')
            bpy.ops.render.render(write_still=True)
            report['rendered_frames'].append(frame)
    elif args.render:
        bpy.ops.render.render(animation=True)
        report['rendered_frames']=list(range(1,721))
    report['render_complete']=bool(args.render)
    report['preview_complete']=bool(args.preview)
    validation.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))


if __name__=='__main__':
    main()
