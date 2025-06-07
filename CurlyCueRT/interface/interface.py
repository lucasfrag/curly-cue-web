
import dearpygui.dearpygui as dpg
import os

def gerar_fios_callback():
    os.system("python ../projects/clump_stylizer/wispify.py "
              "../data/guide_strands/sideSwatchDroopSequence/70.obj "
              "../data/scalp_clouds/sideSwatchScalp.obj "
              "../data/matching_csvs/sideSwatchGuides-sideSwatchScalp-groupingsr30.csv "
              "../outputs/70.obj "
              "--amps ../data/amp_angle_stats/fullCombStats/fullComb.objAmps.npz "
              "--angs ../data/amp_angle_stats/fullCombStats/fullComb.objAngs.npz")

dpg.create_context()

with dpg.window(label="CurlyCueRT Interface", width=400, height=200):
    dpg.add_text("Simulação Interativa de Cabelos Crespos")
    dpg.add_button(label="Gerar Fios", callback=gerar_fios_callback)

dpg.create_viewport(title='CurlyCueRT', width=420, height=220)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
