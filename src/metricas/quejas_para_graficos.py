from dbconn import querydb, querydbtopandas 
import pandas as pd 
import datetime
import calendar
import os

gerencia = "18, 19"

menor = str(datetime.datetime.today() - datetime.timedelta(days=20))[:7]
mayor = str(datetime.datetime.today())[:7] 
menor_año = str(datetime.datetime.today() - datetime.timedelta(days=385))[:7]

if menor[-2:] == "01":
    eliminar =  str(int(menor[:4]) -1) + "-12"
elif menor[-2:] in ["02","03","04","05","06","07","08","09","10"]:
    eliminar = str(int(menor[:4])-1) + "-0" + str(int(menor[-2:])-1)
else:
    eliminar = str(int(menor[:4])-1) + "-" + str(int(menor[-2:])-1)

os.remove(f"datos_quejas/{eliminar}.gzip")
    
for i,j in zip([menor, menor_año], [menor, "acumulado"]): 
    df = querydbtopandas(f"""select a11.workflow_id  workflow_id,
       max(a113.detalle)  detalle3,
      a12.prestad  id_pre_prestador,
      a18.GERENCIA,
      a11.registro_fecha_max,
       max(a13.desc_pre_nombre)  desc_pre_nombre,
       sum(1.0)  CANTIDADETAPASMINNDISTINCT
       from   DBA.CRM_ETAPAS_MIN_MAX a11
       join   DBA.crm_quejas_categ_resol a12
         on   (a11.etapa_id_max = a12.ETAPA_ID)
      join   DBA.d_pre_prestador    a13
         on   (a12.prestad = a13.id_pre_prestador)         
       join   DBA.crm_atributo_quejas    a113
         on   (a12.atributo_id = a113.atributo_id)  
       join   DBA.ft_pad_padron_iq   a14
         on   (a11.ID_AFI_AFILIADO = a14.id_afiliados and
       a11.id_tie_mes_max = a14.MES)  
       join   DBA.CRM_SUBMOTIVOS a18
         on   (a12.SUBMOTIVO_ID = a18.SUBMOTIVO_ID and
       a12.motivo_llamado_id = a18.motivo_id)
    where  (a11.registro_fecha_max >= date("{i}") and a11.registro_fecha_max < date("{mayor}")
    and a11.motivo_id = 8
    and a12.estado in (14)
    and a18.GERENCIA in ({gerencia})
    and a12.prestad <> 0)
    group by   a11.workflow_id,
        a11.registro_fecha_max,
       a18.GERENCIA,
       a12.finalizado,
       prestad,
       a12.ALTA_FECHA
       """)

    df_metrica = df[["workflow_id", "detalle3", "id_pre_prestador","desc_pre_nombre" ]]

    final = df_metrica.groupby([ "id_pre_prestador","desc_pre_nombre", "detalle3" ])["workflow_id"].nunique().reset_index()

    total_prestador = final.groupby([ "id_pre_prestador","desc_pre_nombre"])["workflow_id"].sum().rename("total_prestador")

    final = final.merge(total_prestador, left_on = "id_pre_prestador" , right_on="id_pre_prestador" )

    final = final.rename(columns= {"id_pre_prestador": "Prestador", "desc_pre_nombre": "Razón social", "detalle3": "Clasificación de casos", "workflow_id": "Q de quejas", "total_prestador": "Total de quejas prestador"})

    final.to_parquet(f'datos_quejas/{j}.gzip',compression='gzip')
