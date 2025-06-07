# Small octree implementation (trying to reduce amount of pip installs)

import numpy as np

class octreeNode:
    def __init__(self, data, max_coords, min_coords):
        self.points = data
        self.children = []
        self.max_coords = np.array(max_coords)
        self.min_coords = np.array(min_coords)
        self.is_leaf = False

# helper for octree initialization: makes the octants and populates them (a dictionary) 
def oct_split(points, max, min):
    avg = (np.array(max) + np.array(min)) / 2
    split_dict = {"uuu":[], "uud":[], "udu":[], "udd":[], "duu":[], "dud":[], "ddu":[], "ddd":[]}
    for p in points:
        split = ""
        if p[0] > avg[0]:
            split += 'u'
        else:
            split += 'd'
        if p[1] > avg[1]:
            split += 'u'
        else:
            split += 'd'
        if p[2] > avg[2]:
            split += 'u'
        else:
            split += 'd'
        split_dict[split].append(p)
    return split_dict

# makes the octree out of the big array of points
def make_octree(all_points : np.ndarray, threshold : float, u : np.ndarray, d : np.ndarray) -> octreeNode:
    if len(all_points) < threshold: # base case it's a leaf
        leaf_node = octreeNode(all_points, u, d)
        leaf_node.is_leaf = True
        return leaf_node
    #otherwise chop it up into 8 parts and go again
    split_dict = oct_split(all_points, u, d)
    root_node = octreeNode(None, u, d)
    avg = (np.array(u) + np.array(d)) / 2
    if len(split_dict["uuu"]) > 0:
       root_node.children.append(make_octree(split_dict["uuu"], threshold, u, avg))
    if len(split_dict["uud"]) > 0:
        root_node.children.append(make_octree(split_dict["uud"], threshold, [u[0], u[1], avg[2]], [avg[0], avg[1], d[2]]))
    if len(split_dict["udu"]) > 0:
        root_node.children.append(make_octree(split_dict["udu"], threshold, [u[0], avg[1], u[2]], [avg[0], d[1], avg[2]]))
    if len(split_dict["udd"]) > 0:
        root_node.children.append(make_octree(split_dict["udd"], threshold, [u[0], avg[1], avg[2]], [avg[0], d[1], d[2]]))
    if len(split_dict["duu"]) > 0:
        root_node.children.append(make_octree(split_dict["duu"], threshold, [avg[0], u[1], u[2]], [d[0], avg[1], avg[2]]))
    if len(split_dict["dud"]) > 0:
        root_node.children.append(make_octree(split_dict["dud"], threshold, [avg[0], u[1], avg[2]], [d[0], avg[1], d[2]]))
    if len(split_dict["ddu"]) > 0:
        root_node.children.append(make_octree(split_dict["ddu"], threshold, [avg[0], avg[1], u[2]], [d[0], d[1], avg[2]]))
    if len(split_dict["ddd"]) > 0:
        root_node.children.append(make_octree(split_dict["ddd"], threshold, avg, d))
    return root_node

# quick octree for finding coarse neighbors
def get_close_guess(v : np.ndarray, root : octreeNode, eps : float) -> list:
    # first determine if vert is even within eps of box
    neighbors = []
    if root == None:
        return neighbors
    u = root.max_coords
    d = root.min_coords
    if v[0] > u[0] + eps or v[0] < d[0] - eps or v[1] > u[1] + eps or v[1] < d[1] - eps or v[2] > u[2] + eps or v[2] < d[2] - eps:
        return neighbors
    # terminate if leaf
    if root.is_leaf:
        return root.points
    # otherwise it's branching: better append neighbors a bit!
    for child in root.children:
        neighbors.extend(get_close_guess(v, child, eps))
    return neighbors

# finding neighbors of a vert from an octree
def closest_guide_ind_faster(vert : np.ndarray, guide_octree : octreeNode, eps : float) -> tuple[np.ndarray, float, np.ndarray, float]:
    coarse_neighbors = get_close_guess(vert, guide_octree, eps)
    new_eps = eps
    while len(coarse_neighbors) <= 1:
        new_eps = 2*new_eps
        # print(f"new_eps: {new_eps}")
        coarse_neighbors = get_close_guess(vert, guide_octree, new_eps)
    closest_dist2 = np.sum((vert - np.array(coarse_neighbors[0]))**2)
    closest_dist2_second = np.sum((vert - np.array(coarse_neighbors[0]))**2)
    closest_p = np.array(coarse_neighbors[0])
    closest_p_second = np.array(coarse_neighbors[0])
    # print(f"coarse_neighbors len: {len(coarse_neighbors)}")
    for p in coarse_neighbors:
        cand_dist2 = np.sum((vert - p)**2)
        if cand_dist2 < closest_dist2:
            closest_p_second = closest_p
            closest_p = p
            closest_dist2_second = closest_dist2
            closest_dist2 = cand_dist2
            continue
        if cand_dist2 < closest_dist2_second:
            closest_dist2_second = cand_dist2
            closest_p_second = p
    return closest_p, closest_dist2, closest_p_second, closest_dist2_second

# gets n closest guide indices inside guide_octree
# returns tuple: 
# list of indices (ordered by 1st closest to nth closest), list of square distances (also ordered)
def closest_guide_inds(vert: np.ndarray, guide_octree: octreeNode, eps: float, n: int) -> tuple[np.ndarray[np.ndarray], np.ndarray[float]]:
    coarse_neighbors = get_close_guess(vert, guide_octree, eps)
    new_eps = eps
    while len(coarse_neighbors) < n:
        new_eps = 2*new_eps
        # print(f"new_eps: {new_eps}")
        coarse_neighbors = get_close_guess(vert, guide_octree, new_eps)
    close_ps = np.empty((n, 3))
    close_d2s = np.empty(n)
    for i in range(n):
        close_ps[i] = (np.array(coarse_neighbors[0][:]))
        close_d2s[i] = (float('inf'))
    # print(f"coarse_neighbors len: {len(coarse_neighbors)}")
    for p in coarse_neighbors:
        cand_dist2 = np.sum((vert - p)**2)
        for i in range(n): # slice the distance and point into the correct place
            if cand_dist2 < close_d2s[i]:
                close_d2s[i+1:] = close_d2s[i:-1]
                close_ps[i+1:] = close_ps[i:-1]
                close_d2s[i] = cand_dist2
                close_ps[i] = p[:]
                break
    return close_ps, close_d2s

def average_leaf_diam(root: octreeNode) -> float:
    if root == None:
        return -1.0
    if root.is_leaf:
        return np.max(np.array([root.max_coords[0] - root.min_coords[0], root.max_coords[1] - root.min_coords[1], root.max_coords[2] - root.min_coords[2]]))
    distances = np.array([average_leaf_diam(l) for l in root.children])
    return np.average(distances)