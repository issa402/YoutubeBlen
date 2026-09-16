"""Four-shot football/superhero crossover, recreated from the supplied clip.
Editable 2.5D cel artwork. 192 frames at 24 fps. No external assets.
"""
import argparse
import json
import math
from pathlib import Path
import sys
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import messi_floating as art
from crossover_faces import redraw
from crossover_sprites import sprite
from crossover_spec import FPS, FRAME_END, SHOTS, PREVIEWS, pose_at
from hd_spec import select_eevee_engine, remaining_frames, render_fingerprint, validate_png

PALETTE={'red':'#b72f32','redshade':'#7c202e','redlight':'#e0544c',
 'superblue':'#24699a','superdark':'#174367','green':'#689349','greenshade':'#3c603b',
 'greenlight':'#9fbd66','shell':'#c3a364','shellshade':'#897147','mask':'#4465b6',
 'brownskin':'#af795b','brownlight':'#cb9370','wall':'#34454d','walllight':'#45555c',
 'crack':'#202e36','floor':'#263740','crate':'#66543e','crateshade':'#443e35'}


def poly(name,pts,col,y=0,parent=None):
    return art.shape(name,pts,col,y,parent)


def line(name,pts,y=-.5,width=.014,col='ink',parent=None):
    return art.ink(name,pts,y,width,col,parent)


def delete_parts(root,prefixes):
    for obj in list(root.children):
        if any(obj.name.startswith(p) for p in prefixes):
            bpy.data.objects.remove(obj,do_unlink=True)


def recolor(root,names,color):
    for obj in root.children:
        if obj.type=='MESH' and obj.name in names:
            obj.data.materials.clear()
            obj.data.materials.append(art.MATS[color])


def cape(root,offset,short=False):
    layers=[]
    for i,col in enumerate(('redshade','red','redlight','red','redshade')):
        pts=[(-.65+i*.26,5.15),(-.39+i*.26,5.15),(-.90+i*.52,.65),(-1.42+i*.52,.45)]
        obj=poly('Cape panel '+str(offset)+' '+str(i),pts,col,.3,root)
        # Polygon and ink share the same animated horizontal shear/rotation.
        outline=bpy.data.objects.get(obj.name+' ink')
        layers.append((obj,outline))
    for f in range(1,FRAME_END+1):
        phase=pose_at(f)['cape_phase']
        for i,(obj,outline) in enumerate(layers):
            angle=.065*math.sin(phase+i*.45)
            for item in (obj,outline):
                item.rotation_euler.y=angle
                item.keyframe_insert('rotation_euler',frame=f)
    return [item for pair in layers for item in pair]


def badge(root,superman=False):
    if superman:
        poly('Ronaldo shield',[(-.49,4.93),(.49,4.93),(.62,4.67),(0,4.14),(-.62,4.67)],'gold',-.28,root)
        poly('Shield inset',[(-.36,4.83),(.36,4.83),(.47,4.66),(0,4.27),(-.47,4.66)],'red',-.30,root)
        # An original CR7-themed crest with a geometric seven.
        poly('Seven crest',[(-.23,4.75),(.25,4.75),(.25,4.63),(-.07,4.36),(-.20,4.43),(.09,4.63),(-.23,4.63)],'gold',-.32,root)
    else:
        poly('Omni chest insignia',[(-.49,4.96),(.49,4.96),(.63,4.78),(.5,4.58),(.12,4.58),(.12,3.48),(-.12,3.48),(-.12,4.58),(-.5,4.58),(-.63,4.78)],'red',-.27,root)


