import os


class BlacklistAreaController:

    def __init__(self):
        blacklist_are_dir = os.path.join(
            os.path.dirname(__file__), 'blacklist_area')
        self.blacklist_area = []
        # get all filenames in blacklist_area directory
        for filename in os.listdir(blacklist_are_dir):
            filepath = os.path.join(blacklist_are_dir, filename)

    def is_in_blacklist_area(self, x, y):
        for area in self.blacklist_area:
            if area.is_in_area(x, y):
                return True
        return False
