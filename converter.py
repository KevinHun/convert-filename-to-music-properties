import re
import csv
import time
from difflib import get_close_matches
from excel import FilenameExcel, ExcelWriter
from helpers import Duration, convert_to_xml
from discogs import Discogs


class Converter(object):
    def __init__(self, path_to_excel, debug=False, format='xls', default_labels=None):
        self.excel = FilenameExcel(path_to_excel)
        self.file_list = self.excel.get_rows()
        self.discogs_client = Discogs()
        self.filtered_list = []
        self.full_properties_list = []
        self.debug = debug
        self.sleep_seconds = 3
        self.format = format
        self.default_labels = default_labels

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
            # Remove everything after the third last point (extension...)
            filename_splitted = filename.split('.')
            search_term = '.'.join(filename_splitted[:-3])

            #search_term = filename.split('.', 1)[0]
            # Convert underscores to spaces
            search_term = search_term.replace("_", " ")
            search_term = search_term.replace("-", " ")
            search_term = search_term.replace("'", "")
            # remove trailing numbers or spaces.
            search_term = re.sub(r'^[ \d\.]*', '', search_term)
            file.append(search_term)

    def find_track_in_tracklist(self, file, tracks):
        best_matches = get_close_matches(file[2], tracks)
        if not best_matches:
            # Try again with less match terms.
            filename_without_extension = file[0].split('.', 1)[0]
            if '_' in filename_without_extension:
                # Split into pieces
                new_search_terms = filename_without_extension.split('_')
                for search_term in new_search_terms:
                    best_matches = get_close_matches(search_term, tracks)
                    if best_matches:
                        break
            elif '-' in filename_without_extension:
                # split into pieces
                new_search_terms = filename_without_extension.split('-')
                for search_term in new_search_terms:
                    best_matches = get_close_matches(search_term, tracks)
                    if best_matches:
                        break
            else:
                # last resort, just split into pieces with spaces
                new_search_terms = file[2].split(' ')
                for search_term in new_search_terms:
                    best_matches = get_close_matches(search_term, tracks)
                    if best_matches:
                        break

        if best_matches:
            track_title = best_matches[0]
            return track_title
        return False

    @staticmethod
    def build_tracklist(tracklist):
        expanded_tracklist = []
        for track in tracklist:
            if 'sub_tracks' in track.data.keys():
                # We're dealing with subtracks. Unpack them.
                for sub_track in track.data['sub_tracks']:
                    expanded_tracklist.append(sub_track)
            else:
                expanded_tracklist.append(track.data)
        return expanded_tracklist

    def find_properties_with_item(self, file):
        results = self.discogs_client.search_release(file[2])
        print(file[2])

        retries = 0
        while True:
            try:
                # Get the first result, we feel always lucky
                if not results:
                    # Try with the search term without parentheses content.
                    results = self.discogs_client.search_release(re.sub(r'\(.*\)', '', file[2]))

                    if not results:
                        # Nothing found for this search term, return an empty properties dict with only the filename
                        print("Didn't find any results from discogs")
                        properties = {}
                        properties['Title'] = file[0]
                        properties['Performer'] = ''
                        properties['Composer'] = ''
                        properties['Duration'] = ''
                        properties['Label'] = ''
                        return properties

                release = results[0]
                break
            except:
                # sleep 3 seconds and try again
                time.sleep(self.sleep_seconds)
                print("I have tried {0} times for {1} seconds".format(retries, self.sleep_seconds))
                if retries > 5:
                    raise RuntimeError("Cannot get search results after 6 retries!")

        retries = 0
        while True:
            try:
                release_tracklist = release.tracklist
                break
            except:
                # sleep 3 seconds and try again
                time.sleep(self.sleep_seconds)
                print("I have tried {0} times for {1} seconds".format(retries, self.sleep_seconds))
                if retries > 5:
                    raise RuntimeError("Cannot get tracklist after 6 retries!")
                print("Failed fetching the tracklist. Retry")

        tracklist = self.build_tracklist(release_tracklist)
        tracks = [track['title'] for track in tracklist]
        if self.debug:
            print("release data and tracks data")
            print(release.data)
            print(tracks)
        track_name = self.find_track_in_tracklist(file, tracks)

        if not track_name:
            # If there's still no track found. It might be because the tracklist contains text between () which we don't like!
            # get this text out and repeat.
            tracks = [re.sub(r'\(.*\)', '', track['title']) for track in tracklist]
            track_name = self.find_track_in_tracklist(file, tracks)
            if not track_name:
                # Nothing found for this search term, return an empty properties dict with only the filename
                print("Didn't find the correct track!")
                properties = {}
                properties['Title'] = file[0]
                properties['Performer'] = ''
                properties['Composer'] = ''
                properties['Duration'] = ''
                properties['Label'] = ''
                return properties
            else:
                for track in tracklist:
                    track_title = re.sub(r'\(.*\)', '', track['title'])
                    if track_title == track_name:
                        break
        else:
            for track in tracklist:
                if track['title'] == track_name:
                    break

        properties = {}
        properties['Title'] = track['title']
        properties['Performer'] = ",".join(set([artist.name for artist in release.artists]))
        # Get all the writers
        writers = []
        if 'extraartists' in track.keys():
            for extra_artist in track['extraartists']:
                if extra_artist['role'] == 'Written-By' or extra_artist['role'] == 'Written-By, Composed By':
                    writers.append(extra_artist['name'])
            # if no writers found on the track. Let's get the writers of the release
        if not writers:
            if 'extraartists' in release.data.keys():
                for extra_artist in release.data['extraartists']:
                    if extra_artist['role'] == 'Written-By' or extra_artist['role'] == 'Written-By, Composed By':
                        writers.append(extra_artist['name'])

        properties['Composer'] = ",".join(set(writers))
        properties['Duration'] = file[1].get_in_minutes_seconds()
        properties['Label'] = ",".join(set([label.name for label in release.labels]))
        properties['Year'] = release.year
        # populate default labels
        for key, label in self.default_labels.items():
            properties[key] = label
        print(properties)

        return properties

    def convert_to_full_properties(self):
        counter = 1
        for file in self.filtered_list:
            print(file[0])
            properties = self.find_properties_with_item(file)
            if properties:
                # Add volgnummer
                properties['Volgnummer'] = counter
                self.full_properties_list.append(properties)
                counter += 1

            # Sleep 1 second because the discogs api doesn't like us
            time.sleep(1)

    def export_to_csv(self, file_path, csv_columns=None):
        if not csv_columns:
            csv_columns = ['Volgnummer', 'Sequence', 'Title', 'Kind', 'PerformanceCode', 'Composer', 'Performer',
                             'Duration','Holder', 'Function', 'Year', 'ISRC', 'Label', 'Album', 'CatNr', 'Track']

        try:
            with open(file_path, 'w') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
                writer.writeheader()
                for data in self.full_properties_list:
                    writer.writerow(data)
        except IOError:
            print("I/O error")

    def export_to_excel(self, file_path, excel_columns=None):
        if not excel_columns:
            excel_columns = ['Volgnummer', 'Sequence', 'Title', 'Kind', 'PerformanceCode', 'Composer', 'Performer',
                             'Duration','Holder', 'Function', 'Year', 'ISRC', 'Label', 'Album', 'CatNr', 'Track']
        excel_writer = ExcelWriter(file_path)
        if self.format == 'xls':
            excel_writer.create_excel_xls(self.full_properties_list, excel_columns)
        else:
            excel_writer.create_excel_xlsx(self.full_properties_list, excel_columns)

    def export_to_xml(self, file_path, xml_elements=None):
        if not xml_elements:
            xml_elements = ['Volgnummer', 'Sequence', 'Title', 'Kind', 'PerformanceCode', 'Composer', 'Performer',
                             'Duration','Holder', 'Function', 'Year', 'ISRC', 'Label', 'Album', 'CatNr', 'Track']

        convert_to_xml(self.full_properties_list, xml_elements, file_path)
