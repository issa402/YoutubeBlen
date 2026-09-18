"""Five-shot 2.5D adaptation of the September 16 motion reference.

Backgrounds and pointing are approximations, not pixel-exact replacements.
Run in Blender; no extra Python packages are required.
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
from crossover_sprites import sprite
from crossover_approved import approved_ronaldo
from hd_spec import select_eevee_engine

FPS = 30
END = 162
CUTS = (("arrival", 1, 20), ("hover", 21, 57), ("crouch", 58, 86),
        ("point", 87, 118), ("reveal", 119, END))
PREVIEWS = (1, 12, 20, 21, 57, 58, 86, 87, 100, 114, 119, 145, 162)


def key(obj, field, value, frame):
    setattr(obj, field, value)
    obj.keyframe_insert(field, frame=frame)


def plate(name, offset, asset=None, uv_rect=(0, 0, 1, 1)):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([(-8, 3, -4.5), (8, 3, -4.5), (8, 3, 4.5), (-8, 3, 4.5)], [], [(0, 1, 2, 3)])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location.x = offset
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    emit = nodes.new('ShaderNodeEmission')
    mat.node_tree.links.new(emit.outputs[0], out.inputs[0])
    if asset:
        texture = nodes.new('ShaderNodeTexImage')
        texture.image = bpy.data.images.load(str(HERE / 'assets' / asset), check_existing=True)
        texture.image.pack()
        mat.node_tree.links.new(texture.outputs['Color'], emit.inputs['Color'])
        uv = mesh.uv_layers.new()
        a, b, c, d = uv_rect
        for index, value in enumerate(((a,b),(c,b),(c,d),(a,d))):
            uv.data[index].uv = value
    else:
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 155
        noise.inputs['Detail'].default_value = 5
        ramp = nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].color = (.025,.045,.062,1)
        ramp.color_ramp.elements[1].color = (.14,.20,.24,1)
        mat.node_tree.links.new(noise.outputs['Fac'], ramp.inputs[0])
        mat.node_tree.links.new(ramp.outputs[0], emit.inputs[0])
    mesh.materials.append(mat)
    return obj


def masonry(offset):
    mat=bpy.data.materials.new('Concrete seams')
    mat.diffuse_color=(.022,.035,.045,1)
    for row in range(-3,4):
        for col in range(-4,5):
            x=col*3.4+row*.45;z=row*2.4
            paths=[[(x,z),(x+3.4,z+.35)],[(x,z),(x-.45,z+2.4)]]
            if (row+col)%2==0:
                paths.append([(x+.5,z+.1),(x+.8,z+.45),(x+.72,z+.6),(x+1,z+.9)])
            for points in paths:
                curve=bpy.data.curves.new('Masonry seam','CURVE')
                curve.dimensions='3D';curve.bevel_depth=.014
                spline=curve.splines.new('POLY');spline.points.add(len(points)-1)
                for pt,(px,pz) in zip(spline.points,points):
                    pt.co=(offset+px,2.7,pz,1)
                obj=bpy.data.objects.new('Warehouse joint',curve)
                bpy.context.collection.objects.link(obj);curve.materials.append(mat)

def camera(name, offset, start):
    bpy.ops.object.camera_add(location=(offset,-25,0))
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = Vector((0,1,0)).to_track_quat('-Z','Y').to_euler()
    obj.data.type = 'ORTHO'
    obj.data.ortho_scale = 16
    marker = bpy.context.scene.timeline_markers.new(name, frame=start)
    marker.camera = obj
    return obj


def build(size):
    print('PHASE: clear scene', flush=True)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.timeline_markers.clear()
    scene.render.engine = select_eevee_engine(i.identifier for i in scene.render.bl_rna.properties['engine'].enum_items)
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = 1, END
    scene.render.image_settings.file_format = 'PNG'
    scene.view_settings.view_transform = 'Standard'
    if hasattr(scene, 'eevee') and hasattr(scene.eevee, 'taa_render_samples'):
        scene.eevee.taa_render_samples = 8
    print('PHASE: backgrounds', flush=True)
    cams=[]
    for i,(name,start,end) in enumerate(CUTS):
        offset=i*40
        cams.append(camera(name,offset,start))
        if name=='reveal': plate(name+' background',offset,'reference-doorway.png')
        elif name=='hover': plate(name+' background',offset,'reference-doorway.png',(.25,.25,.73,.83))
        else:
            plate(name+' concrete',offset)
            masonry(offset)
    print('PHASE: character artwork', flush=True)
    small=sprite('Mbappe warehouse wide','mbappe-crouch-matched.png',1.0,2.0,3.0)
    small.location.z=-2.8
    arrival=sprite('Messi foreground arrival','messi-omni-matched.png',-4.0,10,15)
    hover=sprite('Messi city hover','messi-omni-matched.png',40,5.6,8.4,rig='cape')
    crouch=sprite('Mbappe close crouch','mbappe-crouch-matched.png',80,8.0,12.0)
    crouch.location.z=-8.0
    point=sprite('Mbappe pointing','mbappe-profile-matched.png',120,16,10.667,rig=True)
    point.location.z=-5.4
    ronaldo=approved_ronaldo(160)
    ronaldo.location.z=-3.0
    ronaldo.scale=(.86,.86,.86)
    print('PHASE: motion', flush=True)
    # Foreground boots descend into the first shot as in the reference.
    key(arrival,'location',(-4,-2,5),1)
    key(arrival,'location',(-4,-2,-1.5),16)
    key(arrival,'location',(-4,-2,-1.4),20)
    for f in range(21,58):
        key(hover,'location',(40,-1,-4.2+.09*math.sin((f-21)*.16)),f)
    for f in range(58,87):
        t=(f-58)/28
        key(crouch,'rotation_euler',(0,.025*math.sin(t*math.pi),0),f)
        key(crouch,'location',(80,-1,-8+.1*math.sin(t*math.pi)),f)
    # Preserve the approved sprite; push the camera toward its pointing hand.
    # This cannot synthesize the reverse view absent from the flat artwork.
    for f in range(87,119):
        t=max(0,min(1,(f-90)/17))
        smooth=t*t*(3-2*t)
        key(cams[3].data,'ortho_scale',16-3.1*smooth,f)
        key(cams[3],'location',(120-1.25*smooth,-25,.4*smooth),f)
    # A short luminous pulse follows the same late pointing beat.
    glow=plate('Pointing flash',120)
    glow.location.y=-10
    mat=glow.data.materials[0]
    nodes=mat.node_tree.nodes
    nodes.clear()
    out=nodes.new('ShaderNodeOutputMaterial')
    trans=nodes.new('ShaderNodeBsdfTransparent')
    emit=nodes.new('ShaderNodeEmission');emit.inputs['Color'].default_value=(1,.18,.14,1)
    mix=nodes.new('ShaderNodeMixShader')
    mat.node_tree.links.new(trans.outputs[0],mix.inputs[1])
    mat.node_tree.links.new(emit.outputs[0],mix.inputs[2])
    mat.node_tree.links.new(mix.outputs[0],out.inputs[0])
    for f,val in ((1,0),(104,0),(107,.55),(109,.03),(113,.4),(118,0),(162,0)):
        mix.inputs[0].default_value=val;mix.inputs[0].keyframe_insert('default_value',frame=f)
    for f in range(119,163):
        key(ronaldo,'location',(160,-1,-3+.035*math.sin((f-119)*.22)),f)
    scene.camera=cams[0]
    scene.frame_set(1)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_perspective='CAMERA'
                area.spaces.active.overlay.show_overlays=False
                area.spaces.active.show_gizmo=False
                area.spaces.active.shading.type='SOLID'
                area.spaces.active.shading.color_type='TEXTURE'
    return scene


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--resolution',type=int,nargs=2,default=(1920,1080))
    group=parser.add_mutually_exclusive_group()
    group.add_argument('--preview',action='store_true')
    group.add_argument('--render',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    if any(v<64 or v>4096 for v in args.resolution):parser.error('resolution outside 64..4096')
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    frames=list(range(1,END+1)) if args.render else list(PREVIEWS) if args.preview else []
    folder=out/('frames' if args.render else 'previews')
    if frames and folder.exists() and any(folder.iterdir()):raise FileExistsError('Use a fresh output folder')
    scene=build(args.resolution)
    for name,start,end in CUTS:
        scene.frame_set(start)
        assert scene.camera.name==name
    scene.frame_set(1)
    print('PHASE: save blend',flush=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'reference-crossover.blend'))
    if frames:folder.mkdir(exist_ok=True)
    for f in frames:
        scene.frame_set(f);scene.render.filepath=str(folder/f'frame_{f:04}.png')
        bpy.ops.render.render(write_still=True)
        print(f'Frame {f}/{END}',flush=True)
    report={'frames':END,'fps':FPS,'seconds':END/FPS,'cuts':CUTS,'rendered':frames,
            'limitations':['Reconstructed backgrounds, not original pixels','Profile sprite push-in approximates foreshortened pointing','No source audio'],
            'reference_seconds':5.3876333333333335}
    (out/'motion-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')


if __name__=='__main__':main()
