class Dispatcher(object):
    Everything = 0xffff
    Unhandled  = 1 << 15

    def __init__(self):
        self.delegates = []

    def register(self, callback, mask = Everything):
        self.delegates.append([callback, mask])

    def dispatch(self, message, obj):
        expecting = [s[0] for s in self.delegates if (s[-1] & message)]
        [delegate(message, obj) for delegate in expecting]
