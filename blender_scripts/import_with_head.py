import bpy
import os

# Caminhos absolutos dos arquivos
base_path = os.path.dirname(__file__)
hair_path = os.path.abspath(os.path.join(base_path, "../outputs/70.obj"))
head_path = os.path.abspath(os.path.join(base_path, "../data/head_models/headMesh.obj"))

# Limpa a cena
bpy.ops.wm.read_homefile(use_empty=True)

# Ativa o addon .obj
bpy.ops.preferences.addon_enable(module="io_scene_obj")

# === Importa cabeça ===
before_import = set(bpy.data.objects)
bpy.ops.import_scene.obj(filepath=head_path)
after_import = set(bpy.data.objects)
head_obj = (after_import - before_import).pop()
head_obj.name = "HeadModel"
head_obj.location = (0, 0, 0)
bpy.context.view_layer.objects.active = head_obj
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# === Importa fios ===
before_import = set(bpy.data.objects)
bpy.ops.import_scene.obj(filepath=hair_path)
after_import = set(bpy.data.objects)
hair_obj = (after_import - before_import).pop()
hair_obj.name = "HairStrands"

# Alinha fios sobre a cabeça
head_top_z = max((head_obj.matrix_world @ v.co).z for v in head_obj.data.vertices)
hair_bottom_z = min((hair_obj.matrix_world @ v.co).z for v in hair_obj.data.vertices)
offset = head_top_z - hair_bottom_z
hair_obj.location.z += offset

# Aplica transformação
bpy.context.view_layer.objects.active = hair_obj
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

print("✅ Fios posicionados corretamente sobre a cabeça.")
