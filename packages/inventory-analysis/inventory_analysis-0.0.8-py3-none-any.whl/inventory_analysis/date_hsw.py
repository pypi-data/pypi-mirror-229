
week_s5_format = {
    "1900-01-01": "S1"
}

search_date = "1900-01-01"

def week_number_s5_format(date):
    date_string = str(date)
    if date_string in week_s5_format:
        return week_s5_format[date_string]
    else:
        return None  



