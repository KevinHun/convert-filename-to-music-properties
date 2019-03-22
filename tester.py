from converter import Converter

default_labels = {'Kind': 'NVT', 'PerformanceCode': 'Background muziek'}

#converter = Converter('/home/khunyadi/Downloads/TVS_AFL01.xlsx', format='xls', default_labels=default_labels)
converter = Converter('files/EDL-AFL-05-deel-2.xlsx', default_labels=default_labels)
#converter = Converter('/home/khunyadi/Documents/afl_test.xlsx', debug=True,  default_labels=default_labels)
converter.filter_doubles()
converter.add_search_terms()
converter.convert_to_full_properties()
converter.export_to_excel('files/SABAM-EDL-AFL-05-deel-2.xls')
converter.export_to_xml('files/SABAM-EDL-AFL-05-deel-2.xml')
