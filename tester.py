from processor import Processor

default_labels = {'Aard': 'NVT', 'Performance': 'Background muziek'}
proc = Processor(default_labels=default_labels)
proc.process_all_files_in_folder()
