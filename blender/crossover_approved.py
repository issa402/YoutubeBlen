"""Exact supplied Ronaldo pixels mapped to a manually outlined Blender cutout."""
import bpy
from pathlib import Path
from mathutils import Vector

# Boundary follows the supplied 1512x1040 image. Pixels are never resampled here.
OUTLINE=((687,94),(696,83),(688,80),(704,72),(696,70),(717,65),(713,61),(736,63),(744,59),(762,65),(774,63),(790,78),(801,95),(806,121),(800,148),(811,146),(817,154),(812,173),(800,181),(797,208),(801,253),(847,270),(893,279),(896,291),(913,327),(908,352),(919,397),(922,440),(939,475),(937,575),(938,631),(925,641),(937,950),(870,974),(866,938),(849,932),(851,953),(902,1014),(906,1038),(777,1037),(772,996),(780,969),(778,938),(774,918),(715,944),(705,944),(688,973),(683,1015),(683,1035),(587,1038),(583,1012),(625,971),(625,943),(517,972),(542,835),(553,728),(566,643),(550,636),(552,595),(557,575),(548,509),(550,476),(566,443),(569,395),(577,358),(571,326),(587,303),(603,282),(635,277),(691,256),(695,231),(696,209),(689,186),(678,176),(677,160),(682,148),(688,150),(688,126))


# Precomputed from the approved outline in Blender 4.5 to avoid runtime tessellation.
# Compatibility precaution only; the Mac SIGTRAP cause remains unconfirmed.
FACES=((37,38,39),(48,49,50),(37,39,40),(47,48,50),(46,47,50),(36,37,40),(46,50,51),(36,40,41),(32,33,34),(45,46,51),(52,53,54),(45,51,52),(36,41,42),(35,36,42),(31,32,34),(43,44,45),(43,45,52),(43,52,54),(31,34,35),(35,42,43),(31,35,43),(31,43,54),(31,54,55),(31,55,56),(31,56,57),(30,31,57),(30,57,58),(29,30,58),(29,58,59),(28,29,59),(28,59,60),(28,60,61),(28,61,62),(27,28,62),(27,62,63),(26,27,63),(25,26,63),(25,63,64),(25,64,65),(24,25,65),(23,24,65),(23,65,66),(23,66,67),(22,23,67),(22,67,68),(21,22,68),(21,68,69),(20,21,69),(20,69,70),(19,20,70),(19,70,71),(19,71,72),(18,19,72),(18,72,73),(17,18,73),(17,73,74),(16,17,74),(16,74,76),(76,74,75),(15,16,14),(14,16,76),(14,76,77),(13,14,77),(13,77,0),(12,13,0),(11,12,0),(11,0,1),(11,1,2),(11,2,3),(10,11,9),(9,11,3),(9,3,4),(9,4,5),(8,9,7),(7,9,5),(7,5,6))

def approved_ronaldo(offset):
    image=bpy.data.images.load(str(Path(__file__).resolve().parent/'assets/ronaldo-approved.png'),check_existing=True)
    if tuple(image.size)!=(1512,1040):raise ValueError('Approved Ronaldo reference dimensions changed')
    image.pack()
    height=7.25;width=height*1512/1040
    points=[Vector(((x/1512-.5)*width,-1,(1-y/1040)*height)) for x,y in OUTLINE]
    mesh=bpy.data.meshes.new('Approved Ronaldo silhouette')
    mesh.from_pydata(points,[],FACES);mesh.update()
    uv=mesh.uv_layers.new(name='Approved image UV')
    for polygon in mesh.polygons:
        for i in polygon.loop_indices:
            x,y=OUTLINE[mesh.loops[i].vertex_index];uv.data[i].uv=(x/1512,1-y/1040)
    mat=bpy.data.materials.new('Approved Ronaldo original artwork');mat.use_nodes=True
    nodes=mat.node_tree.nodes;nodes.clear()
    tex=nodes.new('ShaderNodeTexImage');tex.image=image
    emit=nodes.new('ShaderNodeEmission');out=nodes.new('ShaderNodeOutputMaterial')
    mat.node_tree.links.new(tex.outputs['Color'],emit.inputs['Color']);mat.node_tree.links.new(emit.outputs[0],out.inputs[0])
    mesh.materials.append(mat)
    obj=bpy.data.objects.new('Ronaldo supplied design',mesh);bpy.context.collection.objects.link(obj);obj.location.x=offset
    return obj
