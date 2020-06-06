from dbconn import querydb, querydbtopandas 
import pandas as pd 
import datetime
import calendar
import os

pd.options.mode.chained_assignment = None

#parametros de la metrica
path1 = "parametros_imagenes/especialidades_exceptuadas.xlsx"
esp_exc = pd.read_excel(path1).esp_exceptuadas.tolist()

path2 = "parametros_imagenes/prestaciones_imagenes.xlsx"
prestaciones_imagenes = pd.read_excel(path2,index_col=0).prestac_pres_prestacion.tolist()
prestaciones_imagenes = [str(x) for x in prestaciones_imagenes]
prestaciones_imagenes = str(prestaciones_imagenes).strip("[").strip("]")

path3 = "parametros_imagenes/centros_de_imagenes.xlsx"
centros_de_imagenes = str(pd.read_excel(path3,index_col=0).id_pre_prestador.tolist()).strip("[").strip("]")

path4 = "parametros_imagenes/homologaciones.xlsx"
homologaciones = pd.read_excel(path4,dtype=str,index_col=0)
validacion_0 = homologaciones.validacion_0.dropna().tolist()
validacion_1 = homologaciones.validacion_1.dropna().tolist()
validacion_2 = homologaciones.validacion_2.dropna().tolist()
validacion_3 = homologaciones.validacion_3.dropna().tolist()

#
menor = str(datetime.datetime.today() - datetime.timedelta(days=20))[:7]
mayor = str(datetime.datetime.today())[:7] 
menor_año = str(datetime.datetime.today() - datetime.timedelta(days=385))[:7]

if menor[-2:] == "01":
    eliminar =  str(int(menor[:4]) -1) + "-12"
elif menor[-2:] in ["02","03","04","05","06","07","08","09","10"]:
    eliminar = str(int(menor[:4])-1) + "-0" + str(int(menor[-2:])-1)
else:
    eliminar = str(int(menor[:4])-1) + "-" + str(int(menor[-2:])-1)

#os.remove(f"datos_imagenes/{eliminar}.gzip")

for i,j in zip([menor, menor_año], [menor, "acumulado"]): 
    df = querydbtopandas(f"""select a11.transac  transac,
    a11.id_afiliado  id_afi_afiliado,
    a11.id_pres_prestacion  id_pres_prestacion,
    max(a17.desc_pres_prestacion)  desc_pres_prestacion,
    max(a17.prestac_pres_prestacion)  prestac_pres_prestacion,
    a11.transac_rela  transac_rela,
    a12.id_pre_prestador  id_pre_prestador0,
    max(a14.desc_pre_nombre)  desc_pre_nombre0,
    Q.deno,
    sum(a11.canti)  QTRANSAC
    from DBA.ft_cm_transac_remotas a11
    join DBA.d_pre_demandante_transac a12
     on (a11.id_pre_prestador_demandante = a12.id_pre_prestador_demandante)
    join DBA.d_pre_prestador a14
     on (a12.id_pre_prestador = a14.id_pre_prestador)
    join DBA.d_pres_prestacion a17
     on (a11.id_pres_prestacion = a17.id_pres_prestacion)
    LEFT JOIN dba.prestad_costo_centros E
        ON a12.id_pre_prestador_demandante = E.prestad and E.baja_fecha is null and e.prepaga = ( select min(PCC1.prepaga) from dba.prestad_costo_centros PCC1 where PCC1.prestad =  e.prestad )   
    LEFT JOIN dba.costo_centros Q
        ON E.centro = Q.centro

    where (cast(a11.fecha as date) >= date("{i}") and cast(a11.fecha as date) < date("{mayor}")
     and a11.id_pre_prestador in ({centros_de_imagenes})
     and a11.tran_tipo in ("IP")
     and a11.baja_fecha is null
     and recha in (0)
     and RTRIM(a17.prestac_pres_prestacion) in ({prestaciones_imagenes})
     and a12.id_pre_prestador <> 0)
    group by a11.transac,
    Q.deno,
    a11.id_afiliado,
    a11.id_pres_prestacion,

    a11.transac_rela,
    a12.id_pre_prestador""")
    
    
    transac_ref = str(df.transac_rela.tolist()).strip("[").strip("]")

    df_id = querydbtopandas(f"""select transac_ref, icd as ICD from DBA.ft_cm_transac_remotas
                    where tran_tipo in ("ID")
                    and cast(fecha as date) >= date("{menor}") and cast(fecha as date) < date("{mayor}")
                    and transac_ref in ({transac_ref})""")

    df_ip = df[["id_pre_prestador0","desc_pre_nombre0", "prestac_pres_prestacion", "desc_pres_prestacion", "transac_rela", "deno"]]
    
    df_ip.deno = df_ip.deno.replace({None:"None"})
    
    for i in validacion_0:
        df_id.loc[df_id["ICD"].str.strip() == i, "ICD" ] = 0
    
    for i in validacion_1:
        df_id.loc[df_id["ICD"].str.strip() == i, "ICD" ] = 1 
    
    for i in validacion_2:
        df_id.loc[df_id["ICD"].str.strip() == i, "ICD" ] = 2
    
    for i in validacion_3:
        df_id.loc[df_id["ICD"].str.strip() == i, "ICD" ] = 3
    
    df_id = df_id[df_id["ICD"].isin([0,1,2,3])]
    
    for i in esp_exc:
        df_ip = df_ip[~df_ip["deno"].str.contains(i)]

    df_ip.deno = df_ip.deno.replace({None:"None"})                
