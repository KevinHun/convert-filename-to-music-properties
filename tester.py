from converter import Converter

converter = Converter('/home/khunyadi/Downloads/TVS_AFL01.xlsx')
#converter = Converter('/home/khunyadi/Downloads/EDL-AFL-07.xlsx')
#converter = Converter('/home/khunyadi/Documents/afl_test.xlsx', debug=True)
converter.filter_doubles()
converter.add_search_terms()
converter.convert_to_full_properties()
#converter.export_to_csv('/home/khunyadi/Downloads/SABAM-AFL-07.csv')
converter.export_to_excel('/home/khunyadi/Downloads/SABAM-AFL-01.xlsx')
