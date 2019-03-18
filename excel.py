import pandas as pd


class FilenameExcel(object):
    def __init__(self, path):
        self.excel = self.read_excel(path)

    @classmethod
    def read_excel(cls, path):
        return pd.read_excel(path)

    def print_headers(self):
        print(self.excel.columns)

    def get_column(self, column_name):
        return self.excel[column_name]

    def get_rows(self):
        rows = []
        for index, row in self.excel.iterrows():
            rows.append([row['Name'], row['Duration']])
        return rows
