from lxml import etree

class Duration(object):
    def __init__(self, duration):
        hours, minutes, seconds, miliseconds = duration.split(':', 3)
        self.hours = int(hours)
        self.minutes = int(minutes)
        self.seconds = int(seconds)
        self.miliseconds = int(miliseconds)

    def add_duration(self, duration):
        self.hours += duration.hours
        self.minutes += duration.minutes
        self.seconds += duration.seconds
        self.miliseconds += duration.miliseconds
        self.reformat_duration_properties()

    def reformat_duration_properties(self):
        if self.miliseconds >= 100:
            self.miliseconds -= 100
            self.seconds += 1
        if self.seconds >= 60:
            self.seconds -= 60
            self.minutes += 1
        if self.minutes >= 60:
            self.minutes -= 60
            self.hours += 1

    def __str__(self):
        return "{0}:{1}:{2}:{3}".format(self.hours, self.minutes, self.seconds, self.miliseconds)

    def get_in_minutes_seconds(self):
        extra_minutes = 0
        extra_second = 0
        if self.hours > 0:
            extra_minutes = self.hours * 60
        if self.miliseconds > 50:
            # round up
            extra_second = 1
        return "{0}:{1}".format(str(self.minutes + extra_minutes).zfill(2), str(self.seconds + extra_second).zfill(2))


def convert_to_xml(data, fields, file_path):
    print('test')
    root = etree.Element('CopyRightXml')
    for item in data:
        copyright_element = etree.Element('CopyRight')
        root.append(copyright_element)

        # Build all xml elements from the fields.
        field_dict = {}
        for field in fields:
            field_dict[field] = etree.Element(field)
            copyright_element.append(field_dict[field])

        for key, value in item.items():
            field_dict[key].text = filter_weird_chars(value)
    etree.ElementTree(root).write(file_path, encoding="UTF-8", xml_declaration=True)


def filter_weird_chars(string_to_replace):
    filtered_string = str(string_to_replace).replace('#', '').replace('<', '').replace('>', '').replace('/', '')
    return filtered_string
