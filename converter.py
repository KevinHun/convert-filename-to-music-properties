import re
import csv
import time
import discogs_client
from difflib import get_close_matches
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
        self.full_properties_list = []
        for file in self.filtered_list:
            results = self.discogs_client.search_release(file[2])
            print(file[2])
            print(results.pages)

            # Get the first result, we feel always lucky
            if not results:
                # Nothing found for this search term, continueing
                continue
            release = results[0]
            tracks = [track.title for track in release.tracklist]
            best_matches = get_close_matches(file[2], tracks)
            if not best_matches:
                # Try again with less match terms.
                new_search_terms = file[2].split(' ')
                for search_term in new_search_terms:
                    best_matches = get_close_matches(search_term, tracks)
                    if best_matches:
                        break

            if best_matches:
                track_title = best_matches[0]
                for track in release.tracklist:
                    if track.title == track_title:
                        break

                properties = {}
                properties['Titel'] = track.title
                properties['Uitvoerder'] = ",".join([artist.name for artist in release.artists])
                properties['Componist'] = ",".join([artist.name for artist in track.credits])
                if not properties['Componist']:
                    properties['Componist'] = ",".join([artist.name for artist in release.credits])
                properties['Duurtijd'] = file[1].get_in_minutes_seconds()
                properties['Label'] = ",".join([label.name for label in release.labels])
                print(properties)
                self.full_properties_list.append(properties)
            else:
                print("Didn't find a single match in the track list, I'm sorry")
            # Sleep 1 second because the discogs api doesn't like us
            time.sleep(1)

    def export_to_csv(self, file_path, csv_columns=None):
        if not csv_columns:
            csv_columns = ['Volgnummer', 'Tijdscode', 'Titel', 'Aard', 'Performance', 'Componist', 'Uitvoerder', 'Duurtijd', 'Rechthebbende', 'Hoedanigheid', 'Jaar', 'ISRC', 'Label', 'Album', 'Cat Nr', 'Track']

        try:
            with open(file_path, 'w') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
                writer.writeheader()
                for data in self.full_properties_list:
                    writer.writerow(data)
        except IOError:
            print("I/O error")
