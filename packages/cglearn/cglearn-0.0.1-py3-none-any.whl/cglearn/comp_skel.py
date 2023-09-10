import numpy as np
from math import comb

# This function compares given 2 skeletons of chain graphs
#
# truepat - true skeleton of a chain graph
# pat - learned skeleton of a chain graph
#
# returns 
# { numTrueEdges,missingEdges extraEdges, shd, tpr, tdr, fpr, acc }
def comp_skel(trueskel, skel):
    # finds missing edges and extra edges in learned skeleton
    missingEdges = len(np.where( (trueskel == 1) & (skel == 0) )[0])/2
    extraEdges = len(np.where( (skel == 1) & (trueskel == 0) )[0])/2

    numTrueEdges = len(np.where( (trueskel == 1))[0])/2 #all trueskel edges
    numLearnedEdges = len(np.where( (skel == 1))[0])/2 #all skel edges

    tp = numLearnedEdges - extraEdges
    N = comb(len(trueskel), 2) - numTrueEdges
    tn = N - extraEdges
    fp = extraEdges
    fn = numTrueEdges - numLearnedEdges if numTrueEdges > numLearnedEdges else 0
    tpr = tp / (tp+fn)
    fpr = fp / (fp + tn)
    tnr = tn / (tn + fp)
    acc = (tp + tn) / (tp + tn + fp + fn)
    tdr = tp / numLearnedEdges

    return {
        'numTrueEdges': numTrueEdges,
        'missingEdges': missingEdges,
        'extraEdges': extraEdges,
        'tpr' : tpr,
        'tdr' : tdr,
        'fpr' : fpr,
        'acc' : acc,
        'tnr' : tnr,
    }