from dbconn_base2 import querydb, querydbtopandas 
import pandas as pd 
import datetime
import calendar
import os

mes = calendar.month_name[(datetime.datetime.today().month)-1]
acumulado = "acumulado"

for i,j in zip([30,182],[mes,acumulado]):
    #determina fecha hoy
    mayor = str(datetime.datetime.today())[:10]
    #determina fecha un mes o 6 meses atras
    menor = str(datetime.datetime.today() - datetime.timedelta(days=i))[:10]
    
    df = querydbtopandas(f"""SELECT DISTINCT
    cpe.prestad prestador,
    cpe.prestac ,
    afilmed.dbo.afn_ape_nom_afilmed_de_presmed (cpe.contra, cpe.inte , null, 'S') afiliado,
    cpe.cantidad ,
    cpe.fecha_vig,
    cpe.conve_excep,    
    valor_referencia, 
    valor_presupuestado, 
    valor_excepcion, 
    valor_liqui,
    pre.ape_razon AS prestador_nombre
      FROM conve_prestaciones_exc cpe
      INNER JOIN prestad_lugares pl ON cpe.prestad = pl.prestad 
       AND cpe.lugar = pl.lugar 
       AND cpe.baja_fecha is null
      INNER JOIN prestad_lugares_norm pln ON cpe.prestad = pln.prestad 
       AND cpe.lugar = pln.lugar  
      INNER JOIN prestadores pre ON cpe.prestad = pre.prestad
      LEFT  JOIN conve_valores_exc cve ON cpe.conve_excep = cve.conve_excep
       AND cve.baja_fecha is null 
      LEFT JOIN conceptos con ON cve.concep = con.concep
      WHERE (cpe.fecha_vig >= ("{menor}") AND cpe.fecha_vig <= ("{mayor}"))""")

    q_excepciones = df.groupby(["prestador", "prestador_nombre"])["cantidad"].sum()

    q_afiliados =  df.groupby(["prestador", "prestador_nombre"])["afiliado"].nunique()

    valor_presupuestado =  df.groupby(["prestador", "prestador_nombre"])["valor_presupuestado"].sum()

    valor_excepcion =  df.groupby(["prestador", "prestador_nombre"])["valor_excepcion"].sum()

    valor_liqui =  df.groupby(["prestador", "prestador_nombre"])["valor_liqui"].sum()

    final = pd.concat([q_excepciones,q_afiliados,valor_presupuestado,valor_excepcion,valor_liqui],axis=1).reset_index()

    final = final.sort_values(by= "cantidad",ascending= False)

    final.reset_index(drop=True, inplace=True)
    
    directory = "metrica_presupuesto"
    file = f"Métrica Presupuesto {j}.xlsx"
    final.to_excel(os.path.join(directory,file))