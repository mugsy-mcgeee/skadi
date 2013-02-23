class RecordsMessages(object):
    def __init__(self):
        self.captures = {}

    def __call__(self, message, obj):
        if not message in self.captures:
            self.captures[message] = []
        self.captures[message].append(obj)

    def recorded_messages(self):
        return self.captures.keys()
