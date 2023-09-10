import ctypes
import numpy as np
from .freq_table import freq_tb
import os


# Compresses a frequency table using a C library.
# mat : Input frequency table matrix.
# Returns: Compressed frequency table matrix.
def compress_freq_table_c(mat):
    if os.name == 'posix':
        file_path = os.path.join(os.path.dirname(__file__), 'comp_freq_tb.so')
        my_module = ctypes.CDLL(file_path)
    elif os.name == 'nt':
        file_path = os.path.join(os.path.dirname(__file__), 'comp_freq_tb.dll')
        my_module = ctypes.windll.LoadLibrary(file_path)

    # define input and return types for C call
    class CompressedMatrix(ctypes.Structure):
        _fields_ = [("data", ctypes.POINTER(ctypes.c_int)),
                    ("row", ctypes.c_int),
                    ("col", ctypes.c_int)]
    my_module.compress_freq_table.argtypes = [ctypes.POINTER(ctypes.c_int),
                                            ctypes.c_int,
                                            ctypes.c_int]
    my_module.compress_freq_table.restype = CompressedMatrix

    flattened_mat = mat.flatten()
    # Create a new array of 'c_int' values and copy the flattened matrix
    c_int_array = (ctypes.c_int * flattened_mat.size)(*flattened_mat)

    mat_ptr = ctypes.cast(c_int_array, ctypes.POINTER(ctypes.c_int))

    # Get the dimensions of the matrix
    row, col = mat.shape
    # Call the compress_freq_table function
    compressed_mat = my_module.compress_freq_table(mat_ptr, row, col)
    compressed_mat = np.ctypeslib.as_array(compressed_mat.data, shape=(compressed_mat.row, compressed_mat.col))
    return compressed_mat

# Compresses a frequency table by removing specified columns.
# tb: Frequency table object to be compressed.
# subset: List of column names to be retained. If None, all columns except the last one will be retained. Defaults to None.
# Returns: Compressed frequency table object.
def compress_freq_tb(tb, subset=None):
    vnames = tb.colnames
    last = len(vnames)
    if subset is None:
        subset = vnames[:-1]
    idx = []
    for ele in subset:
        for i, v in enumerate(vnames[:-1]):
            if ele == v:
                idx.append(i)
                break
    if any(elem is None for elem in idx):
        raise ValueError("Invalid subset!")
    newlev = [tb.levels[i] for i in idx]
    idx.append(last-1)
    sub_table = tb.table[:, idx]
    newtb = compress_freq_table_c(sub_table)
    return freq_tb(table=newtb, levels=newlev, colnames=idx)