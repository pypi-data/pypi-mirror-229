from .freq_table import freq_tb
from .compress_freq_table import compress_freq_tb
import ctypes
from scipy.stats import chi2
import scipy.stats as stats
import os

# Performs a conditional independence test using a C library.
# table: Frequency table matrix.
# levels: List of levels(unique values) for each column in the frequency table.
# i0: First variable index.
# i1: Second variable index.
# Returns:
# tuple: A tuple containing the p-value, deviance, and degrees of freedom.
def cond_ind_test_c(table, levels, i0, i1):

    if os.name == 'posix':
        file_path = os.path.join(os.path.dirname(__file__), 'cond_ind_test.so')
        my_module = ctypes.CDLL(file_path)
    elif os.name == 'nt':
        file_path = os.path.join(os.path.dirname(__file__), 'cond_ind_test.dll')
        my_module = ctypes.windll.LoadLibrary(file_path)

    class CompressedData(ctypes.Structure):
        _fields_ = [("pval", ctypes.c_double),
                    ("dev", ctypes.c_double),
                    ("df", ctypes.c_double)]


    my_module.cond_ind_test.argtypes = [ctypes.POINTER(ctypes.c_int),
                                            ctypes.c_int,
                                            ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_int),
                                            ctypes.c_int,
                                            ctypes.c_int]
    my_module.cond_ind_test.restype = CompressedData
    # table_ptr = table.ctypes.data_as(ctypes.POINTER(ctypes.c_int))

    flattened_mat = table.flatten()
    # Create a new array of 'c_int' values and copy the flattened matrix
    c_int_array = (ctypes.c_int * flattened_mat.size)(*flattened_mat)


    # mat_ptr = mat.ctypes.data_as(ctypes.POINTER(ctypes.c_int))
    table_ptr = ctypes.cast(c_int_array, ctypes.POINTER(ctypes.c_int))

    levels_ptr = (ctypes.c_int * len(levels))(*levels)
    levels_ptr = ctypes.cast(levels_ptr, ctypes.POINTER(ctypes.c_int))
    row, col = table.shape
    result = my_module.cond_ind_test(table_ptr, row, col, levels_ptr, i0, i1)
    return result.pval, result.dev, result.df

# Performs a multinomial conditional independence test.
# tb: Frequency table object.
# u: First variable index.
# v: Second variable index.
# cond: List of variable indices for the conditional set. Defaults to an empty list.
# Returns: Dictionary containing the p-value, deviance, and degrees of freedom.
def multinom_ci_test(tb, u, v, cond=[]):
    # def pchisq(dev, dev_dof):
    #     p_value = 1.0 - chi2.cdf(dev, dev_dof)
    #     return p_value
    if not isinstance(tb, freq_tb):
        raise ValueError("tb should be an object of class freq.tb!")
    if any(col in cond for col in [u, v]):
        raise ValueError("The conditional set should not contain u or v!")
    if tb.table.shape[0] == 1:
        wtb = tb
    else:
        subset = []
        subset.append(u)
        subset.append(v)
        for e in cond:
            subset.append(e)
        wtb = compress_freq_tb(tb, subset)
    pval, dev, df = cond_ind_test_c(wtb.table, wtb.levels, 0, 1)
    pval = 1 - stats.chi2.cdf(dev, df)
    return {"pval": pval, "dev": dev, "df": df}