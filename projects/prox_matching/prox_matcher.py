# The main python file that takes in full-res scalp points and guide points to create voronoi region assignments into a csv

import sys
import numpy as np
import time as ti
import random
import math
import csv
import os
import argparse
import datetime

script_dir = os.path.dirname(__file__)
mymodules_dir = os.path.join(script_dir, '..','..','src')
sys.path.append(mymodules_dir)

import file_io as io
import octrees_lite as oct

def prob_func(r, r0, pf):
    if r <= r0:
        return 0
    return pf/(1-r0)*(r-r0)

# returns a point according to distance array
def zone_selector(ps: np.ndarray[np.ndarray], ds: np.ndarray[float], ratio:float, selection_method = 0)-> np.ndarray:
    p_select = ps[0]
    if len(ds) == 1:
        return p_select
    if ds[0]/ds[1] < ratio:
        return p_select
    inv_ds = 1/ds
    probs = inv_ds/np.sum(inv_ds)
    if selection_method == 0: # inverse probability function
        ind = np.random.choice(np.arange(len(probs)), p = probs)
    elif selection_method == 1: # uniform choice
        ind = np.random.choice(np.arange(len(probs)))
    else:
        ind = -1
    return ps[ind]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("scalpRootsObj", type = str, help = "The full-resolution scalp points")
    parser.add_argument("scalpGuidesObj", type = str, help = "The guide points")
    parser.add_argument("--fout", type = str, help = "The file to output the clumping", default = "./")
    parser.add_argument("--pullR", type = int, help = "The number of nth-ranked distances to find and randomly assign", default = 30)
    parser.add_argument("--nameSuffix", type = str, help = "Adding an identifying string for wedging", default = "")
    parser.add_argument("--recursionLimit", type = int, help = "Recursion limit for the octree stuff", default = 32000)
    parser.add_argument("--smallestNode", type = int, help = "Smallest node for the octree stuff", default = 2)

    args = parser.parse_args()

    print(sys.argv, flush=True)
    sys.setrecursionlimit(args.recursionLimit)

    # reading in the point clouds
    full_roots = io.vert_read(args.scalpRootsObj)
    guide_roots = io.vert_read(args.scalpGuidesObj)
    # v_scalp, f_scalp = igl.read_triangle_mesh(args[2])
    guide_roots_dict = {}
    for i, p in enumerate(guide_roots):
        p_key = str(p)
        guide_roots_dict.update({p_key : int(i)})

    print(f"len(full_roots): {len(full_roots)}")
    print(f"len(guide_roots): {len(guide_roots)}")
    print(f"guide roots dict: {len(guide_roots_dict)}")
    print("making octree...")
    u = np.max(guide_roots, axis = 0)
    d = np.min(guide_roots, axis = 0)
    tree_start = ti.time()
    oct_root = oct.make_octree(guide_roots, args.smallestNode, u, d)
    print(f"octree done in {ti.time() - tree_start} seconds!")
    diam = oct.average_leaf_diam(oct_root)
    print(f"octree average leaf diameter: {diam}")

    # # make an array that matches each index of the full root to its corresponding index into guide_roots
    # and also an array that matches each guide index to a list of all the root indices
    closest_guide = np.zeros(len(full_roots))
    guide_to_roots = [[] for _ in range(len(guide_roots))]
    print("timing closest_guide and guide_to_roots creation")
    creation_start = ti.time()
    percent = 0
    for i, v in enumerate(full_roots):
        cur_percent = int((i/len(full_roots))*100)
        if cur_percent >= percent:
            print(f'{datetime.datetime.now()}: reached {percent}%', flush=True)
            percent += 10
        ps, ds = oct.closest_guide_inds(v, oct_root, diam/2.0, 2*args.pullR)
        # print(ds)
        # some fuzzing depending on distance to center
        selected_p = zone_selector(ps[:args.pullR], ds[:args.pullR], -1.0, selection_method=1)
        closest_guide[i] = int(guide_roots_dict[str(selected_p)])
        guide_to_roots[int(closest_guide[i])].append(i)

    print(f"array creation took {ti.time() - creation_start} seconds.")

    # file_name = args[0].split(".")[0]+"-"+args[1].split(".")[0]+"-prox_dict.txt"
    file_name2 = os.path.split(args.scalpGuidesObj)[1].split(".")[0]+"-"+os.path.split(args.scalpRootsObj)[1].split(".")[0]+"-groupings" + args.nameSuffix + ".csv"
    file_name2 = os.path.join(args.fout, file_name2)
    if not os.path.exists(args.fout):
        os.makedirs(args.fout)
    # print(f"saving to {file_name}")
    # np.savetxt(file_name, closest_guide)
    print(f"saving to {file_name2}") 
    with open(file_name2, "w", newline="") as f:
        wr = csv.writer(f, delimiter=",")
        wr.writerows(guide_to_roots)

    exit(0)