def hero(offset,ronaldo=False):
    root=art.figure()
    root.name='Ronaldo Superman' if ronaldo else 'Messi Omni-Man'
    # Capture original semantic names before duplicates get Blender suffixes.
    for obj in root.children:
        if obj.type=='MESH':
            name=obj.name.split('.')[0]
            if name in ('Left leg','Right leg','Shorts'):
                obj.data.materials[0]=art.MATS['superblue' if ronaldo else 'red']
            elif name in ('Jersey',):
                obj.data.materials[0]=art.MATS['superblue' if ronaldo else 'white']
            elif name in ('Left boot','Right boot','Left sock','Right sock'):
                obj.data.materials[0]=art.MATS['red' if ronaldo else 'white']
            elif 'folded arm' in name:
                obj.data.materials[0]=art.MATS['white']
            elif name in ('Rear arm shadow','Front arm light'):
                obj.data.materials[0]=art.MATS['red']
    delete_parts(root,('Left jersey stripe','Right jersey stripe','Shorts left trim','Shorts right trim',
                       'Left sock stripe','Right sock stripe','Tattoo','Left boot laces','Right boot laces'))
    if ronaldo:
        delete_parts(root,('Rear folded arm','Front folded arm','Rear arm shadow','Front arm light',
            'Left fingertips','Left fingers','Right fingers','Thumb','Beard','Moustache','Lower lip'))
        for side in (-1,1):
            pts=[(side*.77,4.99),(side*1.02,4.71),(side*1.09,3.82),(side*.92,3.05),(side*.62,3.08),(side*.71,3.89)]
            poly('Ronaldo arm '+str(side),pts,'superblue',-.34,root)
            poly('Ronaldo fist '+str(side),[(side*.67,3.14),(side*.94,3.17),(side*1.02,2.88),(side*.9,2.65),(side*.64,2.74)],'skin',-.39,root)
            line('Knuckles '+str(side),[(side*.73,2.94),(side*.94,2.96)],-.43,.015,'shade',root)
        art.rect('Super belt',-.69,3.33,1.38,.17,'gold',-.29,root)
        line('Ronaldo jaw',[(-.32,5.60),(-.16,5.41),(.06,5.37),(.24,5.48),(.34,5.69)],-.43,.016,'shade',root)
        line('Ronaldo smile',[(-.13,5.69),(.04,5.65),(.17,5.70)],-.44,.016,'beard',root)
    redraw(root,ronaldo)
    badge(root,ronaldo)
    capes=cape(root,offset)
    root.location.x=offset
    return root,capes


def city(offset,y=8):
    art.rect('Sky '+str(offset),offset-14,-3,28,16,'sky',y+5)
    for i in range(7):
        for j in range(3):
            art.oval('Cloud',offset-12+i*4+j*.6,7.5+(i%3)*.6,1.4,.32,'cloud',y+4-j*.01,outline=False)
    for i,(x,w,top) in enumerate(((-10,3,7.8),(-6.7,2.6,6),(-4,2.5,2.2),(-1.4,3,2.8),(1.7,2.8,2.5),(4.6,3.1,6.8),(8,3.5,7.8))):
        art.rect('Tower',offset+x,-3,w,top+3,'blueshade',y)
        poly('Tower side',[(offset+x+w,-3),(offset+x+w+.4,-3),(offset+x+w+.4,top+.2),(offset+x+w,top)],'navy',y-.01)
        for r in range(int((top+3)/.48)):
            for c in range(int(w/.38)):
                art.rect('Window',offset+x+.08+c*.38,-2.9+r*.48,.24,.31,'blue',y-.03)


def room(offset,door=False):
    if not door:
        art.rect('Warehouse wall',offset-18,-6,36,20,'wall',8)
    if door:
        city(offset,7)
        art.rect('Door left darkness',offset-16,-3,10.8,14,'ink',4)
        art.rect('Door right darkness',offset+5.2,-3,11,14,'ink',4)
        art.rect('Door lintel',offset-6,8.2,12,5,'ink',4)
        poly('Lit floor',[(offset-5.2,0),(offset+5.2,0),(offset+9,-4),(offset-10,-4)],'walllight',3)
        for x,z,s in ((-7,0,1.4),(-8.5,0,1.5),(-7,1.4,1.2),(7,0,1.3),(8.2,0,1.7)):
            art.rect('Crate',offset+x,z,s,s,'crate',-.2)
            line('Crate brace',[(offset+x,z),(offset+x+s,z+s)],-.25,.055,'crateshade')
        poly('Hero long shadow',[(offset-.6,.15),(offset+.65,.15),(offset+3,-3.8),(offset+.5,-3.8)],'ink',2)
    else:
        # Diagonal masonry gives the high-angle crouch its spatial cues.
        for i in range(-8,9):
            line('Floor joint',[(offset-12,i*1.1),(offset+12,i*1.1+4)],7.8,.012,'crack')
        for i in range(-8,9):
            line('Cross joint',[(offset+i*1.7,-4),(offset+i*1.7-4,12)],7.7,.014,'crack')
        for i in range(20):
            x=offset-10+(i*1.37)%20;z=-2+(i*2.3)%12
            line('Concrete scar',[(x,z),(x+.18,z+.17),(x+.09,z+.42),(x+.32,z+.57)],7.6,.012,'walllight')


