# The main file that turns guide strand geometry into finalized clump geometry

import numpy as np
import random
import math
import sys
import os
import datetime
import argparse

script_dir = os.path.dirname(__file__)
mymodules_dir = os.path.join(script_dir, '..','..','src')
sys.path.append(mymodules_dir)

import file_io as io
import dft_testing as dft

def distance_accumulate(pts):
    ds = np.empty(len(pts))
    ds[0] = 0
    for i in range(1,len(ds)):
        ds[i] = ds[i-1] + np.linalg.norm(pts[i] - pts[i-1])
    return ds

def bez(v0, m0, v1, m1, ts):
    t3 = ts**3
    t2 = ts**2
    vs = np.empty((len(ts), 3))
    for i in range(3):
        vs[:,i] = v0[i] * (2 * t3 - 3 * t2 + 1) + m0[i] * (t3 - 2 * t2 + ts) + v1[i] * (3 * t2 - 2 * t3) + m1[i] * (t3 - t2)
    return vs

def even_bez(v0, m0, v1, m1, res):
    ts = np.linspace(0,1,res)
    pts = bez(v0, m0, v1, m1, ts)
    distances = distance_accumulate(pts)
    even_distances = np.linspace(0, distances[-1], res)
    even_times = np.interp(even_distances, distances, ts)
    return bez(v0, m0 ,v1, m1, even_times)

def curve_interp(curve_0: np.ndarray[np.ndarray], curve_1: np.ndarray[np.ndarray]) -> np.ndarray[np.ndarray]:
    assert curve_0.shape == curve_1.shape, f"curve's shapes don't match: c0: {curve_0.shape} | c1: {curve_1.shape}"
    ts = np.linspace(0,1,len(curve_0))
    return np.transpose(ts*np.transpose(curve_1) + (1-ts)*np.transpose(curve_0))

def catmull(vs, ts):
    cats = np.empty((len(ts), 3))
    if len(vs) == 1:
        for i in range(0,len(cats)):
            cats[i] = vs[0][:]
        return cats
    if len(cats) == 2:
        for i, t in enumerate(ts):
            cats[i] = (1-t)*vs[0] + t*vs[1]
        return cats
    if len(cats) == 3:
        for i, t in enumerate(ts):
            scaled = 2*t
            low = int(math.floor(scaled))
            high = int(math.ceil(scaled))
            if low == high:
                cats[i] = vs[low]
                continue
            if low == 0:
                m0 = vs[2] - vs[0] - 0.5*(vs[2] - vs[1])
            else:
                m0 = 0.5*(vs[2] - vs[0])
            if high == 2:
                m1 = vs[high] - vs[high - 2] - 0.5*(vs[high - 1] - vs[high - 2])
            else: 
                m1 = 0.5*(vs[2] - vs[0])
            real_t = scaled - low
            t3 = real_t**3
            t2 = real_t**2
            cats[i] = vs[low] * (2 * t3 - 3 * t2 + 1) + m0 * (t3 - 2 * t2 + real_t) + vs[high] * (3 * t2 - 2 * t3) + m1 * (t3 - t2)
        return cats

    for i, t in enumerate(ts):
        scaled = t*(len(vs)-1)
        low = int(math.floor(scaled))
        high = int(math.ceil(scaled))
        if low == high:
            cats[i] = vs[low]
            continue
        if low == 0:
            m0 = vs[2] - vs[0] - 0.5 * (vs[3] - vs[1])
        else:
            m0 = 0.5*(vs[low + 1] - vs[low - 1])
        if high == len(vs) - 1:
            m1 = vs[high] - vs[high - 2] - 0.5*(vs[high-1] - vs[high-3])
        else:
            m1 = 0.5*(vs[high + 1] - vs[high - 1])
        real_t = scaled - low
        t3 = real_t**3
        t2 = real_t**2
        cats[i] = vs[low] * (2 * t3 - 3 * t2 + 1) + m0 * (t3 - 2 * t2 + real_t) + vs[high] * (3 * t2 - 2 * t3) + m1 * (t3 - t2)
    return cats

# resamples catmull spline with t_max in (0, 1] cutoff
def even_catmull(vs, res, t_max):
    ts = np.linspace(0, t_max, res)
    pts = catmull(vs, ts)
    distances = distance_accumulate(pts)
    even_distances = np.linspace(0, distances[-1], res)
    even_times = np.interp(even_distances, distances, ts)
    return catmull(vs, even_times)

# takes array elements and drops them out with some probability
def dropout(vs, prob):
    accum = []
    for v in vs:
        if random.random() > prob:
            accum.append(v[:])
    accum_np = np.array(accum)
    if len(accum_np) == 0:
        return accum_np #returning an empty array
    if accum_np.ndim == 1:
        return np.array([accum_np])
    return accum_np

