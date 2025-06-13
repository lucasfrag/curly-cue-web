# ✨ Curly Cue Geometry

**CurlyCueGeometry** is a toolkit for generating and styling curly hair geometry from guide strands, inspired by the paper ["Curly-Cue: Curly Hair Geometry from a Single View"](https://doi.org/10.1145/3680528.3687641).

---

## 🚀 Features

- **Guide-to-Scalp Matching:** Match guide hairs to full scalp hairs with customizable parameters.
- **Spectral Analysis:** Generate spectra for displacement sequences sampled from styled hair sets.
- **Automatic Styling:** Create stylized hair wisps from guide strands and matching data.
- **Blender Integration:** Easily import hair and head models into Blender for visualization.
- **Interactive GUI:** Simple interface for strand generation and Blender visualization.

---

## 📁 Directory Structure

```text
.
├── blender_scripts/        # Automation scripts for Blender
├── data/                   # Input data: OBJ files, stats, CSVs
├── interface/              # GUI based on DearPyGui
├── outputs/                # Generated OBJ files
├── projects/               # Main scripts (matching, styling, export)
├── src/                    # Utilities and core algorithms
├── swatchExample.sh        # Example pipeline script
├── LICENSE
└── README.md
```

---

## 🛠️ Dependencies

- Python 3.8+
- [numpy](https://numpy.org/) (developed with version 1.23.5)
- [dearpygui](https://github.com/hoffstadt/DearPyGui)
- [Blender 3.6+](https://www.blender.org/) (for visualization)

---

## ⚡ Getting Started

1. **Run the Example Pipeline:**

    ```sh
    bash swatchExample.sh
    ```

    This will:
    - Generate guide-to-scalp matching dictionaries.
    - Generate spectra for displacement sequences.
    - Style a hair wisp using the above data.

2. **Interactive GUI:**

    Launch the GUI to generate strands and open results in Blender:

    ```sh
    cd interface/
    python interface.py
    ```

---

## 💡 Usage

- **Guide Matching:** See scripts in `projects/prox_matching` for matching parameters.
- **Styling:** Use `projects/clump_stylizer/wispify.py` to generate stylized strands.
- **Blender Import:** Use `blender_scripts/import_with_head.py` to import results into Blender.

---

## 📦 Data

- Input OBJ files and statistics are in `data`.
- Output OBJ files are saved in `outputs`.

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

> For more details on each processing step, see the scripts in `projects`.