#elimino todas las prestaciones menos la rmn mamaria
    df_ip_rmnmamaria = df_ip[df_ip["deno"] == "RMN Mamaria"]

    df_ip = df_ip[~df_ip["desc_pres_prestacion"].isin([x for x in df_ip["desc_pres_prestacion"] if 'mam' in x.lower()])]

    df_ip = pd.concat([df_ip, df_ip_rmnmamaria],axis=0)

    df_id = df_id.groupby("transac_ref")["ICD"].unique().reset_index()

    def greatest_selection (df_id):
        for i in range(len(df_id.ICD)):
            if len(df_id.ICD[i]) <= 1:
                df_id.ICD[i] = df_id.ICD[i][0]

            elif len(df_id.ICD[i]) > 1:
                df_id.ICD[i].sort()
                df_id.ICD[i] = df_id.ICD[i][-1]
        return df_id

    df_id = greatest_selection(df_id)

    final = pd.merge(df_ip, df_id, left_on="transac_rela",right_on= "transac_ref")

    final = final[["id_pre_prestador0","desc_pre_nombre0", "deno","ICD"]]

    q_transacciones= final.groupby(["id_pre_prestador0"]).count().reset_index()[["id_pre_prestador0","desc_pre_nombre0"]].rename(columns={"desc_pre_nombre0": "Q de transacciones"})

    final_pivot = pd.pivot_table(final, values='id_pre_prestador0', 
                   index=['id_pre_prestador0', 'desc_pre_nombre0', "deno"],
                    columns="ICD", aggfunc="size")

    final_pivot.fillna(0,inplace=True)
    final_pivot.reset_index(inplace=True)
    final_pivot = pd.merge(q_transacciones, final_pivot)

    final_pivot["Normalidad"] = (final_pivot[0] + final_pivot[1] )/ final_pivot["Q de transacciones"]

    total_esp = final_pivot.groupby("deno")["Q de transacciones"].sum().reset_index().rename(columns={"Q de transacciones": "total_esp"})

    final_pivot = pd.merge(final_pivot, total_esp)
    final_pivot["Participación"] = final_pivot["Q de transacciones"] / final_pivot["total_esp"]
    final_pivot["Participación"] = final_pivot["Participación"].mul(100).astype(float).round(2).astype(str).add('%')
    final_pivot.rename(columns={"id_pre_prestador0": "N° Prescriptor", "desc_pre_nombre0": "Prescriptor","Q de transacciones": "Total general"},inplace=True)
    imagenes_tabla = final_pivot[["N° Prescriptor", "Prescriptor", 0,1,2,3,  "Total general","Normalidad", "Participación" ]]

    final_imagenes = imagenes_tabla.sort_values(by= "Total general", ascending= False)

    final_imagenes.columns = ['N° Prescriptor', 'Prescriptor', '0', '1', '2', '3', 'Total general',
           'Normalidad', 'Participación']

    final_imagenes = final_imagenes.reset_index(drop=True).round(2)
    
    final_imagenes.to_parquet(f'datos_imagenes/{j}.gzip',compression='gzip')