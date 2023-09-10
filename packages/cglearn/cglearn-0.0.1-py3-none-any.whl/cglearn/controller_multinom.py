from .as_freq_tb import as_freq_tb
from .ugtojtree import ug_to_jtree
from .junctiontree import SepTree
from .multinom_pc_learn import multinom_pc_learn
from .learn_complex_multinom import learn_complex_multinom
from .draw import draw
from .uig_multinom import naive_getug_multinom
from .multinom_skeleton_mkb import multinom_skeleton_mkb
from .learn_skeleton_multinom import learn_skeleton_multinom

def generate_pattern_discrete(amat, ds, colnames, p, method, sub_method):
    invalidInput = False
    if method == "lcd":
        if sub_method == "simple":
            algo = 0
        elif sub_method == "mkb":
            algo = 1
        else:
            invalidInput = True
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
        print("method = pc, sub_method = stable")
        print("method = pc, sub_method = original")
        print("method = markov_blnkt, sub_method = mbcsp")
        print("method = markov_blnkt, sub_method = original")
        print("method = lcd, sub_method = mkb")
        print("method = lcd, sub_method = simple (this method needs more work)")
        
        return

    freq_tb = as_freq_tb(ds)
    pat = None
    if algo == 0:
        uig = naive_getug_multinom(freq_tb, p, "simple")
        jt:SepTree = ug_to_jtree(uig)
        skel = learn_skeleton_multinom(jt, freq_tb, p)
        pat = learn_complex_multinom(skel, freq_tb, p)

    elif algo == 1:
        uig = naive_getug_multinom(freq_tb, p, "mkb")
        jt:SepTree = ug_to_jtree(uig)
        skel = learn_skeleton_multinom(jt, freq_tb, p)
        pat = learn_complex_multinom(skel, freq_tb, p)

    elif algo == 2:
        skel_pc = multinom_pc_learn(freq_tb, p, algMethod="stable")
        pat = learn_complex_multinom(skel_pc, freq_tb, p)
        
    elif algo == 3:
        skel_pc = multinom_pc_learn(freq_tb, p, algMethod="original")
        pat = learn_complex_multinom(skel_pc, freq_tb, p)
        
    elif algo == 4:
        skel_mkb = multinom_skeleton_mkb(freq_tb, p, ds, "mbcsp")
        pat = learn_complex_multinom(skel_mkb, freq_tb, p)

    elif algo == 5:
        skel_mkb = multinom_skeleton_mkb(freq_tb, p, ds, "original")
        pat = learn_complex_multinom(skel_mkb, freq_tb, p)
    
    customlables = {}
    for i in range(len(colnames)):
        customlables[i] = colnames[i]
    draw(pat, customlables)
    return pat