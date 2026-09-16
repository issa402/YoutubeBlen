"""Alpha-composited character artwork and a bounded side-profile arm lift."""
import math
from pathlib import Path
import bpy
from crossover_spec import pose_at,FRAME_END


def sprite(name,asset,offset,width,height,rig=False):
    image=bpy.data.images.load(str(Path(__file__).resolve().parent/'assets'/asset),check_existing=True)
    image.pack()
    mat=bpy.data.materials.new(name+' cel image');mat.use_nodes=True
    nodes=mat.node_tree.nodes;nodes.clear()
    tex=nodes.new('ShaderNodeTexImage');tex.image=image;tex.interpolation='Linear'
    emit=nodes.new('ShaderNodeEmission');transparent=nodes.new('ShaderNodeBsdfTransparent')
    mix=nodes.new('ShaderNodeMixShader');out=nodes.new('ShaderNodeOutputMaterial')
    cut=nodes.new('ShaderNodeMath');cut.operation='GREATER_THAN';cut.inputs[1].default_value=.78
    links=mat.node_tree.links;links.new(tex.outputs['Color'],emit.inputs['Color'])
    links.new(tex.outputs['Alpha'],cut.inputs[0]);links.new(cut.outputs[0],mix.inputs[0])
    links.new(transparent.outputs[0],mix.inputs[1]);links.new(emit.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],out.inputs[0])
    nx,nz=(40,24) if rig else (1,1)
    vertices=[((i/nx-.5)*width,-1,j/nz*height) for j in range(nz+1) for i in range(nx+1)]
    faces=[(j*(nx+1)+i,j*(nx+1)+i+1,(j+1)*(nx+1)+i+1,(j+1)*(nx+1)+i) for j in range(nz) for i in range(nx)]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
    uv=mesh.uv_layers.new(name='UVMap')
    for polygon in mesh.polygons:
        for index in polygon.loop_indices:
            vi=mesh.loops[index].vertex_index
            uv.data[index].uv=((vi%(nx+1))/nx,(vi//(nx+1))/nz)
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.location.x=offset
    mesh.materials.append(mat)
    if rig:
        for frame in (1,88,96,104,112,132,FRAME_END):
            angle=.20*(1-pose_at(frame)['point_extension'])
            for index,(x,y,z) in enumerate(vertices):
                u=(x/width)+.5;v=z/height
                # Arm is on the left side at chest level; face and shell remain fixed.
                weight=max(0,min(1,(.61-u)/.15))*max(0,min(1,(v-.28)/.08))*max(0,min(1,(.73-v)/.08))
                dx,dz=x-.10*width,z-.55*height
                rotated_x=math.cos(angle)*dx-math.sin(angle)*dz+.10*width
                rotated_z=math.sin(angle)*dx+math.cos(angle)*dz+.55*height
                mesh.vertices[index].co=(x+(rotated_x-x)*weight,y,z+(rotated_z-z)*weight)
                mesh.vertices[index].keyframe_insert('co',frame=frame)
    return obj