def turtle(offset,point=False):
    root=art.empty('Mbappe turtle point' if point else 'Mbappe turtle crouch')
    def p(name,pts,c,y=0):return poly(name,pts,c,y,root)
    def l(name,pts,y=-.5,w=.016,c='ink'):return line(name,pts,y,w,c,root)
    art.oval('Turtle shell',0,2.65,1.19,1.35,'shellshade',.3,root)
    p('Turtle body',[(-.72,3.52),(.60,3.64),(1.01,2.92),(.7,1.53),(-.71,1.52),(-1.03,2.59)],'green',0)
    p('Turtle chest plate',[(-.49,3.45),(.46,3.50),(.67,2.89),(.39,1.77),(-.4,1.72),(-.7,2.88)],'shell',-.1)
    for z in (2.1,2.55,2.98):l('Shell division',[(-.55,z),(0,z-.08),(.53,z+.03)],-.13,.02,'shellshade')
    l('Shell middle',[(0,3.37),(0,1.88)],-.14,.02,'shellshade')
    p('Left crouched thigh',[(-.58,1.92),(-1.2,1.56),(-1.51,.61),(-1.03,.38),(-.57,1.06),(-.12,1.3)],'green',-.02)
    p('Right crouched thigh',[(.28,1.9),(1.23,1.53),(1.4,.8),(.96,.54),(.68,1.09),(.15,1.27)],'green',-.02)
    p('Left foot',[(-1.49,.65),(-1.07,.54),(-.96,.18),(-1.05,.04),(-1.75,.07),(-1.89,.22)],'green',-.08)
    p('Right foot',[(.99,.83),(1.40,.81),(1.60,.2),(1.38,.09),(.86,.13),(.78,.30)],'green',-.08)
    for x,z in ((-1.22,.88),(1.15,.94)):
        art.oval('Knee pad',x,z,.29,.25,'mask',-.12,root)
    p('Left braced arm',[(-.77,3.37),(-1.21,3.19),(-1.48,2.63),(-1.5,1.38),(-1.13,1.34),(-1.05,2.42),(-.6,2.88)],'green',-.18)
    p('Left fist',[(-1.5,1.54),(-1.10,1.53),(-1.06,1.11),(-1.19,.96),(-1.51,1.03),(-1.61,1.22)],'green',-.22)
    p('Bent right arm',[(.71,3.35),(1.03,3.17),(1.13,2.34),(.91,2.01),(.12,2.05),(-.13,2.29),(.05,2.50),(.72,2.4)],'green',-.25)
    p('Three finger hand',[(-.03,2.44),(-.27,2.50),(-.34,2.29),(-.22,2.14),(.12,2.11),(.22,2.30)],'greenlight',-.28)
    # Mbappe-inspired face: close-cropped hair, broad cheeks and a turtle mask.
    p('Mbappe neck',[(-.26,3.45),(.29,3.48),(.32,3.88),(-.25,3.87)],'brownskin',-.14)
    p('Mbappe face',[(-.46,4.52),(-.32,4.75),(.14,4.8),(.43,4.62),(.51,4.26),(.30,3.91),(.06,3.80),(-.25,3.91),(-.47,4.2)],'brownskin',-.20)
    p('Mbappe cropped hair',[(-.46,4.46),(-.49,4.66),(-.33,4.88),(.15,4.94),(.40,4.75),(.45,4.50),(.24,4.66),(-.17,4.64)],'hair',-.23)
    p('Turtle eye mask',[(-.46,4.5),(-.1,4.53),(.15,4.56),(.48,4.48),(.46,4.24),(.13,4.30),(-.06,4.25),(-.43,4.25)],'mask',-.25)
    for x in (-.24,.26):
        art.oval('Mbappe eye',x,4.38,.11,.054,'white',-.28,root,False)
        art.oval('Mbappe pupil',x+.025,4.38,.03,.046,'hair',-.30,root,False)
    p('Mask ties',[(.45,4.44),(.80,4.55),(1.04,4.28),(.74,4.35),(.90,4.09),(.54,4.24)],'mask',.01)
    l('Mbappe nose',[(.02,4.32),(-.025,4.16),(.12,4.14)],-.33,.015,'beard')
    l('Mbappe mouth',[(-.17,4.05),(.05,4.0),(.23,4.07)],-.34,.025,'beard')
    l('Mbappe lower lip',[(-.05,3.96),(.12,3.97)],-.35,.014,'brownlight')
    root.location.x=offset
    return root