def rerooted_curl(v0, m0, dropout_p, t_s, c_d, qs, up):
    cutoff = min(max(int(t_s*len(qs)),3),len(c_d)-1) #the INDEX to which all the displacements get applied
    center_curve = dft.get_centercurve(qs)

    if len(qs) < 6:
        return qs + (v0 - qs[2])

    if cutoff == len(center_curve) - 1:
        m_cut = center_curve[-1] - center_curve[-2]
    else:
        m_cut = 0.5*(center_curve[cutoff+1] - center_curve[cutoff-1]) 
    v_cut = center_curve[cutoff]
    m0 = (center_curve[cutoff//2] - v0) # REALLY short wisps leads to sampling into rooted portion (during sim)
    if np.dot(m0, center_curve[-1] - v0) < 0.0: # so do an alignment check
        # print("performing flip!")
        m0 = qs[-1] - v0 # and fall back to just a lazy solution 
    prox_len = np.linalg.norm(v_cut-v0)
    m0 = m0/np.linalg.norm(m0)*prox_len
    m_cut = m_cut/np.linalg.norm(m_cut)*prox_len
    spine = even_bez(v0, m0, v_cut, m_cut, cutoff + 1) #cutoff + 1 here since it's length of array that is from 0->cutoff
    # spine = curve_interp(center_curve[:cutoff + 1] + (v0 - center_curve[0]), center_curve[:cutoff + 1])
    # spine = curve_interp(spine, center_curve[:cutoff+1])
    wrapped = dft.wind_displacements(spine, c_d, up)
    # wrapped = spine
    # wrapped = center_curve
    # wrapped = center_curve[:cutoff+1]
    # options for manual "locking" of initial positions in wrapped[]?
    wrapped[0] = v0[:]
    # print(f"len(wrapped): {len(wrapped)}")

    post = dropout(qs[cutoff+1:],dropout_p)
    if len(post) == 0:
        return wrapped
    return np.append(wrapped, post, axis = 0)

# each np.ndarray has mismatched shape[0] but is otherwise same
# want to consolidate into (sum of all shape[0]s, <remaining dimensions>) np.ndarray
def numpy_flat(weirdo: list[np.ndarray]) -> np.ndarray:
    tol0 = 0
    for w in weirdo: 
        tol0 += w.shape[0]
    fin = np.zeros((tol0, *weirdo[0].shape[1:]))
    m = 0
    for w in weirdo:
        for v in w:
            fin[m] = v[:]
            m += 1
    return fin

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="adding detail to a sequence of guide obj strands")

    parser.add_argument("inputObj", help="Full filepath to the input obj file", type = str)
    parser.add_argument("scalpFile", help="The obj file containing all the high-resolution strand roots; should correspond to pairing file", type = str)
    parser.add_argument("clumpingFile", help="The csv file that pairs the guide strands with their corresponding group of vertices in the scalp", type= str)
    parser.add_argument("outputObj", help="Full filepath to the output obj file", type = str)

    parser.add_argument("--amps", help="The .npz that contains FFT information for amplitude spectra sampling", type = str, default ='../../data/amp_angle_stats/fullCombStats/fullComb.objAmps.npz')
    parser.add_argument("--angs", help="The .npz that contains FFT information for phase spectra sampling", type = str, default ='../../data/amp_angle_stats/fullCombStats/fullComb.objAmps.npz')
    parser.add_argument("--tlRand", help="Range for tL randomization (range 0-1)", type=float, nargs = 2, default = [0.1, 0.6])
    parser.add_argument("--lenRand", help="Range for strand length in wisp (range 0-1)", type=float, nargs = 2, default = [0.8,1])
    parser.add_argument("--wispR", help="Strictly-cohered wisp radius range", type=float, nargs=2, default=[0.07,0.35])
    parser.add_argument("--dropout", help="Probability of having a vertex drop out in strict area (range 0-1)", type=float, default=0.5)

    args = parser.parse_args()
    
    print(sys.argv, flush=True)

    outputDir = os.path.split(args.outputObj)[0]
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    random.seed(1337)
    np.random.seed(1337)
    amps_container = np.load(args.amps)
    angs_container = np.load(args.angs)
    amps_coll = [amps_container[k] for k in amps_container]
    angs_coll = [angs_container[k] for k in angs_container]

    # load strand(s)
    v, e = io.read_obj_strands(args.inputObj)
    # load scalp
    scalp_file = args.scalpFile
    v_scalp = io.vert_read(scalp_file)
    # load clumping dictionary
    clumping_name = args.clumpingFile
    clumping_map = io.clumping_read(clumping_name)

    m1 = np.array([-5, 5,0])
    styled_verts = []
    styled_edges = []
    marker = 0
    percent_mark = 0
    for i in range(len(e)):
    # for i in range(40,41):
        percent = int((i/len(e))*100)
        if percent >= percent_mark:
            print(f'{datetime.datetime.now()}: reached {percent}%', flush=True)
            percent_mark += 10
        strand = v[e[i]]
        for j in range(len(clumping_map[i])):
            amps_rand = random.choice(amps_coll) #creating the random displacement at the loose portion
            angs_rand = random.choice(angs_coll)
            while len(amps_rand) != len(angs_rand):
                amps_rand = random.choice(amps_coll)
                angs_rand = random.choice(angs_coll)
            freqs = amps_rand*(np.cos(angs_rand) + 1j*np.sin(angs_rand))
            displacements = np.fft.irfft(freqs, axis = 0, n = 2*len(amps_rand))

            shifted_strand = io.par_shift(strand, m1, 2*random.random()-1, 2*random.random()-1, lambda t: io.grow_rate_map(t, args.wispR[0], args.wispR[1]))
            if (len(shifted_strand) < 10): # displacement downscaling: doing smaller winds when the total strand length is low
                displacements = displacements*len(shifted_strand)/10
            rerooted = rerooted_curl(v_scalp[clumping_map[i][j]], m1, args.dropout, args.tlRand[0] + (args.tlRand[1] - args.tlRand[0])*random.random(), displacements, shifted_strand, m1)
            
            rerooted = even_catmull(rerooted, len(rerooted), args.lenRand[0] + (args.lenRand[1] - args.lenRand[0])*random.random()) #length randomization
            styled_verts.append(rerooted[:])
            styled_edges.append(np.arange(marker, marker + len(rerooted)))
            marker += len(rerooted)
            # io.export_strand(rerooted, f"reroot_test{i}-{clumping_map[i][j]}.obj")
    print(f"{datetime.datetime.now()}: finished!")
    print(f"writing to {args.outputObj}", flush=True)
    io.export_obj(numpy_flat(styled_verts), styled_edges, args.outputObj)
