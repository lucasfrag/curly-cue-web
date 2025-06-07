#DFT operations on strands

import file_io as io
import numpy as np

def fft_truncate(arr: np.ndarray, amt: int, axis = 0) -> np.ndarray:
    """ Sets <amt> elements in the RFFT vector of <arr> to zero, then returns IRFFT"""
    freq = np.fft.rfft(arr, axis = axis)
    for i in range(1, amt + 1):
        freq[-i] = 0
    return np.fft.irfft(freq, axis = axis, n = len(arr))

def fft_keep_slow(arr: np.ndarray, amt: int, axis = 0) -> np.ndarray:
    """ Keeps <amt> elements in the RFFT vector of <arr>, then returns IRFFT"""
    freq = np.fft.rfft(arr, axis = axis)
    t_f = np.zeros(freq.shape, dtype=np.complex128)
    for i in range(0, amt):
        t_f[i] = freq[i]
    return np.fft.irfft(t_f, axis = axis, n = len(arr))

def get_centercurve(strand: np.ndarray):
    """ Obtains centercurve of some strand using DFT truncation"""
    # read in verts and edges (don't forget to change depending on format of "l [verts]" lines)
    # v_before, e_before = io.read_obj_strands_blended(filename)
    ds = io.verts_to_displacements(strand)
    freqs = int(np.floor(len(ds)/2) + 1)
    trunc_f = max(min(freqs - 3,3), 1) # gotta keep at least 1 
    ds_trunc = fft_keep_slow(ds, trunc_f)
    centered = io.displacements_to_verts(ds_trunc, strand[0])
    center_shift = np.sum(strand-centered, axis = 0)/len(strand)
    centered = centered + center_shift #center-shift finding (derived from optimizing point-wise distance sum)
    return centered

# does rfft to freq vector according to axis, then truncates amt of slow frequencies to 0
# then does inverse rfft
def hi_pass(arr: np.ndarray, amt: int, axis = 0) -> np.ndarray:
    """ RFFT on <arr>, then sets <amt> elements up front to 0, then returns IRFFT"""
    freq = np.fft.rfft(arr, axis = axis)
    for i in range(0, amt):
        freq[i] = 0
    return np.fft.irfft(freq, axis = axis, n = len(arr))

# does fft-ification and interpolates into something between arr0 and arr1
def fft_interpolate(arr0: np.ndarray, arr1: np.ndarray, t = 0.5, axis = 0) -> np.ndarray:
    """ RFFT on <arr0> and <arr1>, interpolates with <t>, then returns linear combo IRFFT"""
    freq0 = np.fft.rfft(arr0, axis = axis)
    freq1 = np.fft.rfft(arr1, axis = axis)
    assert len(freq0) == len(freq1), f"fft_interpolate: arr0 (len {len(arr0)}) and arr1 (len {len(arr1)}) mismatch"
    freq = (1-t) * freq0 + t * freq1
    return np.fft.irfft(freq, axis = axis, n = len(arr0))

