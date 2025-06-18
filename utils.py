import time

def formatar_tempo(segundos):
    if segundos >= 3600:
        return time.strftime('%H:%M:%S', time.gmtime(segundos))
    else:
        return time.strftime('%M:%S', time.gmtime(segundos))