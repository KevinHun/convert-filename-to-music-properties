from converter import Converter

converter = Converter('/home/khunyadi/Downloads/EDL-AFL-06.xlsx')
converter.filter_doubles()
converter.add_search_terms()
converter.convert_to_full_properties()
converter.export_to_csv('/home/khunyadi/Downloads/SABAM-AFL-06.csv')
