import os
import subprocess

def hex_to_rgb_normalized(hex_color):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255
    return r, g, b


def generate_strands(
    guide_path: str,
    scalp_path: str,
    grouping_csv: str,
    output_path: str,
    curliness: float = 0.5,
    length: float = 1.0,
    density: float = 1.0,
    color="#000000"
):
    
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
            guide_path,
            scalp_path,
            grouping_csv,
            output_path,
            "--curliness", str(curliness),
            "--length", str(length),
            "--density", str(density),
        ],
        cwd=os.path.dirname(wispify_script),
        check=True
    )

# Gerar o arquivo strands.mtl com a cor personalizada
    r, g, b = hex_to_rgb_normalized(color)
    mtl_path = output_path.replace(".obj", ".mtl")
    with open(mtl_path, "w") as mtl_file:
        mtl_file.write(f"""newmtl HairMaterial
        Kd {r:.3f} {g:.3f} {b:.3f}
        Ka 0.1 0.1 0.1
        Ks 0.0 0.0 0.0
        d 1.0
        illum 1
        """)

    # Adicionar referência ao .mtl dentro do .obj
    with open(output_path, "r") as obj_file:
        lines = obj_file.readlines()

    lines.insert(0, "mtllib strands.mtl\n")
    lines.insert(1, "usemtl HairMaterial\n")

    with open(output_path, "w") as obj_file:
        obj_file.writelines(lines)

    print(f"Arquivo .mtl criado em {mtl_path}")






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