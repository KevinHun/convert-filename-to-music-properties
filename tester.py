from converter import Converter

converter = Converter('C:\\Users\\kevin\\Downloads\\TVS_AFL01.xlsx')
converter.filter_doubles()
converter.add_search_terms()
converter.convert_to_full_properties()
converter.export_to_csv('C:\\Users\\kevin\\Downloads\\SABAM AFL1.csv')