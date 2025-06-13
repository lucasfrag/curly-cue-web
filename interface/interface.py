import dearpygui.dearpygui as dpg
import subprocess
import os
from pathlib import Path
import threading
import time

# Caminhos base
WISPIFY     = "../projects/clump_stylizer/wispify.py"
GUIDE_OBJ   = "../data/guide_strands/sideSwatchDroopSequence/70.obj"
SCALP_OBJ   = "../data/scalp_clouds/sideSwatchScalp.obj"
CSV_MATCH   = "../data/matching_csvs/sideSwatchGuides-sideSwatchScalp-groupingsr30.csv"
OUT_OBJ     = "../outputs/70.obj"
AMPS_NPZ    = "../data/amp_angle_stats/fullCombStats/fullComb.objAmps.npz"
ANGS_NPZ    = "../data/amp_angle_stats/fullCombStats/fullComb.objAngs.npz"
BLENDER_EXE = Path("C:/Program Files/Blender Foundation/Blender 3.6/blender.exe")

progress_bar_id = None
progress_overlay_id = None
progress_thread = None
progress_running = False

def log(texto):
    """Adiciona texto ao log da interface"""
    dpg.add_text(texto, parent=log_id)

def abrir_blender_callback():
    log("🚀 Abrindo Blender...")
    try:
        log("🧠 Abrindo Blender com modelo base e fios...")

        blender_script = Path(__file__).parent / "../blender_scripts/import_with_head.py"
        subprocess.Popen([
            str(BLENDER_EXE),
            "--python", str(blender_script.resolve())
        ])
        log("✅ Blender aberto com modelo base e fios.")
    except Exception as e:
        log(f"❌ Erro ao abrir Blender: {e}")

def atualizar_barra_progresso():
    global progress_running
    pct = 0.0
    while progress_running and pct < 0.99:
        pct += 0.01
        dpg.set_value(progress_bar_id, pct)
        dpg.configure_item(progress_bar_id, overlay=f"{int(pct*100)}%")
        time.sleep(0.1)
    if not progress_running:
        dpg.set_value(progress_bar_id, 0.0)
        dpg.configure_item(progress_bar_id, overlay="0%")

def gerar_fios_callback():
    global progress_thread, progress_running

    log("🔧 Gerando arquivo .obj...")
    dpg.set_value(progress_bar_id, 0.0)
    dpg.configure_item(progress_bar_id, overlay="0%")
    progress_running = True
    progress_thread = threading.Thread(target=atualizar_barra_progresso)
    progress_thread.start()

    result = subprocess.run([
        "python", str(WISPIFY),
        str(GUIDE_OBJ),
        str(SCALP_OBJ),
        str(CSV_MATCH),
        str(OUT_OBJ),
        "--amps", str(AMPS_NPZ),
        "--angs", str(ANGS_NPZ)
    ], capture_output=True, text=True)

    progress_running = False
    progress_thread.join()

    if result.returncode == 0:
        dpg.set_value(progress_bar_id, 1.0)
        dpg.configure_item(progress_bar_id, overlay="✅ Pronto para abrir no Blender!")
        log("✅ Arquivo .obj gerado com sucesso!")
    else:
        log("❌ Erro ao gerar o arquivo:")
        log(result.stderr)
        dpg.set_value(progress_bar_id, 0.0)
        dpg.configure_item(progress_bar_id, overlay="0%")

# Interface com DearPyGui
dpg.create_context()

with dpg.window(label="CurlyCueRT Interface", width=540, height=380):
    dpg.add_text("Simulação Interativa de Cabelos Crespos")
    dpg.add_button(label="Gerar Fios", callback=gerar_fios_callback)
    dpg.add_button(label="Abrir no Blender", callback=abrir_blender_callback)

    dpg.add_progress_bar(default_value=0.0, overlay="0%", width=-1)
    progress_bar_id = dpg.last_item()

    dpg.add_separator()
    dpg.add_text("📄 Log de Execução:")
    log_id = dpg.add_child_window(width=-1, height=180, autosize_x=True)

dpg.create_viewport(title='CurlyCueRT', width=560, height=420)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
