import datetime

def salvar_log(pontuacao):
    agora = datetime.datetime.now()
    data_str = agora.strftime("%Y-%m-%d")
    hora_str = agora.strftime("%H:%M:%S")
    
    try:
        with open("log.dat", "a", encoding="utf-8") as f:
            f.write(f"Pontuação: {pontuacao}, Data: {data_str}, Hora: {hora_str}\n")
    except Exception as e:
        print(f"Erro ao salvar o log: {e}")