# gets list of arrays, averages over each array element
# also gets std div
# theoretically a bit odd for shorter strands eh
def padding_stats(arrs: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """ A helper for fft_stats to get avg and std_div of formatted data"""
    max_len = 0
    for a in arrs:
        cand_len = len(a)
        if cand_len > max_len:
            max_len = cand_len
    padded_data = np.zeros((len(arrs), max_len,arrs[0].shape[-1]),dtype=np.complex128)
    for i in range(0, len(padded_data)):
        padded_data[i] = np.pad(arrs[i],((0,max_len-len(arrs[i])),(0,0)), mode = 'constant')
    avg = np.average(padded_data, axis = 0)
    div = np.std(padded_data, axis = 0)
    return avg, div

# does fft stat-finding given a vert and edge array from an obj
# first stat: average, second stat: standard deviation
def fft_stats(verts: np.ndarray[np.ndarray], edges: list[list[int]]) -> tuple[np.ndarray, np.ndarray]:
    """ Obtains basic fft average and std_div from set of strands (NOT CENTRAL DISPLACEMENT VERSION)"""
    all_freqs = []
    for st in edges:
        cos = verts[st]
        ds = io.verts_to_displacements(cos)
        freq = np.fft.rfft(ds, axis=0)
        all_freqs.append(freq[:])
    return padding_stats(all_freqs)

def get_central_displacements(verts: np.ndarray[np.ndarray], mode: int = 2) -> np.ndarray[np.ndarray]:
    """ Obtains central displacements from strand defined by <verts> in order"""
    if mode == 2: #2D projection option
        disps = np.empty((len(verts), 2))
    else: #3D projection option
        disps = np.empty((len(verts), 3))
    centrals = get_centercurve(verts)
    offs = verts - centrals
    frames = io.make_frames(centrals, verts[0] - centrals[0])
    if mode == 2:
        for i in range(len(disps)):
            disps[i][0] = np.dot(offs[i],frames[i][0])
            disps[i][1] = np.dot(offs[i],frames[i][1])
    else: 
        for i in range(len(disps)):
            disps[i][0] = np.dot(offs[i],frames[i][0])
            disps[i][1] = np.dot(offs[i],frames[i][1])
            disps[i][2] = np.dot(offs[i],frames[i][2])
    return disps

def wind_displacements(centers: np.ndarray[np.ndarray], ds: np.ndarray[np.ndarray], up: np.ndarray, mode: int = 2) -> np.ndarray[np.ndarray]:
    """ Winds central displacements around center strand"""
    winded = np.empty(centers.shape)
    frames = io.make_frames(centers, up)
    assert len(centers) <= len(ds), f"len(centers): {len(centers)} | len(ds): {len(ds)}"
    if mode == 2:
        for i in range(len(winded)):
            winded[i] = centers[i] + frames[i][0]*ds[i][0] + frames[i][1]*ds[i][1]
    else:
        for i in range(len(winded)):
            winded[i] = centers[i] + frames[i][0]*ds[i][0] + frames[i][1]*ds[i][1] + frames[i][2]*ds[i][2]
    return winded

def fft_central_stats(verts: np.ndarray[np.ndarray], edges: list[list[int]]) -> tuple[np.ndarray, np.ndarray]:
    """ Obtains average and std_div of central displacement spectra"""
    all_freqs = []
    for st in edges:
        cos = verts[st]
        ds = get_central_displacements(cos)
        freq = np.fft.rfft(ds, axis = 0)
        all_freqs.append(freq[:])
    return padding_stats(all_freqs)

def spec_add(a: np.ndarray[np.ndarray], b: np.ndarray[np.ndarray], fa: np.ndarray, fb: np.ndarray) -> np.ndarray[np.ndarray]:
    """ Helper for adding two spectra that have slightly different resolutions"""
    if len(a) == len(b):
        return a + b
    r_val = a
    for i, wb in enumerate(fb):
        min_ind = np.abs(fa-wb).argmin() #ayo numpy trickery eh
        r_val[min_ind] += b[i] 
    return r_val

def resampled_stats(a: list[np.ndarray], spec_target: np.ndarray, spec_collection: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """ Helper for obtaining mean and std_div of frequency spectra"""
    max_len = len(spec_target)
    dim = a[0].shape[-1]
    resampled_collection = np.empty((len(a), max_len, dim))
    for i in range(len(resampled_collection)):
        for d in range(dim):
            resampled_collection[i][:,d] = np.interp(spec_target, spec_collection[i], a[i][:,d])
    mean = np.average(resampled_collection, axis = 0)
    div = np.std(resampled_collection, axis = 0)
    return mean, div

def resampled_sum(a: list[np.ndarray], spec_target: np.ndarray, spec_collection: list[np.ndarray]) -> np.ndarray:
    """ Helper for adding different-resolution frequency spectra"""
    max_len = np.max([len(f) for f in a])
    dim = a[0].shape[-1]
    resampled_collection = np.empty((len(a), max_len, dim))
    for i in range(len(resampled_collection)):
        for d in range(dim):
            resampled_collection[i][:,d] = np.interp(spec_target, spec_collection[i], a[i][:,d])
    sum = np.sum(resampled_collection, axis = 0)
    return sum
        
def fft_amp_angle_stats(verts: np.ndarray[np.ndarray], edges: list[list[int]]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """ Given a big set of strands, obtains averaged amplitude and frequency spectra of central displacements"""
    amp_collection = []
    re_collection = []
    im_collection = []
    spec_collection = []
    for e in edges:
        strand = verts[e]
        ds = get_central_displacements(strand)
        freq = np.fft.rfft(ds, axis = 0)
        freq_a = np.abs(freq)
        freq_re = np.real(freq)/freq_a
        freq_im = np.imag(freq)/freq_a

        spec_collection.append(np.fft.rfftfreq(len(ds)))
        amp_collection.append(freq_a[:])
        re_collection.append(freq_re[:])
        im_collection.append(freq_im[:])
    spec_target = np.fft.rfftfreq(np.max([len(e) for e in edges]))
    amp_avg, amp_sig = resampled_stats(amp_collection, spec_target, spec_collection)
    re_mean, re_sig = resampled_stats(re_collection, spec_target, spec_collection)
    im_mean, im_sig = resampled_stats(im_collection, spec_target, spec_collection)
    ang_avg = np.arctan2(im_mean, re_mean)
    ang_sig = np.arctan2(im_sig, re_sig)
    return amp_avg, amp_sig, ang_avg, ang_sig

def fft_amp_angle_collect(verts: np.ndarray[np.ndarray], edges: list[list[int]]) -> tuple[list[np.ndarray], list[np.ndarray]]:
    """ Given a big set of strands, obtains all amplitude and frequency spectra of central displacements"""
    amp_collection = []
    angle_collection = []
    for e in edges:
        strand = verts[e]
        ds = get_central_displacements(strand)
        freq = np.fft.rfft(ds, axis = 0)
        freq_a = np.abs(freq)
        freq_re = np.real(freq)/freq_a
        freq_im = np.imag(freq)/freq_a
        strand_angs = np.arctan2(freq_im, freq_re)

        amp_collection.append(freq_a[:])
        angle_collection.append(strand_angs[:])
    return amp_collection, angle_collection

def polar_to_complex(norm_arr: np.ndarray[np.ndarray], arg_arr: np.ndarray[np.ndarray]) -> np.ndarray[np.ndarray]:
    """ Helper for converting between polar coordinates and complex coordinates"""
    return norm_arr*(np.cos(arg_arr) + 1j* np.sin(arg_arr))