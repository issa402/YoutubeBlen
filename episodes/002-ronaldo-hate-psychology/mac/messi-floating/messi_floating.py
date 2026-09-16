"""Original 2.5D Messi illustration and animated city. Blender 4.5 / 5.2.

Art consists of editable colored polygon layers, ink curves and a deforming cape.
No downloaded likeness, textures, fonts, plugins or simulation caches required.
"""
import argparse
import json
import math
from pathlib import Path
import random
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from floating_spec import FRAME_END, FPS, PREVIEWS, pose_at
from hd_spec import remaining_frames, render_fingerprint, select_eevee_engine, validate_png

COLORS = {'ink': '#172631', 'skin': '#edba91', 'shade': '#c58566',
          'light': '#ffdbb2', 'hair': '#352c29', 'hairlight': '#514035',
          'beard': '#684939', 'white': '#f1f4e9', 'blue': '#77bdd7',
          'blueshade': '#458fae', 'navy': '#233a51', 'gold': '#e2bb69',
          'cape': '#438cae', 'capeshade': '#28607e', 'capelight': '#78bcd0',
          'sky': '#a8c4d3', 'cloud': '#d6e2df', 'cloudlight': '#e6eae2'}
MATS = {}
ROOT = None


def material(name, color):
    if name in MATS:
        return MATS[name]
    rgb = [int(color[i:i+2], 16) / 255 for i in (1, 3, 5)]
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*rgb, 1)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    emit = nodes.new('ShaderNodeEmission')
    # Convert display sRGB to linear so Standard view preserves the palette.
    emit.inputs['Color'].default_value = tuple(v / 12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb) + (1,)
    out = nodes.new('ShaderNodeOutputMaterial')
    mat.node_tree.links.new(emit.outputs[0], out.inputs['Surface'])
    MATS[name] = mat
    return mat


def ink(name, points, y=-.1, width=.018, color='ink', parent=None, closed=False):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 1
    curve.bevel_depth = width
    curve.resolution_u = 2
    curve.bevel_resolution = 1
    spline = curve.splines.new('POLY')
    spline.points.add(len(points)-1)
    for p, (x, z) in zip(spline.points, points):
        p.co = (x, y, z, 1)
    spline.use_cyclic_u = closed
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(MATS[color])
    obj.parent = parent
    return obj


def shape(name, points, color, y=0, parent=None, outline=True, width=.018):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([(x, y, z) for x, z in points], [], [list(range(len(points)))])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(MATS[color])
    obj.parent = parent
    if outline:
        ink(name+' ink', points, y-.004, width, parent=parent, closed=True)
    return obj


def oval(name, x, z, rx, rz, color, y=0, parent=None, outline=True):
    return shape(name, [(x+rx*math.cos(a*math.tau/40), z+rz*math.sin(a*math.tau/40)) for a in range(40)], color, y, parent, outline)


def rect(name, x, z, w, h, color, y=0, parent=None, outline=False):
    return shape(name, [(x,z),(x+w,z),(x+w,z+h),(x,z+h)], color,y,parent,outline)


def empty(name):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    return obj


