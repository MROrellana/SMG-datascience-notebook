from dbconn import querydb, querydbtopandas 
import pandas as pd 
import datetime
import calendar
import os

path1 = "parametros_cirugias/cirugias_validas.xlsx"
path2 = "parametros_cirugias/centros_propios.xlsx"

cirugias_validas = pd.read_excel(path1,index_col=0,dtype=str).prestac_pres_prestacion.tolist()
cirugias_validas = str(cirugias_validas).strip("[").strip("]")

centros_propios = pd.read_excel(path2,index_col=0).id_pre_prestador.tolist()

mes = calendar.month_name[(datetime.datetime.today() - datetime.timedelta(days=105)).month]
acumulado = "acumulado"

for i,j in zip([105,255],[mes,acumulado]):
    

    menor = str(datetime.datetime.today() - datetime.timedelta(days=i))[:10]

    mayor = str(datetime.datetime.today() - datetime.timedelta(days=74))[:10]

    
    df = querydbtopandas(f"""select 
                a11.id_pre_prestador  id_pre_prestador,
                max(a15.desc_pre_nombre)  desc_pre_nombre,
                max(a15.vigente)  vigente,
                a12.id_pre_prestador  id_pre_prestador0,
                max(a16.desc_pre_nombre)  desc_pre_nombre0,
                sum(a11.i_ft_importe_prestacion)  RDENES,
                sum(case  when (  i_ft_importe_prestacion *i_Ft_Cantidad <= 0) then 0  when  (i_ft_importe_prestacion *i_Ft_Cantidad <> 0 ) then   i_Ft_Cantidad   end )  CANTIDADORDENES0
from      DBA.ft_ordenes               a11
                join        DBA.d_auto_autorizacion     a12
                  on        (((a11.id_auto_sucursal * 10000000) + a11.i_ft_autorizacion) = ((a12.id_auto_sucursal * 10000000) + a12.id_auto_autorizacion))
                join        DBA.d_exp_expediente a13
                  on        (((a11.id_ofi_oficina * 10000000) + a11.id_exp_expediente) = ((a13.ofi * 10000000) + a13.id_exp_expediente))
                join        DBA.d_pre_prestador   a15
                  on        (a11.id_pre_prestador = a15.id_pre_prestador)
                join        DBA.d_pre_prestador_autoriza a16
                  on        (a12.id_pre_prestador = a16.id_pre_prestador)
                join        DBA.d_pres_prestacion a17
                  on        (a11.id_pres_prestacion = a17.id_pres_prestacion)
where (CONVERT(DATETIME,a13.exp_mes, "mm-YYYY") >= date("{menor}") and CONVERT(DATETIME,a13.exp_mes, "mm-YYYY") < date("{mayor}")
and a15.id_pre_tipo in ('E','P')
and a11.id_nom_nomenclador in (1,11)
and (not a11.id_pre_prestador in (154688))
and (a12.id_pre_prestador <> 0)
and RTRIM(a17.prestac_pres_prestacion) in ({cirugias_validas}))
group by             a11.id_pres_prestacion,
                a11.id_nom_nomenclador,
                a11.id_pre_prestador,
                a12.id_pre_prestador""")
    
    df_propios = df[df["id_pre_prestador0"].isin(centros_propios)]

    df_no_propios = df[~df["id_pre_prestador0"].isin(centros_propios)]

    propios = df_propios.groupby(["id_pre_prestador", "desc_pre_nombre"])["CANTIDADORDENES0"].sum().reset_index().rename(columns = {"CANTIDADORDENES0": "propios"})

    no_propios = df_no_propios.groupby(["id_pre_prestador", "desc_pre_nombre"])["CANTIDADORDENES0"].sum().reset_index().rename(columns = {"CANTIDADORDENES0": "no_propios"})

    final = pd.merge(propios, no_propios,how="outer")

    final.fillna(0,inplace=True)

    final["total"]  = final["propios"] + final["no_propios"]

    final["porcentaje en propios"] = (final["propios"] /final["total"])

    final = final.round(2)

    final.rename(columns= {"id_pre_prestador": "Prestador", "desc_pre_nombre": "Razón Social", "propios": "Propias", "no_propios": "No propias", "total": "Total general","porcentaje en propios":"% en Propias" },inplace=True)
   
    
    directory = "metrica_cirugias"
    file = f"Métrica Cirugías {j}.xlsx"
    final.to_excel(os.path.join(directory,file))