
### IMPORTS ###
import pyodbc
import pandas as pd

  
#DB3 (replica)


#Host: 11.0.1.154
#Puerto: 4100
#User: datastage
#Pass: swiss08ds
#Base: Prestaci

#server="192.168.1.173"
#port="2638"
#user="usr_dw"
#passwd="dwsmg15"
#db="DW_SMG"
#driver="/opt/conda/lib/libtdsodbc.so"
     
    
    
### CONFIGS ###
server="11.0.1.154"
port="4100"
user="datastage"
passwd="swiss08ds"
db="Prestaci"
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