def city():
    rect('Sky', -40,-20,80,50,'sky',30)
    randomizer = random.Random(10)
    for n in range(18):
        x, z = randomizer.uniform(-18,18), randomizer.uniform(4,10)
        for j in range(4):
            oval(f'Cloud {n} {j}', x+j*.65,z+randomizer.uniform(-.2,.2),1.4,.35,
                 'cloudlight' if j==2 else 'cloud', 24-j*.01, outline=False)
    palettes = [('far','#89a7b6','#adc8d1','#7796a8'),
                ('middle','#688c9f','#9fbfcb','#567b90'),
                ('near','#3e657e','#78a7bc','#2a4f68')]
    for layer,(name,base,glass,side) in enumerate(palettes):
        for key,col in ((name,base),(name+'glass',glass),(name+'side',side)):
            material(key,col)
        group = empty(name+' skyline')
        y = 16-layer*5
        for n in range(11):
            x = -18+n*3.4+randomizer.uniform(-.3,.3)
            w = randomizer.uniform(2.2,3.3)
            # Flanking towers frame an open central sky corridor.
            top = randomizer.uniform(3.8,7.5) if abs(x)>3.5 else randomizer.uniform(-.1,1.5)
            bottom = -7
            rect(f'{name} tower {n}',x,bottom,w,top-bottom,name,y,parent=group)
            shape(f'{name} side {n}',[(x+w,bottom),(x+w+.45,bottom),(x+w+.45,top+.22),(x+w,top)],name+'side',y-.01,group,False)
            shape(f'{name} roof {n}',[(x,top),(x+.45,top+.22),(x+w+.45,top+.22),(x+w,top)],name+'glass',y-.02,group,False)
            for row in range(int((top-bottom)/.48)):
                for col in range(int(w/.42)):
                    rect(f'{name} window {n} {row} {col}',x+.10+col*.42,bottom+.12+row*.48,.27,.32,
                         name+'glass' if (row+col)%5 else name+'side',y-.03,parent=group)
            rect(f'{name} crown {n}',x,top-.12,w,.07,name+'side',y-.05,parent=group)
        for frame in (1,FRAME_END):
            group.location.x = (frame-1)/(FRAME_END-1) * (.15+layer*.26)
            group.keyframe_insert('location',frame=frame)


