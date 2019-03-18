import re
import discogs_client
from excel import FilenameExcel
from helpers import Duration
from discogs import Discogs


class Converter(object):
    def __init__(self, path_to_excel):
        self.excel = FilenameExcel(path_to_excel)
        self.file_list = self.excel.get_rows()
        self.discogs_client = Discogs()
        self.filtered_list = []

    def filter_doubles(self):
        last_file = None
        for file in self.file_list:
            filename = file[0]
            if filename[:-2] == last_file:
                # This one needs to be filtered out and the duration added to the previous one.
                self.filtered_list[-1][1].add_duration(Duration(file[1]))
            else:
                self.filtered_list.append([file[0], Duration(file[1])])
            last_file = filename[:-2]

    def add_search_terms(self):
        if not self.filtered_list:
            raise ValueError("filtered_list is still empty. Did you initialize it yet?")

        for file in self.filtered_list:
            filename = file[0]
            # Remove everything after first point (extension...)
            search_term = filename.split('.', 1)[0]
            # Convert underscores to spaces
            search_term = search_term.replace("_", " ")

            # remove trailing numbers or spaces.
            search_term = re.sub(r'^[ \d\.]*', '', search_term)
            file.append(search_term)

    def convert_to_full_properties(self):
        full_properties_list = []
        for file in self.filtered_list:
            results = self.discogs_client.search_release(file[2])
            print(file[2])
            print(results.pages)

            # Get the first result, we feel always lucky
            if not results:
                # Nothing found for this search term, continueing
                continue
            result = results[0]
            properties = {}
            properties['Titel'] = result.title
            properties['Uitvoerder'] = ",".join([artist.name for artist in result.artists])
            properties['Componist'] = ",".join([artist.name for artist in result.credits])
            properties['Duurtijd'] = file[1].get_in_minutes_seconds()
            properties['Label'] = ",".join([label.name for label in result.labels])
            print(properties)
            full_properties_list.append(properties)
