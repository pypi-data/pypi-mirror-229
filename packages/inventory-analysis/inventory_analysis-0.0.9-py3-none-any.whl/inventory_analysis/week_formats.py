
format_s5 ={
    "1900-01-01": "S1"
}

def week_number(format,date):
    date_string = str(date)
    key=format.get(date_string)
    return(key)