def figure():
    root = empty('Messi hover root')
    # All artwork is front-facing -Y, with Z up. Layers use real depth offsets.
    def p(name,pts,c,y=0):
        return shape(name,pts,c,y,root)
    def line(name,pts,y=-.4,w=.014,c='ink'):
        return ink(name,pts,y,w,c,root)
    # Tapered, slightly asymmetrical airborne legs and relaxed gold boots.
    p('Left leg', [(-.61,3),(-.06,2.95),(-.10,2.1),(-.23,1.4),(-.33,.79),(-.65,.79),(-.68,1.5),(-.77,2.12)], 'skin',-.02)
    p('Right leg',[(.05,2.95),(.61,3),(.7,2.2),(.55,1.63),(.46,.72),(.16,.70),(.1,1.7),(-.04,2.12)],'skin',-.03)
    p('Left sock',[(-.69,1.56),(-.24,1.52),(-.32,.63),(-.65,.61)],'white',-.06)
    p('Right sock',[(.1,1.47),(.58,1.5),(.48,.57),(.2,.53)],'white',-.065)
    p('Left sock stripe',[(-.68,1.4),(-.26,1.37),(-.27,1.28),(-.67,1.3)],'blue',-.08)
    p('Right sock stripe',[(.13,1.32),(.55,1.35),(.54,1.24),(.14,1.22)],'blue',-.085)
    p('Left boot',[(-.65,.78),(-.33,.75),(-.28,.41),(-.4,.11),(-.6,.12),(-.71,.26),(-.72,.5)],'gold',-.12)
    p('Right boot',[(.2,.67),(.48,.69),(.60,.40),(.83,.26),(.87,.11),(.48,.06),(.30,.18)],'gold',-.13)
    line('Left boot laces',[(-.61,.49),(-.38,.45),(-.60,.39),(-.41,.34)],-.15,.009)
    line('Right boot laces',[(.42,.44),(.62,.32),(.44,.31),(.68,.22)],-.16,.009)
    p('Shorts',[(-.74,3.42),(.73,3.42),(.77,2.6),(.12,2.47),(0,2.87),(-.13,2.48),(-.78,2.62)],'navy',-.16)
    line('Shorts seam',[(0,3.22),(0,2.89)],-.19)
    line('Shorts left trim',[(-.65,3.28),(-.66,2.74)],-.19,.025,'white')
    line('Shorts right trim',[(.63,3.28),(.65,2.74)],-.19,.025,'white')
    # Shirt silhouette and clipped sky-blue panels.
    p('Jersey',[(-.34,5.25),(-.92,5.06),(-1.08,4.79),(-.95,4.27),(-.74,4.19),(-.68,3.3),(.69,3.3),(.76,4.19),(.98,4.27),(1.08,4.79),(.92,5.06),(.34,5.25)],'white',-.20)
    p('Left jersey stripe',[(-.65,5.13),(-.32,5.25),(-.29,3.32),(-.61,3.32)],'blue',-.22)
    p('Right jersey stripe',[(.28,5.25),(.62,5.14),(.61,3.32),(.29,3.32)],'blue',-.22)
    line('Jersey hem',[(-.66,3.42),(0,3.39),(.67,3.42)],-.24,.012,'blueshade')
    p('Neck',[(-.28,5.56),(.28,5.56),(.32,5.13),(.17,4.96),(-.14,4.96),(-.33,5.14)],'skin',-.25)
    p('Neck shadow',[(-.28,5.55),(.27,5.55),(.27,5.28),(-.04,5.14),(-.29,5.29)],'shade',-.27)
    line('Collar',[(-.37,5.20),(-.22,4.99),(0,4.93),(.21,4.99),(.37,5.20)],-.30,.035,'navy')
    # Folded arms: continuous contours, elbow bends and overlapping hands.
    p('Rear folded arm',[(-.97,4.74),(-1.03,4.37),(-.88,4.02),(-.65,3.98),(.38,4.42),(.56,4.64),(.42,4.84),(.19,4.78),(-.65,4.36),(-.70,4.78)],'skin',-.34)
    p('Rear arm shadow',[(-1.0,4.36),(-.87,4.07),(-.64,4.04),(.36,4.47),(.39,4.59),(-.64,4.2)],'shade',-.35)
    p('Front folded arm',[(.77,4.82),(1.00,4.69),(1.03,4.33),(.86,4.05),(.65,4.03),(-.43,4.56),(-.64,4.57),(-.77,4.74),(-.69,4.91),(-.44,4.96),(-.22,4.83),(.65,4.39)],'skin',-.39)
    p('Front arm light',[(-.27,4.77),(.68,4.27),(.87,4.26),(.70,4.09),(-.37,4.59)],'shade',-.405)
    line('Left fingertips',[(-.71,4.82),(-.48,4.81),(-.33,4.74)],-.43,.011)
    line('Left fingers',[(-.7,4.75),(-.48,4.72),(-.36,4.65)],-.43,.011)
    line('Thumb',[(-.45,4.92),(-.37,4.83),(-.22,4.80)],-.43,.012)
    line('Right fingers',[(.33,4.64),(.47,4.76),(.43,4.84)],-.44,.013)
    # Restrained abstract tattoo marks on the visible right forearm.
    for i in range(5):
        x=.04+i*.105
        line('Tattoo '+str(i),[(x,4.6-i*.047),(x+.02,4.49-i*.047),(x+.08,4.48-i*.047)],-.44,.008,'beard')
    # Head: recognisable beard, close sides, swept dark hair, compact face.
    oval('Left ear',-.43,5.83,.10,.17,'skin',-.28,root)
    oval('Right ear',.43,5.83,.10,.17,'skin',-.28,root)
    p('Face',[(-.41,6.24),(-.23,6.43),(.16,6.45),(.39,6.28),(.44,5.96),(.38,5.57),(.20,5.36),(-.12,5.34),(-.34,5.53),(-.43,5.94)],'skin',-.31)
    p('Face shadow',[(.30,6.29),(.4,6.22),(.43,5.95),(.37,5.6),(.2,5.4),(.06,5.40),(.21,5.70),(.24,6.05)],'shade',-.325)
    p('Beard',[(-.40,5.91),(-.32,5.71),(-.19,5.66),(-.04,5.74),(.13,5.7),(.3,5.76),(.4,5.96),(.37,5.57),(.23,5.36),(.03,5.29),(-.17,5.35),(-.34,5.53)],'beard',-.35)
    p('Hair',[(-.43,5.96),(-.48,6.23),(-.43,6.47),(-.29,6.53),(-.33,6.64),(-.11,6.60),(.03,6.7),(.19,6.59),(.33,6.62),(.46,6.45),(.46,6.21),(.40,5.99),(.34,6.28),(.16,6.35),(-.09,6.30),(-.31,6.33),(-.34,5.99)],'hair',-.37)
    line('Hair sweep',[(-.33,6.44),(-.14,6.47),(.05,6.51),(.24,6.48)],-.40,.022,'hairlight')
    line('Hair sweep2',[(-.28,6.52),(-.08,6.55),(.09,6.58)],-.40,.015,'hairlight')
    for side in (-1,1):
        x=side*.20
        oval('Eye white '+str(side),x,6.00,.105,.043,'white',-.38,root,False)
        oval('Iris '+str(side),x+.008,6.00,.032,.041,'hair',-.395,root,False)
        oval('Eye glint '+str(side),x-.001,6.014,.009,.012,'white',-.405,root,False)
        line('Brow '+str(side),[(x-.105,6.11),(x-.01,6.14),(x+.094,6.11)],-.42,.025,'hair')
        line('Eye lid '+str(side),[(x-.105,6.01),(x-.02,6.045),(x+.10,6.018)],-.42,.012)
    line('Nose',[(.025,6.03),(.01,5.89),(.07,5.83),(-.025,5.81),(-.065,5.84)],-.42,.012,'beard')
    p('Moustache',[(-.17,5.72),(-.04,5.78),(.03,5.75),(.10,5.77),(.21,5.70),(.15,5.64),(.02,5.68),(-.12,5.65)],'hair',-.42)
    line('Mouth',[(-.11,5.63),(.035,5.61),(.14,5.63)],-.45,.014)
    line('Lower lip',[(-.04,5.57),(.07,5.56)],-.45,.012,'skin')
    for i in range(7):
        x=-.20+i*.065
        line('Beard texture '+str(i),[(x,5.47+abs(x)*.15),(x+.014,5.40+abs(x)*.3)],-.44,.007,'hairlight')
    return root


