import pandas as pd
import xlsxwriter


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

class ExcelWriter(object):
    def __init__(self, file_path):
        self.file_path = file_path

    def create_excel(self, data, excel_columns):
        workbook = xlsxwriter.Workbook(self.file_path)
        worksheet = workbook.add_worksheet()

        row = 0
        col = 0

        for column_name in excel_columns:
            worksheet.write(row, col, column_name)
            col += 1

        # increment row
        row += 1
        for data_row in data:
            for key, value in data_row.items():
                worksheet.write(row, excel_columns.index(key), value)
            row += 1

        workbook.close()