def pointing_hand(offset):
    hand=sprite('Mbappe side-profile pointing','mbappe-profile.png',offset,10,6.667,rig=True)
    return hand,hand


def camera(name,offset,z,scale,start):
    bpy.ops.object.camera_add(location=(offset,-25,z))
    cam=bpy.context.object;cam.name=name+' camera'
    cam.rotation_euler=(Vector((offset,0,z))-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type='ORTHO';cam.data.ortho_scale=scale;cam.data.clip_end=100
    cam.data.passepartout_alpha=1
    marker=bpy.context.scene.timeline_markers.new(name,frame=start);marker.camera=cam
    return cam


def build(resolution):
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    art.MATS.clear()
    for key,value in {**art.COLORS,**PALETTE}.items():art.material(key,value)
    scene=bpy.context.scene
    scene.timeline_markers.clear()
    scene.render.engine=select_eevee_engine(i.identifier for i in scene.render.bl_rna.properties['engine'].enum_items)
    scene.eevee.taa_render_samples=8
    scene.render.resolution_x,scene.render.resolution_y=resolution
    scene.render.resolution_percentage=100
    scene.render.fps=FPS;scene.frame_start=1;scene.frame_end=FRAME_END
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8'
    scene.view_settings.view_transform='Standard';scene.view_settings.look='None'
    city(0);messi,mcape=hero(0)
    room(35);mbappe=sprite('Mbappe crouch','mbappe-crouch.png',35,4.1,6.15)
    room(70);pointbody,hand=pointing_hand(70)
    room(105,True);ronaldo,rcape=hero(105,True)
    cameras=[camera('messi',0,3.5,13.4,1),camera('mbappe',35,3.0,11.5,45),camera('point',70,3.4,12.4,88),camera('ronaldo',105,3.4,14.1,133)]
    # Ronaldo emerges from silhouette into color, as in the doorway reveal.
    reveal_materials={}
    for obj in ronaldo.children:
        if obj.type in ('MESH','CURVE'):
            for slot in obj.material_slots:
                old=slot.material
                if old.name not in reveal_materials:
                    new=old.copy();new.name='Ronaldo reveal '+old.name
                    reveal_materials[old.name]=new
                slot.material=reveal_materials[old.name]
    for frame in range(1,FRAME_END+1):
        pose=pose_at(frame)
        messi.location.z=pose['hover'];messi.keyframe_insert('location',frame=frame)
        mbappe.location.z=.035*math.sin(frame*.3);mbappe.keyframe_insert('location',frame=frame)
        extension=pose['point_extension']
        # Profile hand gesture is baked into the sprite mesh, keeping the face still.
        cameras[0].data.ortho_scale=13.4-.5*min(1,(frame-1)/43)
        cameras[0].data.keyframe_insert('ortho_scale',frame=frame)
        cameras[3].data.ortho_scale=14.1-.6*pose['reveal']
        cameras[3].data.keyframe_insert('ortho_scale',frame=frame)
        for mat in reveal_materials.values():
            emit=next(n for n in mat.node_tree.nodes if n.type=='EMISSION')
            emit.inputs['Strength'].default_value=.025+.975*pose['reveal']
            emit.inputs['Strength'].keyframe_insert('default_value',frame=frame)
    scene.camera=cameras[0];scene.sync_mode='FRAME_DROP';scene.render.filepath='//frames/frame_'
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                space=area.spaces.active;space.region_3d.view_perspective='CAMERA'
                space.overlay.show_overlays=False;space.show_gizmo=False;space.shading.type='MATERIAL'
    bpy.ops.object.select_all(action='DESELECT');scene.frame_set(1)
    return scene,messi,hand


def inspect(scene,messi,hand):
    samples=[]
    for frame in PREVIEWS:
        scene.frame_set(frame);bpy.context.view_layer.update()
        expected=pose_at(frame)['shot']+' camera'
        assert scene.camera.name==expected,(frame,scene.camera.name,expected)
        samples.append({'frame':frame,'camera':scene.camera.name,'messi_z':messi.location.z,'point_tip_z':hand.data.vertices[13*41+2].co.z,'profile_head':list(hand.data.vertices[20*41+27].co)})
    assert samples[0]['messi_z']!=samples[1]['messi_z']
    point_samples=[s for s in samples if s['camera']=='point camera']
    assert max(s['point_tip_z'] for s in point_samples)-min(s['point_tip_z'] for s in point_samples)>.5
    assert len({tuple(s['profile_head']) for s in point_samples})==1, 'Arm rig distorted the face'
    scene.frame_set(1)
    return {'validated':True,'frames':FRAME_END,'fps':FPS,'duration_seconds':FRAME_END/FPS,
            'resolution':[scene.render.resolution_x,scene.render.resolution_y],
            'shots':SHOTS,'motion_samples':samples,'format':'original layered 2.5D recreation',
            'character_mapping':{'Omni-Man':'Messi','Spider-Man':'Mbappe Ninja Turtle','Thor':'Ronaldo Superman'},
            'bundled_assets':['assets/mbappe-profile.png','assets/mbappe-crouch.png'],'render_complete':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--resolution',type=int,nargs=2,default=[1920,1080])
    modes=parser.add_mutually_exclusive_group();modes.add_argument('--preview',action='store_true');modes.add_argument('--render',action='store_true')
    parser.add_argument('--resume',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    if any(not 64<=n<=4096 for n in args.resolution):parser.error('resolution must be between 64 and 4096')
    if args.resume and not args.render:parser.error('--resume requires --render')
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    sources=[Path(__file__).with_name(n) for n in ('superhero_crossover.py','crossover_spec.py','messi_floating.py','floating_spec.py','hd_spec.py','crossover_faces.py','crossover_sprites.py')]
    sources.extend(sorted((Path(__file__).resolve().parent/'assets').glob('mbappe-*.png')))
    fingerprint=render_fingerprint(sources,{'resolution':args.resolution,'frames':FRAME_END})
    folder=out/('previews' if args.preview else 'frames');ledger=out/'render-state.json'
    todo=remaining_frames(folder,ledger,fingerprint,args.resolution,args.resume,end=FRAME_END) if args.render else list(PREVIEWS) if args.preview else []
    if args.preview and folder.exists() and any(folder.iterdir()):raise FileExistsError('Use a fresh preview output folder')
    scene,messi,hand=build(args.resolution);report=inspect(scene,messi,hand);report['fingerprint']=fingerprint
    reportpath=out/'motion-report.json';reportpath.write_text(json.dumps(report,indent=2),encoding='utf-8')
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'superhero-crossover.blend'))
    completed=sorted(set(range(1,FRAME_END+1))-set(todo)) if args.render else []
    if todo:folder.mkdir(exist_ok=True)
    for frame in todo:
        path=folder/f'frame_{frame:04}.png'
        if path.exists():raise FileExistsError(f'Refusing to overwrite {path}')
        scene.frame_set(frame);scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
        validate_png(path,args.resolution);completed.append(frame)
        if args.render:ledger.write_text(json.dumps({'fingerprint':fingerprint,'completed':sorted(completed)}),encoding='utf-8')
        print(f'Completed {frame}/{FRAME_END}',flush=True)
    report.update(render_complete=args.render and len(completed)==FRAME_END,rendered_frames=completed)
    reportpath.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report),flush=True)


if __name__=='__main__':main()
