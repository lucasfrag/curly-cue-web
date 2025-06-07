import dearpygui.dearpygui as dpg
import subprocess
import os
from pathlib import Path

# Caminhos base
WISPIFY     = "../projects/clump_stylizer/wispify.py"
GUIDE_OBJ   = "../data/guide_strands/sideSwatchDroopSequence/70.obj"
SCALP_OBJ   = "../data/scalp_clouds/sideSwatchScalp.obj"
CSV_MATCH   = "../data/matching_csvs/sideSwatchGuides-sideSwatchScalp-groupingsr30.csv"
OUT_OBJ     = "../outputs/70.obj"
AMPS_NPZ    = "../data/amp_angle_stats/fullCombStats/fullComb.objAmps.npz"
ANGS_NPZ    = "../data/amp_angle_stats/fullCombStats/fullComb.objAngs.npz"

# Caminho para o Blender 3.6
BLENDER_EXE = Path("C:/Program Files/Blender Foundation/Blender 3.6/blender.exe")

def gerar_fios_callback():
    # Gera o .obj
    subprocess.run([
        "python", str(WISPIFY),
        str(GUIDE_OBJ),
        str(SCALP_OBJ),
        str(CSV_MATCH),
        str(OUT_OBJ),
        "--amps", str(AMPS_NPZ),
        "--angs", str(ANGS_NPZ)
    ])
    print("✅ Arquivo .obj gerado!")

    # Abre no Blender com importação automática
    subprocess.Popen([
        "C:/Program Files/Blender Foundation/Blender 3.6/blender.exe",
        "--python-expr",
        (
            "import bpy;"
            "bpy.ops.wm.read_homefile(use_empty=True);"
            "bpy.ops.preferences.addon_enable(module='io_scene_obj');"
            f"bpy.ops.import_scene.obj(filepath=r'{str(OUT_OBJ)}')"
        )
    ])


# Interface com DearPyGui
dpg.create_context()
with dpg.window(label="CurlyCueRT Interface", width=420, height=200):
    dpg.add_text("Simulação Interativa de Cabelos Crespos")
    dpg.add_button(label="Gerar Fios e Abrir no Blender", callback=gerar_fios_callback)

dpg.create_viewport(title='CurlyCueRT', width=440, height=220)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
