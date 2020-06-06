try:
    import pyodbc
except:
    import subprocess
    subprocess.run('conda install -y pyodbc freetds', shell = True)
    import pyodbc

#libraries
for i in ["schedule", "dash", "pyarrow", "unidecode", "dash_bootstrap_components", "plotly", "plotly_express"]:
    import subprocess
    subprocess.run(f'pip install {i}', shell = True)



#import pyodbc
import pandas as pd

### CONFIGS ###
server="192.168.1.173"
port="2638"
user="usr_dw"
passwd="dwsmg15"
db="DW_SMG"
driver="/opt/conda/lib/libtdsodbc.so"

### QUERYDB ###
def querydb(query):
    try:
        conn = pyodbc.connect(driver=driver,server=server,port=port,uid=user,pwd=passwd,database=db)
        cursor = conn.cursor()
        result = cursor.execute(query)
        rows = result.fetchall()
        columns = cursor.description
    except Exception as err:
        print("El error del SQL es: %s" % str(err))
    finally:
        conn.close()
    return (columns,rows)

### QUERY TO PANDAS ###
def querydbtopandas(query):
    try:
        conn = pyodbc.connect(driver=driver,server=server,port=port,uid=user,pwd=passwd,database=db)
        df = pd.read_sql(query,conn)
    except Exception as err:
        print("El error del SQL es: %s" % str(err))
    finally:
        conn.close()
    return df


import os
os.system("python /home/jovyan/Swiss-Metricas/metricas/main.py")
os.system("python /home/jovyan/Swiss-Metricas/metricas/times_scheduler.py")
