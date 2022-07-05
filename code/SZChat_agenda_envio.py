from glob import glob
import sched
import threading
import schedule
import time

from typepy import Bool

#EXEMPLOS DE AGENDAMENTO
#schedule.every(10).minutes.do(job)
#schedule.every().hour.do(job)
#schedule.every().day.at("10:30").do(job)
#schedule.every().monday.do(job)
#schedule.every().wednesday.at("13:15").do(job)
#schedule.every().minute.at(":17").do(job)

def sendWhatsAppCobranca():
    print(" -> WHATS: Estou rodando na thread %s" % threading.current_thread() )
    time.sleep(120)
    
def job():
    print(" -> Estou rodando na thread %s" % threading.current_thread() )

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

schedule.every(10).seconds.do(sendWhatsAppCobranca)
schedule.every(10).seconds.do(run_threaded, job)
schedule.every(10).seconds.do(run_threaded, job)

#while 1:
#    schedule.run_pending()
#    time.sleep(1)

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("Keyboard Interrupt.")
        exit
    except Exception as e:
        print(str(e))
        exit
