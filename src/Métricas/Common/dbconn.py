try:
    import pyodbc
except:
    import subprocess
    subprocess.run('conda install -y pyodbc freetds')
    import pyodbc
### IMPORTS ###
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
