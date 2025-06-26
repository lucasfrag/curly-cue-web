import os
import json
import math


def generate_mock_strands(output_json_path, curliness=0.5, length=1.0, density=1.0):
    num_strands = int(100 * density)
    points_per_strand = 20
    strands = []

    for s in range(num_strands):
        base_x = (s % 10) * 0.005
        base_y = (s // 10) * 0.005
        strand = []
        for i in range(points_per_strand):
            t = i / (points_per_strand - 1)
            z = -t * length
            angle = t * math.pi * 10 * curliness
            x = base_x + math.sin(angle) * 0.01 * curliness
            y = base_y + math.cos(angle) * 0.01 * curliness
            strand.append([x, y, z])
        strands.append(strand)

    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, "w") as f:
        json.dump(strands, f)

    return strands


def save_obj_and_mtl(strands, output_dir, color_hex="#000000"):
    obj_path = os.path.join(output_dir, "strands.obj")
    mtl_path = os.path.join(output_dir, "strands.mtl")
    mtl_name = "hairMaterial"

    r = int(color_hex[1:3], 16) / 255
    g = int(color_hex[3:5], 16) / 255
    b = int(color_hex[5:7], 16) / 255

    with open(mtl_path, "w") as mtl:
        mtl.write(f"newmtl {mtl_name}\n")
        mtl.write(f"Kd {r:.4f} {g:.4f} {b:.4f}\n")  # Difusa
        mtl.write(f"Ka 0.1 0.1 0.1\n")
        mtl.write(f"Ks 0.2 0.2 0.2\n")
        mtl.write(f"Ns 10.0\n")

    with open(obj_path, "w") as obj:
        obj.write(f"mtllib strands.mtl\n")
        obj.write(f"usemtl {mtl_name}\n")
        vertex_index = 1

        for strand in strands:
            for p in strand:
                obj.write(f"v {p[0]} {p[1]} {p[2]}\n")
            for i in range(1, len(strand)):
                a = vertex_index + i - 1
                b = vertex_index + i
                obj.write(f"l {a} {b}\n")
            vertex_index += len(strand)


def generate_strands(
    guide_path: str,
    scalp_path: str,
    grouping_csv: str,
    output_path: str,
    curliness: float = 0.5,
    length: float = 1.0,
    density: float = 1.0,
    color: str = "#000000"
):
    output_json_path = os.path.join("output", "strands.json")
    output_dir = os.path.dirname(output_path)

    print("🌀 Gerando fios com curvatura...")
    print(f" - Curliness: {curliness}")
    print(f" - Length: {length}")
    print(f" - Density: {density}")
    print(f" - Cor: {color}")
    print(f" - Arquivo JSON: {output_json_path}")

    strands = generate_mock_strands(
        output_json_path=output_json_path,
        curliness=curliness,
        length=length,
        density=density
    )

    print("💾 Salvando strands.obj e strands.mtl...")
    save_obj_and_mtl(strands, output_dir, color)
    print("✅ Tudo pronto!")
