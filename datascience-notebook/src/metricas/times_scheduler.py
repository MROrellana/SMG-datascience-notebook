import schedule
import time
import os
import datetime

def primerodemes():
    if datetime.date.today().day ==1:
        os.system("python quejas_schedule.py")
        os.system("python calificaciones_schedule.py")
        os.system("python imagenes_schedule.py")
        os.system("python presupuesto_schedule.py")
        os.system("python desconocimiento_schedule.py")
    else:
        print("not first")


def quincedemes():
    if datetime.date.today().day ==15:
        os.system("python consultas_schedule.py")
        os.system("python farmacia_schedule.py")
        os.system("python cirugias_schedule.py")
    else:
        print("not fifteen")

schedule.every().day.at("02:00").do(primerodemes)
schedule.every().day.at("02:00").do(quincedemes)

while 1:
    schedule.run_pending()
    time.sleep(1)