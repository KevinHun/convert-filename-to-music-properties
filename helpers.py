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
        return "{0}:{1}".format(self.minutes + extra_minutes, self.seconds + extra_second)