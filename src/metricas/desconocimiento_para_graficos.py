from dbconn import querydb, querydbtopandas 
import pandas as pd 
import datetime
import calendar
import os

path = "parametros_desconocimiento/centros_propios_swiss.xlsx"

clinicas_propias_id = pd.read_excel(path,index_col=0).id_pre_prestador.to_list()

menor = str(datetime.datetime.today() - datetime.timedelta(days=20))[:7]
mayor = str(datetime.datetime.today())[:7] 
menor_año = str(datetime.datetime.today() - datetime.timedelta(days=385))[:7]

if menor[-2:] == "01":
    eliminar =  str(int(menor[:4]) -1) + "-12"
elif menor[-2:] in ["02","03","04","05","06","07","08","09","10"]:
    eliminar = str(int(menor[:4])-1) + "-0" + str(int(menor[-2:])-1)
else:
    eliminar = str(int(menor[:4])-1) + "-" + str(int(menor[-2:])-1)

os.remove(f"datos_desconocimiento/{eliminar}.gzip")

for i,j in zip([menor, menor_año], [menor, "acumulado"]): 
    df = querydbtopandas(f"""select    a11.id_encuesta  id_encuesta,    
                a11.id_afiliado  id_afi_afiliado,
                a11.id_prestador  id_pre_prestador,                   
                max(a13.desc_pre_nombre)  desc_pre_nombre,
                max(a13.vigente)  vigente,
                a11.id_transac_tipo  id_transac_tipo,            
                a11.id_prest_prestacion  id_pres_prestacion,
                max(a18.desc_pres_prestacion)  desc_pres_prestacion,
                max(a18.prestac_pres_prestacion)  prestac_pres_prestacion,
                sum(distinct a11.i_CNT_desc)  QDESCONOCIDAS
from      DBA.ft_prest_encuestas              a11
                join        DBA.d_pre_prestador   a13
                  on        (a11.id_prestador = a13.id_pre_prestador)
                join        DBA.d_pres_prestacion a18
                  on        (a11.id_prest_prestacion = a18.id_pres_prestacion)
where (cast(a11.fec_encuesta as date) >= date("{i}") and cast(a11.fec_encuesta as date) < date("{mayor}")
and a11.id_moti_desconoc <> 1
and a11.id_prestador <> 0)
group by             a11.id_encuesta,
                a11.id_afiliado,
                a11.id_prestador,         
                a13.id_pre_especialidad,
                a11.id_transac_tipo,
                a11.id_prest_prestacion,
                DATE(a11.fec_consumo),
                a11.id_tie_mes_c""")
    
    
    cma = df[df["id_pre_prestador"].isin(clinicas_propias_id)][["id_pre_prestador", "desc_pre_nombre"]].rename(columns={"desc_pre_nombre": "cma"})
    df = pd.merge(df, cma, how="outer").fillna("No aplica")
    encuestas_desconocidas = df.groupby(["id_pre_prestador","desc_pre_nombre","cma"])["id_encuesta"].nunique()
    afiliados_desconocidos = df.groupby(["id_pre_prestador","desc_pre_nombre", "cma"])["id_afi_afiliado"].nunique()
    df = pd.concat([encuestas_desconocidas, afiliados_desconocidos],axis=1).reset_index()
    df.rename(columns = {"id_pre_prestador":"Prestador",
                     "desc_pre_nombre":"Razón Social",
                     "id_encuesta":"Q desconocidas",
                     "id_afi_afiliado":"Q afiliados"},inplace=True)
    final = df[['Prestador', 'Razón Social', 'cma', 'Q afiliados', 'Q desconocidas']]
    
    final.to_parquet(f'datos_desconocimiento/{j}.gzip',compression='gzip') 