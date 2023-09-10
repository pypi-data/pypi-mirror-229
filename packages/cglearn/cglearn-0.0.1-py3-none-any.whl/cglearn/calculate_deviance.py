import numpy as np

# finds inverse of a matrix
# M - input matrix
# return inverse of the matrix, success/failure
def mat_inverse(M):
    inv = M
    failed = False
    try:
        inv = np.linalg.inv(M)
    except np.linalg.LinAlgError as err:
        failed = True
    return inv, failed

# finds product of 2 matrices
# x : First matrix.
# nrx : Number of rows in x.
# ncx : Number of columns in x.
# y : Second matrix.
# nry : Number of rows in y.
# ncy : Number of columns in y.
# inverseFailed : Flag indicating if matrix inversion failed.
# z : Resultant matrix.
# return inverse of the matrix, success/failure
def mat_prod(x, nrx, ncx, y, nry, ncy, inverseFailed, z):
    # Check if any element in x or y is NaN
    if nrx > 0 and ncx > 0 and nry > 0 and ncy > 0:
        if inverseFailed or np.isnan(x).any() or np.isnan(y).any():
            # Perform element-wise matrix multiplication
            for i in range(x.shape[0]):
                for k in range(y.shape[1]):
                    sum_val = 0.0
                    for j in range(x.shape[1]):
                        sum_val += x[i, j] * y[j, k]
                    z[i, k] = sum_val
        else:
            # Perform matrix multiplication using numpy's dot function
            z = np.dot(x, y)
    else:
        z.fill(0.0)
    
    return z

# perform a conditional independence test for normally distributed data using the deviance proposed in Whittaker (1989) pp180-181

# S - covariance matrix
# n_var - no of variables(columns)
# N - no of samples
# i - vertex 1
# j - vertex 2
# Q - separation set
# q - size of separation set

# returns chi value
def dev_ci_test(S, n_var, N, i, j, Q, q):
    subn = q + 2
    subvars = np.zeros(subn, dtype=int)
    Mmar = np.zeros((subn, subn), dtype=float)
    S11 = np.zeros((2, 2), dtype=float)
    S11_2 = np.zeros((2, 2), dtype=float)
    S12 = np.zeros((2, subn - 2), dtype=float)
    S21 = np.zeros((subn - 2, 2), dtype=float)
    S22 = np.zeros((subn - 2, subn - 2), dtype=float)
    S22inv = np.zeros((subn - 2, subn - 2), dtype=float)
    tmpmat1 = np.zeros((2, subn - 2), dtype=float)
    tmpmat = np.zeros((2, 2), dtype=float)
    
    subvars[0] = i
    subvars[1] = j
    for k in range(2, subn):
        subvars[k] = Q[k - 2]
    
    for k in range(subn):
        for l in range(subn):
            Mmar[k, l] = S[subvars[k]][subvars[l]]
            if k <= 1 and l > 1:
                S12[k, l - 2] = Mmar[k, l]
            if k > 1 and l <= 1:
                S21[k - 2, l] = Mmar[k, l]
            if k > 1 and l > 1:
                S22[k - 2, l - 2] = Mmar[k, l]
            if k <= 1 and l <= 1:
                S11[k, l] = Mmar[k, l]
    
    if subn - 2 > 0:
        S22inv, inverseFailed = mat_inverse(S22)
        tmpmat1 = mat_prod(S12, 2, subn-2, S22inv, subn-2, subn-2, inverseFailed, tmpmat1)
        tmpmat = mat_prod(tmpmat1, 2, subn-2, S21, subn-2, 2, inverseFailed, tmpmat)
        
        S11_2 = S11 - tmpmat
        
        chi_value = N * np.log(1.0 - S11_2[0][1]*S11_2[1][0] / (S11_2[0][0] * S11_2[1][1]))
    else:
        chi_value = N * np.log(1.0 - Mmar[0][1]*Mmar[1][0] / (Mmar[0][0] * Mmar[1][1]))
    
    # if chi_value is nan, then assign chivalue = chi2.ppf(1 - 1e-16, 1)
    # the above eqation gives us  68.7632522116684
    # hence no need to use 'from scipy.stats import chi2' just to get a constant value
    if np.isnan(chi_value):
        chi_value = 68.7632522116684

    return -chi_value