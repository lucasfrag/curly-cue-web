import os
import subprocess


def generate_strands(guide_path: str, scalp_path: str, grouping_csv: str, output_path: str):
    """
    Executa o wispify.py com os caminhos fornecidos, garantindo que:
    - o script seja executado na pasta correta
    - todos os caminhos passados sejam absolutos
    """
    wispify_script = os.path.join(
        os.path.dirname(__file__),
        "wispify.py"
    )

    guide_path = os.path.abspath(guide_path)
    scalp_path = os.path.abspath(scalp_path)
    grouping_csv = os.path.abspath(grouping_csv)
    output_path = os.path.abspath(output_path)
    wispify_script = os.path.abspath(wispify_script)

    subprocess.run(
        [
            "python",
            os.path.basename(wispify_script),
            os.path.abspath(guide_path),
            os.path.abspath(scalp_path),
            os.path.abspath(grouping_csv),
            os.path.abspath(output_path),
        ],
        cwd=os.path.dirname(wispify_script),
        check=True
    )

    # Aqui você pode incluir pós-processamento se necessário
    strands = read_obj_strands(output_path)
    return strands


def read_obj_strands(filename: str):
    import numpy as np

    strands = []
    with open(filename, "r") as f:
        current = []
        for line in f:
            if line.startswith("v "):
                parts = line.strip().split()
                x, y, z = map(float, parts[1:])
                current.append([x, y, z])
            elif line.startswith("o ") and current:
                strands.append(current)
                current = []
        if current:
            strands.append(current)

    return strands
