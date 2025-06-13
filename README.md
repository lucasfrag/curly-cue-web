# Curly Cue Geometry

CurlyCueGeometry is a toolset for generating and styling curly hair strand geometry from guide strands, inspired by the paper ["Curly-Cue: Curly Hair Geometry from a Single View"](https://doi.org/10.1145/3680528.3687641).

## Features

- **Guide-to-Full Strand Matching:** Match guide strands to full scalp strands using customizable parameters.
- **Spectral Analysis:** Generate spectra for displacement sequences sampled from combed hair sets.
- **Automated Hair Styling:** Create styled hair swatches from guide strands and matching data.
- **Blender Integration:** Easily import generated hair and head models into Blender for visualization.
- **Interactive GUI:** Simple interface for generating strands and launching Blender.

## Directory Structure

```
.
├── blender_scripts/        # Blender automation scripts
├── data/                   # Input data: OBJ files, stats, CSVs
├── interface/              # DearPyGui-based GUI
├── outputs/                # Generated OBJ files
├── projects/               # Main processing scripts (matching, styling, exporting)
├── src/                    # Core utilities and algorithms
├── swatchExample.sh        # Example pipeline script
├── LICENSE
└── README.md
```

## Dependencies

- Python 3.8+
- [numpy](https://numpy.org/) (developed on version 1.23.5)
- [dearpygui](https://github.com/hoffstadt/DearPyGui)
- [Blender 3.6+](https://www.blender.org/) (for visualization)

## Quick Start

1. **Run the Example Pipeline:**

   ```sh
   bash swatchExample.sh
   ```

   This will:
   - Generate guide-to-scalp matching dictionaries.
   - Generate spectra for displacement sequences.
   - Style a hair swatch using the above data.

2. **Interactive GUI:**

   Launch the GUI to generate strands and open results in Blender:

   ```sh
   cd interface/
   python interface.py
   ```

## Usage

- **Guide Matching:** See scripts in `projects/prox_matching` for matching parameters.
- **Styling:** Use `projects/clump_stylizer/wispify.py` to generate styled strands.
- **Blender Import:** Use `blender_scripts/import_with_head.py` to import results into Blender.

## Data

- Input OBJ files and statistics are in `data`.
- Output OBJ files are written to `outputs`.

## License

This project is licensed under the MIT License. See `LICENSE` for details.

---

For more details on each processing step, refer to the scripts in `projects`.
