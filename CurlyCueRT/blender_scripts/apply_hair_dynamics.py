
import bpy
import os

# Caminho para o .obj (ajuste conforme necessário)
obj_path = bpy.path.abspath("//../outputs/70.obj")

# Importa o objeto .obj
bpy.ops.import_scene.obj(filepath=obj_path)

# Seleciona o objeto recém-importado
obj = bpy.context.selected_objects[0]
bpy.context.view_layer.objects.active = obj

# Adiciona sistema de partículas de cabelo
bpy.ops.object.particle_system_add()
psys = obj.particle_systems[0]
psys.settings.type = 'HAIR'
psys.settings.use_hair_dynamics = True
psys.settings.count = 500
psys.settings.hair_length = 1.0
psys.settings.use_rotations = True

print("✔️ Sistema de cabelo com física aplicado!")
