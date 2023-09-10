from .uig_norm import get_uig_norm
import numpy as np
from .ugtojtree import ug_to_jtree
from .junctiontree import SepTree
from .learn_skeleton_norm import learn_skeleton_norm
from .learn_complex_norm import learn_complex_norm
from .gaussianpclearn import gaussian_pc_learn
from .gaussian_skeleton_mkb import gaussian_skeleton_mkb
from .draw import draw

def generate_pattern_gaussian(amat, ds, colnames, p, method, sub_method):
    invalidInput = False
    if method == "lcd":
        algo = 1
    elif method == "pc":
        if sub_method == "stable":
            algo = 2
        elif sub_method == "original":
            algo = 3
        else:
            invalidInput = True
    elif method == "markov_blnkt":
        if sub_method == "mbcsp":
            algo = 4
        elif sub_method == "original":
            algo = 5
        else:
            invalidInput = True
    else:
        invalidInput = True

    if invalidInput:
        print("Please provide correct input, following are the valid ones ")
        print("method = lcd, sub_method = ")
        print("method = pc, sub_method = stable")
        print("method = pc, sub_method = original")
        print("method = markov_blnkt, sub_method = mbcsp")
        print("method = markov_blnkt, sub_method = original")
        return

    n = len(ds)
    cov = np.cov(ds, rowvar=False, bias=True)

    if algo == 1:
        # discreet lcd
        uig = get_uig_norm(ds, p)
        jt:SepTree = ug_to_jtree(uig)
        skel = learn_skeleton_norm(jt, cov, n, p)
        pat = learn_complex_norm(skel, cov, n, p)

    elif algo == 2:
        pc_skel = gaussian_pc_learn(cov, n, p, algMethod="stable")
        pat = learn_complex_norm(pc_skel, cov, n, p)

    elif algo == 3:
        pc_skel = gaussian_pc_learn(cov, n, p, algMethod="original")
        pat = learn_complex_norm(pc_skel, cov, n, p)

    elif algo == 4:
        mkb_skel = gaussian_skeleton_mkb(cov, n, p, ds, "mbcsp")
        pat = learn_complex_norm(mkb_skel, cov, n, p)

    elif algo == 5:
        mkb_skel = gaussian_skeleton_mkb(cov, n, p, ds, "original")
        pat = learn_complex_norm(mkb_skel, cov, n, p)

    customlables = {}
    for i in range(len(colnames)):
        customlables[i] = colnames[i]
    draw(pat, customlables)
    return pat