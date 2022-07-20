from datetime import datetime
from yaml import parse
from datetimerange import DateTimeRange
from dateutil.parser import *

def getIsTimeSend():
    if datetime.now().weekday() == 7: #domingo não faz nada
        return False
    else:
        manha_inicio = parse("08:00:00") # substituir pelo horário que vem do banco de dados
        manha_fim = parse("12:00:00")
        tarde_inicio = parse("13:30:00")
        tarde_fim = parse("18:00:00")

        if datetime.now().weekday() == 6: #sábado trabaha-se somente de manhã
            timeRangeManha = DateTimeRange(manha_inicio, manha_fim)
            horaAtual = parse(str(datetime.now()))
            return (horaAtual in timeRangeManha)
        else:
            #falta validar se é feriado!
            timeRangeManha = DateTimeRange(manha_inicio, manha_fim)
            timeRangeTarde = DateTimeRange(tarde_inicio, tarde_fim)
            horaAtual = parse(str(datetime.now()))

            vResult = ((horaAtual in timeRangeManha) or (horaAtual in timeRangeTarde))
            return vResult

if __name__ == '__main__':
    agora = getIsTimeSend()
    print(agora)
