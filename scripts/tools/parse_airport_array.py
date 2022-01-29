def parse_airport_array(airport_array: str):
    return airport_array.replace("{", "").replace("}", "").split(",")
