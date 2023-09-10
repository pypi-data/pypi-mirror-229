import numpy as np
from .freq_table import freq_tb
from .compress_freq_table import compress_freq_tb

# Convert a matrix into a frequency table.
# mat : Input matrix.
# Returns: freq_tb: Frequency table object
def as_freq_tb(mat):
    n = mat.shape[0]
    mat = mat.astype(int)
    levels = np.apply_along_axis(lambda x: len(np.unique(x)), axis=0, arr=mat)
    num_cols = mat.shape[1]
    col_names = [i for i in range(0, num_cols + 1)]
    tb = freq_tb(table=np.hstack((mat, np.ones((n, 1), dtype=int))),
                 levels=levels, colnames=col_names)
    # return compress_freq_tb(tb, [0, 1, 2, 6, 7])
    return compress_freq_tb(tb)