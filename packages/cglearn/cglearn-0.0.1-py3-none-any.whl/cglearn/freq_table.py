# Stores a frequency table object.
# table: Frequency table matrix.
# levels: List of levels(unique values) for each column in the frequency table.
# colnames: List of column names.
class freq_tb:
    def __init__(self, table, levels, colnames=None):
        self.table = table
        self.levels = levels
        self.colnames = colnames