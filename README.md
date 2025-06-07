# CurlyCueGeometry
Curly-Cue's geometry step: making new strands from guide strands
(https://doi.org/10.1145/3680528.3687641)

## Dependencies:
numpy (developed on version 1.23.5)

## Quick Start:
`bash swatchExample.sh` will do three things in sequence:
1. Generate guide strand -> full scalp matching dictionaries at varying randomness distances.
2. Generate spectra for central displacement sequences sampled from a fully-combed set of strands.
3. Generate a styled swatch of hair (frame 70 from the .obj sequence in `data/`) from a set of guide strands using the above.

For more detail on each of these steps, refer to individual locations in `projects/` and their `argparse` parameters.
