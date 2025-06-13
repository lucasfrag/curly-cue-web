import bpy
import os
from mathutils import Vector

# === CONFIGURAÇÕES ===
BASE_DIR = os.path.dirname(__file__)
HEAD_PATH = os.path.abspath(os.path.join(BASE_DIR, "../data/head_models/headMesh.obj"))
HAIR_PATH = os.path.abspath(os.path.join(BASE_DIR, "../outputs/70.obj"))

# === LIMPA A CENA ===
bpy.ops.wm.read_homefile(use_empty=True)

# === ATIVA SUPORTE A OBJ ===
bpy.ops.preferences.addon_enable(module="io_scene_obj")

# === IMPORTA CABEÇA ===
before = set(bpy.data.objects)
bpy.ops.import_scene.obj(filepath=HEAD_PATH)
after = set(bpy.data.objects)
head = (after - before).pop()
head.name = "HeadModel"
head.location = (0, 0, 0)
bpy.context.view_layer.objects.active = head
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# === IMPORTA CABELO ===
before = set(bpy.data.objects)
bpy.ops.import_scene.obj(filepath=HAIR_PATH)
after = set(bpy.data.objects)
hair = (after - before).pop()
hair.name = "HairStrands"

# === RECENTRALIZA O CABELO EM TORNO DO PRÓPRIO CENTRO ===
# Calcula centro médio dos vértices
verts = [hair.matrix_world @ v.co for v in hair.data.vertices]
center = sum(verts, Vector((0, 0, 0))) / len(verts)
# Move para a origem e aplica
hair.location -= center
bpy.context.view_layer.objects.active = hair
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# === POSICIONA CABELO SOBRE A CABEÇA ===
# Pega o ponto mais alto da cabeça (Z)
top_z = max((head.matrix_world @ v.co).z for v in head.data.vertices)
# Pega o ponto mais baixo do cabelo (Z)
bottom_z = min((hair.matrix_world @ v.co).z for v in hair.data.vertices)
# Calcula deslocamento vertical
offset_z = top_z - bottom_z
hair.location.z += offset_z

# Aplica posição final
bpy.context.view_layer.objects.active = hair
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

print("✅ Cabelo centralizado e posicionado corretamente sobre a cabeça.")
