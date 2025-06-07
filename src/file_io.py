#io processing for objs and strand arrays

import numpy as np
import csv

def vert_read(filename: str) -> np.ndarray:
    """ Reads only vertices from an .obj and stores in an np.array"""
    total_verts = 0
    with open(filename) as file:
        line = file.readline()
        while line:
            line = line.split()
            if line[0] == "v":
                total_verts += 1
            line = file.readline()
    verts = np.empty(shape=(total_verts,3))
    i = 0
    with open(filename) as file:
        line = file.readline()
        while line:
            line = line.split()
            if line[0] == "v":
                verts[i] = line[1:]
                i += 1
            line = file.readline()
    return verts

def edge_root_read(filename: str) -> list:
    """ Reads edge root (indexes into verts) from .obj"""
    edge_roots = []
    with open(filename) as file:
        line = file.readline()
        while line:
            line = line.split()
            if line[0] == "l":
                edge_roots.append([int(line[1]) - 1]) # obj's edges index into verts starting at 1 
                line = file.readline()
    return edge_roots

def read_obj_strands(filename: str) -> tuple[np.ndarray, list[list[int]]]:
    """ Reads verts and edges from .obj"""
    total_verts = 0
    with open(filename) as file:
        line = file.readline()
        while line:
            line = line.split()
            if line[0] == "v":
                total_verts += 1
            line = file.readline()
    verts = np.empty(shape=(total_verts,3))
    edges = []
    i = 0
    with open(filename) as file:
        line = file.readline()
        while line:
            line = line.split()
            if line[0] == "v":
                verts[i] = line[1:]
                i += 1
            if line[0] == "l":
                strand = []
                for j in range(1,len(line)):
                    strand.append(int(line[j]) - 1)
                edges.append(strand[:])
            line = file.readline()
    return verts, edges

def read_obj_strands_blended(filename: str) -> tuple[np.ndarray, list[list[int]]]:
    """ Reads verts and edges from .obj, then attempts to collate individual edges into long strand"""
    total_verts = 0
    with open(filename) as file:
        line = file.readline()
        while line:
            line = line.split()
            if line[0] == "v":
                total_verts += 1
            line = file.readline()
    verts = np.empty(shape=(total_verts,3))
    edges = []
    i = 0
    strand = []
    with open(filename) as file:
        line = file.readline()
        while line:
            line = line.split()
            if line[0] == "v":
                verts[i] = line[1:]
                i += 1
            if line[0] == "l":
                if strand == []:
                    strand = [int(line[1]) - 1, int(line[2]) - 1]
                elif strand[len(strand) - 1] != int(line[1]) - 1:
                    if strand != []:
                        edges.append(strand[:])
                    strand = [int(line[1]) - 1, int(line[2]) - 1]
                else:
                    strand.append(int(line[2]) - 1)
            line = file.readline()
    return verts, edges

def verts_to_displacements(p: np.ndarray) -> np.ndarray:
    """Gets an (n x 3) ndarray and returns an (n-1 x 3) ndarray of sequential displacement values"""
    d = np.empty(shape = (p.shape[0] - 1, p.shape[1]))
    for i in range(0, len(p) - 1):
        d[i] = p[i+1] - p[i]
    return d

def displacements_to_verts(d: np.ndarray, v0: np.ndarray) -> np.ndarray:
    """From an (n x 3) ndarray of sequential displacement values, returns an (n+1 x 3) ndarray of vertex positions"""
    vs = np.empty(shape = (d.shape[0] + 1, d.shape[1]))
    vs[0] = v0
    tol_d = np.zeros(3)
    for i in range(0, len(d)):
        tol_d += d[i]
        vs[i+1] = v0 + tol_d
    return vs

# ASSUMES v is 3D
def export_obj(verts: np.ndarray, strands: list, filename: str):
    """Outputs verts and strands into obj"""
    with open(filename, "w", newline="") as f:
        for v in verts:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        for s in strands:
            f.write("l")
            for n in s:
                f.write(f" {n+1}")
            f.write("\n")

def export_strand(verts: np.ndarray, filename: str):
    """Outputs contiguous strand of verts assuming they're all sequentially connected"""
    with open(filename, "w", newline = "") as f:
        for v in verts:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        f.write("l")
        for i in range(0, len(verts)):
            f.write(f" {i+1}")

def make_frames(verts: np.ndarray[np.ndarray], up: np.ndarray) -> np.ndarray[np.ndarray[np.ndarray]]:
    """From list of vertices and a starting vector, obtain list of frames with point-wise tangents"""
    frames = np.empty((len(verts),3,3))

    # tangents derived from catmull-rom spline interpolation
    if len(frames) == 1: # can't even do forward differencing
        w = verts[0]
        w = w/np.linalg.norm(w)
        u = np.cross(up, w)
        u = u/np.linalg.norm(u)
        v = np.cross(w, u)
        v = v/np.linalg.norm(v)
        frames[0][0] = u[:]
        frames[0][1] = v[:]
        frames[0][2] = w[:]
        return frames

    if len(frames) < 4: # there's no Catmull explanation for this. Just do forward tangent
        for i in range(0, len(frames)):
            w = np.empty(3)
            if i == len(frames) - 1:
                w = verts[i] - verts[i-1]
            else:
                w = verts[i+1] - verts[i]
            w = w/np.linalg.norm(w)
            u = np.cross(up, w)
            u = u/np.linalg.norm(u)
            v = np.cross(w, u)
            v = v/np.linalg.norm(v)
            frames[i][0] = u[:]
            frames[i][1] = v[:]
            frames[i][2] = w[:]
        return frames

    for i in range(0, len(frames)):
        # first get the tangent
        w = np.empty(3)
        if i == 0:
            w = verts[2] - verts[0] - 0.5*(verts[3] - verts[1])
        elif i == len(frames) - 1:
            w = verts[i] - verts[i-2] - 0.5*(verts[i-1] - verts[i-3])
        else:
            w = 0.5*(verts[i+1] - verts[i-1])
        w = w/np.linalg.norm(w)
        u = np.cross(up, w)
        u = u/np.linalg.norm(u)
        v = np.cross(w, u)
        v = v/np.linalg.norm(v)
        frames[i][0] = u[:]
        frames[i][1] = v[:]
        frames[i][2] = w[:]
    return frames

def clumping_read(filename: str)->list[list[int]]:
    """ Takes a clumping csv and returns a corresponding associative array c[] """
    # c[i] is a seq of indices j st scalp[j] is closest to root[i]
    with open(filename) as fp:
        reader = csv.reader(fp)
        guides_to_bases = [row for row in reader] 
    for i in range(len(guides_to_bases)):
        for j in range(len(guides_to_bases[i])):
            guides_to_bases[i][j] = int(guides_to_bases[i][j])
    return guides_to_bases

def grow_rate_map(t, high = 0.15, low = 0.07):
    """ Helper for interpolating weighting"""
    return low + (high - low)*t

def par_shift(verts: np.ndarray[np.ndarray], up:np.ndarray, x: float, y: float, grow_map) -> np.ndarray[np.ndarray]:
    """does a parallel-transported 2d shift using u, v of frame defined by up vector"""
    frames = make_frames(verts, up)
    ts = np.linspace(0, 1, len(verts))
    facs = grow_map(ts)
    new_verts = verts + x*np.transpose(facs*np.transpose(frames[:,0])) + y*np.transpose(facs*np.transpose(frames[:,1]))
    return new_verts
