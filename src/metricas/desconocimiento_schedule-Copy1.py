from dbconn import querydb, querydbtopandas 
import pandas as pd 
import datetime
import calendar
import os

path = "parametros_desconocimiento/centros_propios_swiss.xlsx"

clinicas_propias_id = pd.read_excel(path,index_col=0).id_pre_prestador.to_list()


mes = calendar.month_name[(datetime.datetime.today().month)-1]
acumulado = "acumulado"


for i,j in zip([30,182],[mes,acumulado]):
    #determina fecha hoy
    mayor = str(datetime.datetime.today())[:10]
    #determina fecha un mes o 6 meses atras
    menor = str(datetime.datetime.today() - datetime.timedelta(days=i))[:10]
    
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
where (cast(a11.fec_encuesta as date) >= date("{menor}") and cast(a11.fec_encuesta as date) < date("{mayor}")
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
    
    directory = "metrica_desconocimiento"
    file = f"Métrica Desconocimiento {j}.xlsx"
    final.to_excel(os.path.join(directory,file))