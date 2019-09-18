from datetime import datetime

def format_timestamp(timestamp):
    print(timestamp)
    aux = datetime.fromtimestamp(timestamp//1000.0)
    print(timestamp)
    return aux.strftime("%b_%a_%H.%M.%S")