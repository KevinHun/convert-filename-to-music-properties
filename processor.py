import os
from converter import Converter


class Processor(object):
    def __init__(self, path_to_folder='files', debug=False, format_excel='xls', default_labels=None):
        # check if path exists
        if os.path.exists(path_to_folder):
            self.path_to_folder = path_to_folder
        elif path_to_folder == 'files':
            os.makedirs('files')
        else:
            raise ValueError("Path {0} doesn't exist".format(path_to_folder))

        self.debug = debug
        self.format_excel = format_excel
        self.default_labels = default_labels
        self.check_and_setup_folder_structure()

    def check_and_setup_folder_structure(self):
        # check if process map exists
        process_folder = os.path.join(self.path_to_folder, 'process')
        if not os.path.exists(process_folder):
            os.makedirs(process_folder)

        done_folder = os.path.join(self.path_to_folder, 'done')
        if not os.path.exists(done_folder):
            os.makedirs(done_folder)

        results_folder = os.path.join(self.path_to_folder, 'results')
        if not os.path.exists(results_folder):
            os.makedirs(results_folder)

        # Move all .xlsx files into the process folder
        for item in os.listdir(self.path_to_folder):
            if os.path.isfile(os.path.join(self.path_to_folder, item)):
                if '.xlsx' in item:
                    os.rename(os.path.join(self.path_to_folder, item), os.path.join(self.path_to_folder,
                                                                                    'process', item))

    def process_all_files_in_folder(self):
        process_folder = os.path.join(self.path_to_folder, 'process')
        done_folder = os.path.join(self.path_to_folder, 'done')
        results_folder = os.path.join(self.path_to_folder, 'results')
        all_files = os.listdir(process_folder)
        for process_file in all_files:
            if '.xlsx' in process_file:
                print("Found a file to process: {0}".format(process_file))
                file_path = os.path.join(process_folder, process_file)
                converter = Converter(file_path, format_excel=self.format_excel,
                                      default_labels=self.default_labels)
                converter.filter_doubles()
                converter.add_search_terms()
                converter.convert_to_full_properties()
                result_file_name = process_file.replace('.xlsx', ' - SABAM.xls')

                converter.export_to_excel(os.path.join(results_folder, result_file_name))
                os.rename(file_path, os.path.join(done_folder, process_file))
                print("Done with processing file: {0}".format(process_file))
