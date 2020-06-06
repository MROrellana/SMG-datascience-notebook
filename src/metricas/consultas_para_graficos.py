from dbconn import querydb, querydbtopandas 
import pandas as pd
import numpy as np
import datetime
import calendar
import os

path1 = "parametros_consultas/prestaciones_excluidas.xlsx"

prestaciones_excluidas = pd.read_excel(path1 ,usecols = ["prestac_pres_prestacion"], dtype=str )["prestac_pres_prestacion"].tolist()
prestaciones_excluidas = str(prestaciones_excluidas).strip("[").strip("\"]")

zona = "2,3,4,5"
provincia = "1,2"


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
#os.remove(f"datos_consultas/{eliminar}.gzip")


for i,j in zip([menor, menor_año], [menor, "acumulado"]): 
    df = querydbtopandas(f"""select a11.id_pres_prestacion,
           a16.prestac_pres_prestacion,
           a11.id_pre_prestador,
           a13.desc_pre_nombre,
           a11.id_afi_afiliado ,  
           Q.deno,
           a11.id_tie_dia_consumo,   
           FLOOR(DATEDIFF(year, a14.naci_fecha, a11.id_tie_dia_consumo)) edad_afiliado 

    from        DBA.ft_ordenes        a11
           join        DBA.d_pre_prestador        a13
             on        (a11.id_pre_prestador = a13.id_pre_prestador)
           join        DBA.afi_afiliados        a14
             on        (a11.id_afi_afiliado = a14.id_afiliado)
           join        DBA.d_pres_prestacion        a16
             on        (a11.id_pres_prestacion = a16.id_pres_prestacion)     
           join       DBA.d_prof_convertir_especialidad a19  
            on         (a13.id_pre_especialidad  = a19.id_prof_especialidad)
           LEFT JOIN dba.prestad_costo_centros E
            ON a11.id_pre_prestador = E.prestad and E.baja_fecha is null and e.prepaga = ( select min(PCC1.prepaga) from dba.prestad_costo_centros PCC1 where PCC1.prestad =  e.prestad )   
           LEFT JOIN dba.costo_centros Q
            ON E.centro = Q.centro
    where        (a13.id_pre_tipo in ('E', 'P')            
    and a11.id_nom_nomenclador in (5)            
    and cast(id_tie_dia_consumo as date) >= date("{i}") and cast(id_tie_dia_consumo as date) < date("{mayor}")
    and a13.id_afi_zona in ({zona})
    and a13.id_afi_provincia in ({provincia})

    and RTRIM(a16.prestac_pres_prestacion) not in ({prestaciones_excluidas}))
    group by a11.id_pres_prestacion,
           a16.prestac_pres_prestacion,
           a11.id_pre_prestador,
           a13.desc_pre_nombre,
           Q.deno,
           a11.id_afi_afiliado,
           a11.id_tie_dia_consumo,
           edad_afiliado""")

    reconsultas = df.groupby(["id_pre_prestador", "desc_pre_nombre", "deno", "id_afi_afiliado"])["id_afi_afiliado"].count().rename("CANTIDADORDENES0").reset_index()
    reconsultas["uno"] = 1

    pivot_1 = pd.pivot_table(reconsultas, values='uno', index=['id_pre_prestador', "desc_pre_nombre", "deno"],
                 columns=['CANTIDADORDENES0'], aggfunc=np.sum).fillna(0)

    pivot_1["Más de 4 - Q afiliados"] = pivot_1[pivot_1.columns.tolist()[4:]].sum(axis=1)

    edad_promedio_afiliados = pd.DataFrame(df.groupby(["id_pre_prestador",  "desc_pre_nombre", "deno"])["edad_afiliado"].mean())
    total_consultas_prestador = reconsultas.groupby(["id_pre_prestador",  "desc_pre_nombre", "deno"])["CANTIDADORDENES0"].sum()
    pivot = pd.concat([total_consultas_prestador,edad_promedio_afiliados, pivot_1],axis=1)
    pivot.reset_index(inplace=True)
    if 1 not in pivot.columns:
        pivot[1] = 0
    if 2 not in pivot.columns:
        pivot[2] = 0
    if 3 not in pivot.columns:
        pivot[3] = 0
    if 4 not in pivot.columns:
        pivot[4] = 0

    pivot["Consultas - participación %"] =  (pivot[1]/pivot["CANTIDADORDENES0"])*100
    pivot["2 consultas - participación %"] =  ((pivot[2]*2)/pivot["CANTIDADORDENES0"])*100
    pivot["3 consultas - participación %"] =  ((pivot[3]*3)/pivot["CANTIDADORDENES0"])*100

    pivot["4 consultas - participación %"] =  ((pivot[4]*4)/pivot["CANTIDADORDENES0"])*100

    pivot["Participación %"] = 100 - pivot["Consultas - participación %"]
    pivot["Más de 4 - participación %"] = pivot["Participación %"] - (pivot["2 consultas - participación %"]+pivot["3 consultas - participación %"]+pivot["4 consultas - participación %"])
    pivot["Total de reconsultas"] = pivot[2] + pivot[3] + pivot[4] + pivot["Más de 4 - Q afiliados"]
    pivot.rename(columns= {1: "Consultas - Q afiliados", 2: "2 consultas - Q afiliados", 3: "3 consultas - Q afiliados", 4: "4 consultas - Q afiliados", "desc_pre_nombre": "Razon social",
    "deno": "Especialidad","id_pre_prestador": "Prestador", "edad_afiliado": "Promedio edad de afiliados", "CANTIDADORDENES0": "Total Consultas" },inplace=True)    
    pivot = pivot.sort_values("Participación %", ascending=False).round(2)
    pivot = pivot.reset_index(drop=True)
    pivot = pivot[['Prestador', 'Razon social', 'Especialidad', 'Total Consultas',
           'Promedio edad de afiliados', 'Consultas - Q afiliados','Consultas - participación %',
           '2 consultas - Q afiliados', '2 consultas - participación %',
           '3 consultas - Q afiliados', '3 consultas - participación %',
           '4 consultas - Q afiliados',  '4 consultas - participación %',
           'Más de 4 - Q afiliados',  'Más de 4 - participación %',
           'Total de reconsultas','Participación %']]

    pivot.to_parquet(f'datos_consultas/{j}.gzip',compression='gzip') 



