from circuits import Component


class EventConsumer(Component):

    def produced(self, *args):
        print("EventConsumer produced called")
