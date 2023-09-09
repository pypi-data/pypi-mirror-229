
class s5_format:

    week_s5_format = {
        "1900-01-01": "S1"
    }


    def week_number_s5_format(date):
        date_string = str(date)
        if date_string in week_s5_format:
            return week_s5_format[date_string]
        else:
            return None  



