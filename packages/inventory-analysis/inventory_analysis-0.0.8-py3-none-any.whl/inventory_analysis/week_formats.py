
class s5_format:
    def __init__(self):
        self.s5_format_dict = {
            "1900-01-01": "S1"
        }

    def get_week_number_s5(self, key):
        return self.s5_format_dict.get(key)



