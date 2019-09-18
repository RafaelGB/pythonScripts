from datetime import datetime

def format_timestamp(timestamp):
    aux = datetime.fromtimestamp(timestamp//1000.0)
    return aux.strftime("%b_%a_%H.%M.%S")