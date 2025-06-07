# takes in a full-resolution simulation as input and outputs the amplitude and angle spectra for
# later stylization usage

import numpy as np
import sys
import os
import argparse

script_dir = os.path.dirname(__file__)
mymodules_dir = os.path.join(script_dir, '..','..','src')
sys.path.append(mymodules_dir)

import file_io as io
import dft_testing as dft

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Generating spectra for later usage in stylization")
    parser.add_argument("fullRezObj", help = "The full resolution strand set that takes all of the amplitude/angle info", type = str)
    parser.add_argument("outputDir", help = "Directory to put the output angles and amplitudes .npz files")

    args = parser.parse_args()
    print(sys.argv, flush = True)

    verts, edges = io.read_obj_strands(args.fullRezObj)
    amps, angs = dft.fft_amp_angle_collect(verts, edges)

    if not os.path.exists(args.outputDir):
        os.makedirs(args.outputDir)

    fullRezTail = os.path.split(args.fullRezObj)[1]
    np.savez(os.path.join(args.outputDir, f'{fullRezTail}Amps'), *amps)
    np.savez(os.path.join(args.outputDir, f'{fullRezTail}Angs'), *angs)