from dbconn import querydb, querydbtopandas 
import pandas as pd
import numpy as np
import datetime
import calendar
import os

#quince de mayo ELEIMINAR DSPS y DESCOMENTAR EL OS.REMOVE!!!!

quince_de_mayo = datetime.datetime.strptime("2020-05-15", "%Y-%m-%d")
###################################

menor = str(quince_de_mayo  - datetime.timedelta(days=90))[:7]
mayor = str(quince_de_mayo - datetime.timedelta(days=70))[:7]
menor_año = str(quince_de_mayo - datetime.timedelta(days=455))[:7]

if menor[-2:] == "01":
    eliminar =  str(int(menor[:4]) -1) + "-12"
elif menor[-2:] in ["02","03","04","05","06","07","08","09","10"]:
    eliminar = str(int(menor[:4])-1) + "-0" + str(int(menor[-2:])-1)
else:
    eliminar = str(int(menor[:4])-1) + "-" + str(int(menor[-2:])-1)

    #DESCOMENTARRR
#os.remove(f"datos_farmacia/{eliminar}.gzip")


for i,j in zip([menor, menor_año], [menor, "acumulado"]): 
    df = querydbtopandas(f"""select id_prestador_efector, 
        a14.id_afiliado,
        desc_pre_nombre, 
        d.exp_mes,
        sum(i_ft_cantidad) cantidad,
        sum(i_ft_importe) importe,
        id_medicamento,
        Q.deno
    from dba.ft_costo_medico A
        left JOIN dba.d_pre_prestador B
            ON a.id_prestador_efector = b.id_pre_prestador
        LEFT JOIN dba.fecha_mes D
            ON a.id_tie_fecha_liquidacion = d.id_Tie_mes
        left join DBA.afi_afiliados a14
             on a.id_afiliado = a14.id_afiliado
        left JOIN dba.prestad_costo_centros E
            ON A.id_prestador_efector = E.prestad and E.baja_fecha is null and e.prepaga = ( select min(PCC1.prepaga) from dba.prestad_costo_centros PCC1 where PCC1.prestad =  e.prestad )   
        LEFT JOIN dba.costo_centros Q
            ON E.centro = Q.centro
    where CONVERT(DATETIME,d.exp_mes, "mm-YYYY") >= date("{i}") and CONVERT(DATETIME,d.exp_mes, "mm-YYYY") < date("{mayor}")
    and id_prestador_efector not in (0)
    and tbl_origen = 'receta_medicamento'
    group by id_prestador_efector, desc_pre_nombre, a14.id_afiliado,Q.deno,
    d.exp_mes,
        id_medicamento,
    i_ft_cantidad, i_ft_importe""")


    #calculo metrica
    importe = df.groupby(["id_prestador_efector","desc_pre_nombre", "deno" ])["importe"].sum()

    cantidad_ordenes = df.groupby(["id_prestador_efector","desc_pre_nombre", "deno" ])["cantidad"].sum()

    cantidad_afiliados = df.groupby(["id_prestador_efector","desc_pre_nombre", "deno" ])["id_afiliado"].nunique()

    df = pd.concat([importe,cantidad_ordenes,cantidad_afiliados],axis=1).reset_index()

    df["promedio por afiliado"] = df["importe"] / df["id_afiliado"]
    df["promedio por receta"] = df["importe"] / df["cantidad"]

    suma_especialidad = df.groupby("deno")["promedio por afiliado"].sum()
    
    desv_stan_especialidad = df.groupby("deno")['promedio por afiliado'].std().rename("desvios por especialidad").reset_index()
    
    num_prestador_esp = df.groupby("deno")["desc_pre_nombre"].nunique()

    media_especialidad = (suma_especialidad/num_prestador_esp).reset_index().rename(columns= {0: "media por especialidad"})

    df = df.merge(media_especialidad).merge(desv_stan_especialidad)

    df["Diferencia respecto de la media"] = ((df["promedio por afiliado"] / df["media por especialidad"]) -1 )*100
    
    df["desvios de la media de su sp"] = (df["promedio por afiliado"] - df["media por especialidad"]) /  df["desvios por especialidad"]

    
    df = df.round(2)

    df = df[['id_prestador_efector', 'desc_pre_nombre', 'deno',  'media por especialidad',  'Diferencia respecto de la media',
            'id_afiliado', 'cantidad', 'promedio por afiliado',
           'promedio por receta', 'importe' , "desvios de la media de su sp"]]

    df.columns = ["N° Prestador", "Médico", "Especialidad", "Media por especialidad", "Diferencia respecto de la media", "Afil. Usuarios", "Recetas", "Promedio por afiliado", "Promedio por receta", "A cargo de SMMP", "desvios de la media de su sp"]


    df.to_parquet(f'datos_farmacia/{j}.gzip',compression='gzip') 


