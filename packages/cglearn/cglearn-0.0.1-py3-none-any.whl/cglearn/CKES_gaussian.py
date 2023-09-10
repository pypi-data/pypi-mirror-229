import numpy as np
import random
from .is_chain_graph import is_acyclic
from .norm_ci_test import gaussCItest

class CKESAlgorithmGaussian:
    def __init__(self, nrOfNoChangeIterations, nrOfGraphsToTestInEqClass, nrOfSplitOrMergingsPerGraphChange, cg):
        self.nrOfNoChangeIterations = nrOfNoChangeIterations
        self.nrOfGraphsToTestInEqClass = nrOfGraphsToTestInEqClass
        self.nrOfSplitOrMergingsPerGraphChange = nrOfSplitOrMergingsPerGraphChange
        self.cg = cg
        self.n = len(cg[0])

    def hasUndirected(self, x, y, cg):
        return cg[x][y] == 1 and cg[y][x] == 1
    
    def removeEdge(self, x, y, cg):
        cg[x][y] = 0
        cg[y][x] = 0

        return
    
    def addUndirected(self, x, y, cg):
        cg[x][y] = 1
        cg[y][x] = 1
        return True
    
    def hasDirected(self, x, y, cg):
        return cg[x][y] == 1 and cg[y][x] == 0
    
    def addDirected(self, x, y, cg):
        cg[x][y] = 1
        cg[y][x] = 0
        return True
    
    def hasEdge(self, x, y, cg):
        return cg[x][y] == 1 or cg[y][x] == 1
    
    def get_component_numbers(self, component_numbers, cg):
        n_vars = len(component_numbers)
        for i in range(n_vars):
            component_numbers[i] = -1
        current_cc_nr = 0

        for i in range(n_vars):
            if component_numbers[i] == -1:
                component_numbers[i] = current_cc_nr
                change = True
                while change:
                    change = False
                    for k in range(i, n_vars):
                        if component_numbers[k] == current_cc_nr:
                            for l in range(i, n_vars):
                                if (self.hasUndirected(k, l, cg) and component_numbers[l] != current_cc_nr):
                                    component_numbers[l] = current_cc_nr
                                    change = True
                current_cc_nr += 1

        return current_cc_nr



    
    def splitIfFeasible(self, U, L, cg):
        paL = [0]*self.n
        neLcapU = [0]*self.n
        
        for i in range(self.n):
            if L[i] == 1:
                for j in range(self.n):
                    if self.hasDirected(j, i, cg):
                        paL[j] = 1
                    elif self.hasUndirected(i, j, cg) and U[j] == 1:
                        neLcapU[j] = 1
        
        for a in range(self.n):
            if neLcapU[a] == 1:
                for b in range(self.n):
                    if paL[b] == 1 and not self.hasDirected(b, a, cg):
                        return False
        
        for a in range(self.n):
            if neLcapU[a] == 1:
                for b in range(self.n):
                    if a != b and neLcapU[b] == 1 and not self.hasEdge(a, b, cg):
                        return False
        
        for a in range(self.n):
            if L[a] == 1:
                for b in range(self.n):
                    if U[b] == 1 and self.hasUndirected(b, a, cg):
                        self.addDirected(b, a, cg)
        
        return True

    def mergeIfFeasible(self, U, L, cg):
        paL = [0]*self.n
        
        for i in range(self.n):
            if L[i] == 1:
                for j in range(self.n):
                    if self.hasDirected(j, i, cg):
                        paL[j] = 1
        
        for a in range(self.n):
            if U[a] == 1 and paL[a] == 1:
                for b in range(self.n):
                    if a != b and paL[b] == 1 and U[b] == 0 and not self.hasDirected(b, a, cg):
                        return False
        
        for a in range(self.n):
            if U[a] == 1 and paL[a] == 1:
                for b in range(self.n):
                    if a != b and U[b] == 1 and paL[b] == 1 and not self.hasEdge(a, b, cg):
                        return False
        
        for a in range(self.n):
            if L[a] == 1:
                for b in range(self.n):
                    if U[b] == 1 and self.hasDirected(b, a, cg):
                        self.addUndirected(b, a, cg)
        
        return True

    def performFeasibleMerge(self, cg):
        componentOrdering = list(range(self.get_component_numbers(self.inComponent, cg)))
        random.shuffle(componentOrdering)

        for low in componentOrdering:
            lowerComponentNodes = [0]*self.n
            parentComponents = []

            for i in range(self.n):
                if self.inComponent[i] == low:
                    lowerComponentNodes[i] = 1
                    for j in range(self.n):
                        if self.hasDirected(j, i, cg) and self.inComponent[j] not in parentComponents:
                            parentComponents.append(self.inComponent[j])

            if parentComponents:
                random.shuffle(parentComponents)

                for up in parentComponents:
                    upperComponentNodes = [0]*self.n

                    for i in range(self.n):
                        if self.inComponent[i] == up:
                            upperComponentNodes[i] = 1

                    if self.mergeIfFeasible(upperComponentNodes, lowerComponentNodes, cg):
                        return True

        return False

    def performFeasibleSplitRecursively(self, i, nodesInComponent, U, L, cg):
        if i == len(nodesInComponent):
            if any(val == 1 for val in U) and any(val == 1 for val in L):
                success = self.splitIfFeasible(U, L, cg)
                return success
            else:
                return False
        else:
            if random.randint(0, 1) == 0:
                U[nodesInComponent[i]] = 1
                if self.performFeasibleSplitRecursively(i + 1, nodesInComponent, U, L, cg):
                    return True
                else:
                    U[nodesInComponent[i]] = 0
                    L[nodesInComponent[i]] = 1
                    return self.performFeasibleSplitRecursively(i + 1, nodesInComponent, U, L, cg)
            else:
                L[nodesInComponent[i]] = 1
                if self.performFeasibleSplitRecursively(i + 1, nodesInComponent, U, L, cg):
                    return True
                else:
                    L[nodesInComponent[i]] = 0
                    U[nodesInComponent[i]] = 1
                    return self.performFeasibleSplitRecursively(i + 1, nodesInComponent, U, L, cg)

    def performFeasibleSplit(self, cg):
        componentOrdering = list(range(self.get_component_numbers(self.inComponent, cg)))
        random.shuffle(componentOrdering)

        for comp in componentOrdering:
            nodesInComponent = [i for i in range(self.n) if self.inComponent[i] == comp]

            if len(nodesInComponent) > 1:
                if self.performFeasibleSplitRecursively(0, nodesInComponent, [0]*self.n, [0]*self.n, cg):
                    return True

        return False

    def learnLWFCG(self, pThresh, ds):
        cov = np.cov(ds, rowvar=False, bias=True)
        d = np.sqrt(cov.diagonal())
        parcor = ((cov.T/d).T)/d
        suffStat = {'C' : parcor, 'n' : len(ds)}
        cg = self.cg

        n = len(cg[0])
        self.inComponent = [0] * n
        for i in range(n):
            self.inComponent[i] = 0

        visitedCGs = set()
        iterationsWithNoImprovement = 0
        bestCG = cg.copy()

        while iterationsWithNoImprovement < self.nrOfNoChangeIterations:
            iterationsWithNoImprovement += 1
            pRemove = pThresh
            pAdd = pThresh

            for _ in range(self.nrOfGraphsToTestInEqClass):
                for x in range(n):
                    for y in range(n):
                        if self.hasUndirected(x, y, cg):
                            self.removeEdge(x, y, cg)
                            cg_tuple = tuple(map(tuple, cg))
                            if cg_tuple in visitedCGs:
                                self.addUndirected(x, y, cg)
                                continue
                            self.addUndirected(x, y, cg)
                            bdX = []
                            bdY = []
                            for bdVar in range(n):
                                if bdVar != x and bdVar != y:
                                    if self.hasDirected(bdVar, x, cg) or self.hasUndirected(bdVar, x, cg):
                                        bdX.append(bdVar)
                                    if self.hasDirected(bdVar, y, cg) or self.hasUndirected(bdVar, y, cg):
                                        bdY.append(bdVar)
                            pValOp = min(gaussCItest(x, y, bdX, suffStat), gaussCItest(x, y, bdY, suffStat))
                            if pValOp > pRemove:
                                pRemove = pValOp
                                self.removeEdge(x, y, cg)
                                bestCG = cg.copy()
                                self.addUndirected(x, y, cg)
                        elif self.hasDirected(x, y, cg):
                            self.removeEdge(x, y, cg)
                            cg_tuple = tuple(map(tuple, cg))
                            if cg_tuple in visitedCGs:
                                self.addDirected(x, y, cg)
                                continue
                            self.addDirected(x, y, cg)
                            bdY = []
                            for bdVar in range(n):
                                if bdVar != x and bdVar != y and (self.hasDirected(bdVar, y, cg) or self.hasUndirected(bdVar, y, cg)):
                                    bdY.append(bdVar)
                            pValOp = gaussCItest(x, y, bdY, suffStat)
                            if pValOp > pRemove:
                                pRemove = pValOp
                                self.removeEdge(x, y, cg)
                                bestCG = cg.copy()
                                self.addDirected(x, y, cg)
                        elif pRemove == pThresh and x != y and not self.hasEdge(x, y, cg):
                            bdX = []
                            bdY = []
                            for bdVar in range(n):
                                if bdVar != x and bdVar != y:
                                    if self.hasDirected(bdVar, x, cg) or self.hasUndirected(bdVar, x, cg):
                                        bdX.append(bdVar)
                                    if self.hasDirected(bdVar, y, cg) or self.hasUndirected(bdVar, y, cg):
                                        bdY.append(bdVar)
                            pValX = gaussCItest(x, y, bdX, suffStat)
                            pValY = gaussCItest(x, y, bdY, suffStat)
                            addDirectedPossible = False
                            addUndirectedPossible = False
                            if pValY < pAdd:
                                addDirectedPossible = True
                                addUndirectedPossible = True
                            elif pValX < pAdd:
                                addUndirectedPossible = True

                            if addDirectedPossible:
                                self.addDirected(x, y, cg)
                                if is_acyclic(cg):
                                    pAdd = pValY
                                    bestCG = cg.copy()
                                else:
                                    addDirectedPossible = False
                                self.removeEdge(x, y, cg)

                            if not addDirectedPossible and addUndirectedPossible:
                                self.addUndirected(x, y, cg)
                                if is_acyclic(cg):
                                    pAdd = min(pValX, pValY)
                                    bestCG = cg.copy()
                                self.removeEdge(x, y, cg)
                
                for j in range(self.nrOfSplitOrMergingsPerGraphChange):
                    if random.randint(0, 1) == 1:
                        self.performFeasibleMerge(cg)
                    else:
                        self.performFeasibleSplit(cg)


            if pRemove != pThresh or pAdd != pThresh:
                iterationsWithNoImprovement = 0
                cg = bestCG.copy()
                cg_tuple = tuple(map(tuple, cg))
                visitedCGs.add(cg_tuple)

        ans = cg.copy()
        bestCG = None
        cg = None
        return ans