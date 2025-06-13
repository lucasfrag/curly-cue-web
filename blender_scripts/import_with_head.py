import bpy
import os
from mathutils import Vector

# Caminhos absolutos
base_path = os.path.dirname(__file__)
hair_path = os.path.abspath(os.path.join(base_path, "../outputs/70.obj"))
head_path = os.path.abspath(os.path.join(base_path, "../data/head_models/headMesh.obj"))

# Limpa a cena
bpy.ops.wm.read_homefile(use_empty=True)

# Ativa o suporte a .obj
bpy.ops.preferences.addon_enable(module="io_scene_obj")

# === Importa a cabeça ===
before = set(bpy.data.objects)
bpy.ops.import_scene.obj(filepath=head_path)
after = set(bpy.data.objects)
head = (after - before).pop()
head.name = "HeadModel"
head.location = (0, 0, 0)
bpy.context.view_layer.objects.active = head
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Cria empty e detecta o objeto criado
before = set(bpy.data.objects)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
after = set(bpy.data.objects)
anchor = (after - before).pop()
anchor.name = "AnchorHeadTop"

# Move o empty para o topo da cabeça (Z máximo)
top_z = max((head.matrix_world @ v.co).z for v in head.data.vertices)
anchor.location = Vector((0, 0, top_z))

# === Importa o cabelo ===
before = set(bpy.data.objects)
bpy.ops.import_scene.obj(filepath=hair_path)
after = set(bpy.data.objects)
hair = (after - before).pop()
hair.name = "HairStrands"

# Centraliza o cabelo em X/Y, baseia Z na parte inferior dos fios
hair_bottom = min((hair.matrix_world @ v.co).z for v in hair.data.vertices)
sum_xy = Vector((0.0, 0.0))
for v in hair.data.vertices:
    world_co = hair.matrix_world @ v.co
    sum_xy += Vector((world_co.x, world_co.y))
hair_center_xy = sum_xy / len(hair.data.vertices)

hair.location = Vector((anchor.location.x - hair_center_xy.x,
                        anchor.location.y - hair_center_xy.y,
                        anchor.location.z - hair_bottom))

# Aplica transformações
bpy.context.view_layer.objects.active = hair
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

print("✅ Cabelo posicionado com sucesso.")
