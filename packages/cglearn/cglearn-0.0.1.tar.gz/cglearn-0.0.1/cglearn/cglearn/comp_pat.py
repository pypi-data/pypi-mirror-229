import numpy as np
from math import comb

# This function compares given 2 patterns of chain graphs
#
# truepat - true pattern of a chain graph
# pat - learned pattern of a chain graph
#
# returns 
# { trueArrows,missingArrows extraArrows, shd, tpr, tdr, fpr, acc }
def comp_pat(truepat, pat):
    # shd
    # remove bidirectional edges
    shd = len(np.where((truepat == 0) & (truepat.T == 0) & ((pat == 1) | (pat.T == 1)))[0])
    # add bidirectional edges
    shd += len(np.where((truepat == 1) & (truepat.T == 1) & ((pat == 0) | (pat.T == 0)))[0])
    # since we are counting birectional twice, we need to divide it by 2
    shd /= 2
    # add, remove, change directional edge
    shd += len(np.where((truepat == 1) & (truepat.T == 0) & (pat == 0))[0])
    shd += len(np.where((truepat == 1) & (truepat.T == 0) & (pat == 1) & (pat.T == 1))[0])

    # finds true complex arrows, missing arrows in learned pattern and extra arrows in leared pattern
    trueArrows = len(np.where(truepat - truepat.T == 1)[0])
    missingArrows = len(np.where( (truepat == 1) & (truepat.T == 0) & ((pat != 1) | (pat.T != 0)) )[0])
    extraArrows = len(np.where( (pat == 1) & (pat.T == 0) & ((truepat != 1) | (truepat.T != 0)) )[0])
    trueEdges = len(np.where( (truepat == 1) & (truepat.T == 1))[0])/2 # all undirectional edges
    learnedArrows = len(np.where( (pat == 1) & (pat.T == 0))[0]) #all pat edges
    learnedEdges = len(np.where( (pat == 1) & (pat.T == 1))[0])/2
    missingEdges = len(np.where( (truepat == 1) & (truepat.T == 1) & ( (pat!=1) | (pat.T!=1)) )[0])/2
    extraEdges = len(np.where( (pat == 1) & (pat.T == 1) & ( (truepat!=1) | (truepat.T!=1)) )[0])/2

    tdr = shd = tpr = fpr = tnr = acc = 0

    try:
        tp = (learnedEdges - extraEdges) + (learnedArrows - extraArrows)
        N = 3*comb(len(truepat), 2) - trueEdges - trueArrows
        tn = N - extraArrows - extraEdges
        fp = extraEdges + extraArrows
        fn = (trueEdges - learnedEdges) + (trueArrows - learnedArrows)
        if(fn < 0):
            fn = 0
        tpr = tp / (tp+fn)
        fpr = fp / (fp + tn)
        tnr = tn / (tn + fp)
        acc = (tp + tn) / (tp + tn + fp + fn)
        tdr = tp / (learnedEdges + learnedArrows)
    except ZeroDivisionError:
        print("ZeroDivisionError")
    except:
        print("error occured")


    # numEdgesTruePattern = len(np.where( (truepat == 1) & (truepat.T == 0))[0]) # all directional edges
    # numEdgesTruePattern += len(np.where( (truepat == 1) & (truepat.T == 1))[0])/2 # all undirectional edges
    # numEdgesLearnedPattern = len(np.where( (pat == 1) & (pat.T == 0))[0]) #all pat edges
    # numEdgesLearnedPattern += len(np.where( (pat == 1) & (pat.T == 1))[0])/2

    # tp = numEdgesLearnedPattern - extraArrows
    # N = comb(len(truepat), 2) - numEdgesTruePattern
    # tn = N - extraArrows
    # tpr = tp / numEdgesTruePattern
    # tdr = tp / numEdgesLearnedPattern
    # fpr = extraArrows / N
    # acc = (tp + tn) / (numEdgesTruePattern + N)

    return {
        'trueArrows': trueArrows,
        'missingArrows': missingArrows,
        'extraArrows': extraArrows,
        'TrueEdges': trueEdges,
        'missingEdges': missingEdges,
        'extraEdges': extraEdges,
        'shd': shd,
        'tpr' : tpr,
        'tdr' : tdr,
        'fpr' : fpr,
        'acc' : acc,
        'tnr' : tnr,
    }