def cape(root):
    # Independent strips wave coherently; no simulation or frame handlers needed.
    strips=[]
    for i in range(12):
        col = 'capeshade' if i%4==0 else 'capelight' if i%4==2 else 'cape'
        mesh=bpy.data.meshes.new('Cape strip '+str(i))
        mesh.from_pydata([(0,0,0)]*18, [], [(j*2,j*2+1,j*2+3,j*2+2) for j in range(8)])
        mesh.update()
        obj=bpy.data.objects.new(mesh.name,mesh)
        bpy.context.collection.objects.link(obj)
        obj.parent=root
        mesh.materials.append(MATS[col])
        strips.append(obj)
    for frame in range(1,FRAME_END+1):
        phase=pose_at(frame)['cape_phase']
        for i,obj in enumerate(strips):
            for row in range(9):
                v=row/8
                for edge in (0,1):
                    u=(i+edge)/12
                    x=(u-.5)*(1.32+1.8*v)+.22*math.sin(phase-v*3)*v
                    z=5.19-4.35*v+.15*math.sin(phase+u*5-v*2)*v*v
                    y=.25+.13*math.sin(u*math.tau*2+phase-v*2)*v
                    vert=obj.data.vertices[row*2+edge]
                    vert.co=(x,y,z)
                    vert.keyframe_insert('co',frame=frame)
    return strips


