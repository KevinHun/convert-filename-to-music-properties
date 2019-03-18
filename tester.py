from converter import Converter

converter = Converter('C:\\Users\\kevin\\Downloads\\TVS_AFL01.xlsx')
converter.filter_doubles()
converter.add_search_terms()
converter.convert_to_full_properties()