from dbconn import querydb, querydbtopandas 
import pandas as pd 
import datetime
import calendar
import os

#parametros de calificacicones
path = "parametros_calificaciones/items_encuestas.xlsx"

items_encuestas = str(pd.read_excel(path).item_id.tolist()).strip("[").strip("]")

dict_id = {3: 'Atención Médica',
 2: 'Trato y Cordialidad',
 4: 'Disponibilidad de Turno',
 1: 'Puntualidad',
 5: 'Limpieza y Confort'}   

menor = str(datetime.datetime.today() - datetime.timedelta(days=20))[:7]
mayor = str(datetime.datetime.today())[:7] 
menor_año = str(datetime.datetime.today() - datetime.timedelta(days=385))[:7]

if menor[-2:] == "01":
    eliminar =  str(int(menor[:4]) -1) + "-12"
elif menor[-2:] in ["02","03","04","05","06","07","08","09","10"]:
    eliminar = str(int(menor[:4])-1) + "-0" + str(int(menor[-2:])-1)
else:
    eliminar = str(int(menor[:4])-1) + "-" + str(int(menor[-2:])-1)

os.remove(f"datos_calificaciones/{eliminar}.gzip")
    
for i,j in zip([menor, menor_año], [menor, "acumulado"]): 
    df = querydbtopandas(f"""
    select  a11.id_item  id,
           a11.id_encuesta  id_encuesta,
           a12.id_afiliado  id_afi_afiliado,
           a12.id_prestador  id_pre_prestador,
           a17.desc_pre_nombre  desc_pre_nombre_efector,
           a18.desc_pre_nombre  desc_pre_nombre,
           a18.id_pre_tipo,   
           a12.id_prest_efector,
           fec_encuesta,
           a11.i_R RESPUESTA
    from        DBA.ft_d_prest_encuestas        a11
           join        DBA.ft_prest_encuestas        a12
             on        (a11.id_encuesta = a12.id_encuesta)
           join        DBA.d_pre_prestador        a17
             on        (a12.id_prest_efector = a17.id_pre_prestador)      
           join        DBA.d_pre_prestador        a18
             on        (a12.id_prestador = a18.id_pre_prestador)
    where (cast(fec_encuesta as date) >= date("{i}") and cast(fec_encuesta as date) < date("{mayor}")
    and a11.id_item in ({items_encuestas})
    and a18.id_pre_tipo in ("E","C","P","I"))
    group by        a11.id_item,
           a11.i_R,
           fec_encuesta,
           a11.id_encuesta,
           a12.id_afiliado,
           a12.id_prestador,
           a17.desc_pre_nombre,    
           a18.id_pre_tipo,
           a18.desc_pre_nombre,
           a12.id_prest_efector""")

    dict_id = {3: 'Atención Médica',
     2: 'Trato y Cordialidad',
     4: 'Disponibilidad de Turno',
     1: 'Puntualidad',
     5: 'Limpieza y Confort'}   


    df["id"] = df["id"].map(dict_id)

    df_part_equipos = df[df["id_pre_tipo"].isin(["P","E"])][["id","id_encuesta", "id_afi_afiliado", "id_pre_prestador", "desc_pre_nombre", "RESPUESTA" ]]

    df_inst_circ = df[df["id_pre_tipo"].isin(["I","C"])][["id","id_encuesta","id_afi_afiliado", "id_prest_efector", "desc_pre_nombre_efector", "RESPUESTA"]]

    df_inst_circ.rename(columns={"id_prest_efector": "id_pre_prestador", "desc_pre_nombre_efector":"desc_pre_nombre"},inplace=True)

    df = pd.concat([df_part_equipos, df_inst_circ])

    df = df[df["id_pre_prestador"] != 0]

    q_afiliados = df.groupby("id_pre_prestador")["id_afi_afiliado"].nunique().rename_axis('id_pre_prestador').reset_index(name='q_afiliados')

    q_respuestas = df.groupby("id_pre_prestador")["id_encuesta"].nunique().rename_axis('id_pre_prestador').reset_index(name='q_respuestas')

    df = df.merge(q_respuestas).merge(q_afiliados)

    pivot = pd.pivot_table(df, 
                 index=["id_pre_prestador","desc_pre_nombre", "q_afiliados", "q_respuestas"], 
                 columns="id", 
                 values="RESPUESTA", aggfunc= ["mean", "sum"]).reset_index()
    pivot.columns = ["Prestador", 'Razón social', 'Q afiliados', "Q respuestas", 'Atención Médica m', 'Disponibilidad de Turno m',
               'Limpieza y Confort m', 'Puntualidad m', 'Trato y Cordialidad m',
               'Atención Médica s', 'Disponibilidad de Turno s', 'Limpieza y Confort s',
               'Puntualidad s', 'Trato y Cordialidad s']

    pivot.rename(columns={
                    'Atención Médica s':"Calificación Atención Médica",
                    'Disponibilidad de Turno s':"Calificación Disponibilidad de Turno",
                    'Limpieza y Confort s':"Calificación Limpieza y Confort",
                    'Puntualidad s': "Calificación Puntualidad", 
                    'Trato y Cordialidad s':"Calificación Trato y Cordialidad",
                    'Atención Médica m':"Promedio Calificación Atención Médica", 
                    'Disponibilidad de Turno m':"Promedio Calificación Disponibilidad de Turno", 
                    'Limpieza y Confort m':"Promedio Calificación Limpieza y Confort",
                    'Puntualidad m':"Promedio Calificación Puntualidad",
                    'Trato y Cordialidad m':"Promedio Calificación Trato y Cordialidad"}, inplace=True)

    pivot["Promedio total"] = (pivot["Promedio Calificación Atención Médica"]+
                                  pivot["Promedio Calificación Disponibilidad de Turno"]+
                                  pivot["Promedio Calificación Limpieza y Confort"]+
                                  pivot["Promedio Calificación Puntualidad"]+
                                  pivot["Promedio Calificación Trato y Cordialidad"]) / 5

    pivot= pivot[['Prestador', 'Razón social', 'Q respuestas', 'Q afiliados',
                         'Calificación Atención Médica', 'Promedio Calificación Atención Médica',
                         'Calificación Disponibilidad de Turno','Promedio Calificación Disponibilidad de Turno',
                         'Calificación Limpieza y Confort',   'Promedio Calificación Limpieza y Confort',
                         'Calificación Puntualidad',   'Promedio Calificación Puntualidad',
                         'Calificación Trato y Cordialidad',  'Promedio Calificación Trato y Cordialidad','Promedio total']]
    pivot = pivot.sort_values(by="Promedio total", ascending= True)
    pivot = pivot.round(2)

    pivot.to_parquet(f'datos_calificaciones/{j}.gzip',compression='gzip')