def build(resolution):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    MATS.clear()
    for name,col in COLORS.items():
        material(name,col)
    scene=bpy.context.scene
    scene.render.engine=select_eevee_engine(i.identifier for i in scene.render.bl_rna.properties['engine'].enum_items)
    scene.eevee.taa_render_samples=16
    scene.render.resolution_x,scene.render.resolution_y=resolution
    scene.render.resolution_percentage=100
    scene.render.fps=FPS
    scene.frame_start,scene.frame_end=1,FRAME_END
    scene.render.image_settings.file_format='PNG'
    scene.render.image_settings.color_mode='RGB'
    scene.render.image_settings.color_depth='8'
    scene.view_settings.view_transform='Standard'
    scene.view_settings.look='None'
    scene.world.color=(.4,.5,.6)
    city()
    root=figure()
    strips=cape(root)
    bpy.ops.object.camera_add(location=(0,-25,3.5))
    camera=bpy.context.object
    camera.name='Opening camera'
    camera.rotation_euler=(Vector((0,0,3.5))-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type='ORTHO'
    camera.data.clip_end=100
    camera.data.passepartout_alpha=1
    scene.camera=camera
    for frame in range(1,FRAME_END+1):
        pose=pose_at(frame)
        root.location.z=pose['height']
        root.keyframe_insert('location',frame=frame)
        camera.location.x=pose['camera_x']
        camera.keyframe_insert('location',frame=frame)
        camera.data.ortho_scale=pose['camera_scale']
        camera.data.keyframe_insert('ortho_scale',frame=frame)
    scene.render.filepath='//frames/frame_'
    scene.sync_mode='FRAME_DROP'
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                space=area.spaces.active
                space.region_3d.view_perspective='CAMERA'
                space.overlay.show_overlays=False
                space.show_gizmo=False
                space.shading.type='MATERIAL'
                space.region_3d.view_camera_zoom=10
    bpy.ops.object.select_all(action='DESELECT')
    scene.frame_set(1)
    return scene,root,strips


def inspect(scene,root,strips):
    samples=[]
    for frame in PREVIEWS:
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        points=[root.matrix_world@Vector(v.co) for obj in strips for v in obj.data.vertices]
        sample={'frame':frame,'root_z':root.location.z,'camera_x':scene.camera.location.x,
                'camera_scale':scene.camera.data.ortho_scale,'cape_tip':list(points[-1]),
                'cape_bounds_z':[min(p.z for p in points),max(p.z for p in points)]}
        samples.append(sample)
    assert max(s['root_z'] for s in samples)-min(s['root_z'] for s in samples)>.1
    assert len({tuple(s['cape_tip']) for s in samples})>1
    assert samples[0]['camera_scale']>samples[-1]['camera_scale']
    assert all(s['cape_bounds_z'][0]>.3 for s in samples)
    assert all(o.parent==root for o in strips)
    scene.frame_set(1)
    return {'validated':True,'format':'layered 2.5D cel illustration, not a sculpted 3D likeness',
            'subject':'stylized Messi in fictional superhero pose','fps':FPS,'frames':FRAME_END,
            'resolution':[scene.render.resolution_x,scene.render.resolution_y],
            'world_up':'+Z','character_forward':'-Y','samples':samples,
            'external_assets':[],'render_complete':False,'object_count':len(scene.objects)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--resolution',type=int,nargs=2,default=[1920,1080])
    modes=parser.add_mutually_exclusive_group()
    modes.add_argument('--preview',action='store_true')
    modes.add_argument('--render',action='store_true')
    parser.add_argument('--resume',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    if any(not 64<=n<=4096 for n in args.resolution):
        parser.error('resolution dimensions must be between 64 and 4096')
    if args.resume and not args.render:
        parser.error('--resume requires --render')
    out=args.output.resolve()
    out.mkdir(parents=True,exist_ok=True)
    fingerprint=render_fingerprint([Path(__file__),Path(__file__).with_name('floating_spec.py'),Path(__file__).with_name('hd_spec.py')],{'resolution':args.resolution,'frames':FRAME_END})
    folder=out/('previews' if args.preview else 'frames')
    ledger=out/'render-state.json'
    todo=remaining_frames(folder,ledger,fingerprint,args.resolution,args.resume,end=FRAME_END) if args.render else list(PREVIEWS) if args.preview else []
    if args.preview and folder.exists() and any(folder.iterdir()):
        raise FileExistsError('Preview files exist; choose a fresh --output directory')
    scene,root,strips=build(args.resolution)
    report=inspect(scene,root,strips)
    report['fingerprint']=fingerprint
    report_path=out/'motion-report.json'
    report_path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'messi-floating.blend'))
    completed=sorted(set(range(1,FRAME_END+1))-set(todo)) if args.render else []
    if todo:
        folder.mkdir(exist_ok=True)
    for frame in todo:
        scene.frame_set(frame)
        path=folder/f'frame_{frame:04}.png'
        if path.exists():
            raise FileExistsError(f'Refusing to overwrite {path}')
        scene.render.filepath=str(path)
        bpy.ops.render.render(write_still=True)
        validate_png(path,args.resolution)
        completed.append(frame)
        if args.render:
            ledger.write_text(json.dumps({'fingerprint':fingerprint,'completed':sorted(completed)}),encoding='utf-8')
        print(f'Completed frame {frame}/{FRAME_END}',flush=True)
    report.update(render_complete=args.render and len(completed)==FRAME_END,rendered_frames=completed)
    report_path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report),flush=True)


if __name__=='__main__':
    main()
