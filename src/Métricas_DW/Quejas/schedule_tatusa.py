import schedule
import time
import os

def job():
    os.system("python quejas.py")
    
schedule.every(120).seconds.do(job)

while 1:
    schedule.run_pending()
    time.sleep(1)