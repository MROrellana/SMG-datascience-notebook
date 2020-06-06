from dbconn import querydb, querydbtopandas 
import pandas as pd 
import datetime
import calendar
import os


mes = calendar.month_name[(datetime.datetime.today() - datetime.timedelta(days=135)).month]
acumulado = "acumulado"

for i,j in zip([135,285],[mes,acumulado]):

    menor = str(datetime.datetime.today() - datetime.timedelta(days=i))[:10]

    mayor = str(datetime.datetime.today() - datetime.timedelta(days=104))[:10]

    df = querydbtopandas(f"""select id_prestador_efector, 
        a14.id_afiliado,
        desc_pre_nombre, 
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
    where CONVERT(DATETIME,d.exp_mes, "mm-YYYY") >= date("{menor}") and CONVERT(DATETIME,d.exp_mes, "mm-YYYY") < date("{mayor}")
    and id_prestador_efector not in (0)
    and tbl_origen = 'receta_medicamento'
    group by id_prestador_efector, desc_pre_nombre, a14.id_afiliado,Q.deno,
        id_medicamento,
    i_ft_cantidad, i_ft_importe""")
    
    importe = df.groupby(["id_prestador_efector","desc_pre_nombre", "deno" ])["importe"].sum()

    cantidad_ordenes = df.groupby(["id_prestador_efector","desc_pre_nombre", "deno" ])["cantidad"].sum()

    cantidad_afiliados = df.groupby(["id_prestador_efector","desc_pre_nombre", "deno" ])["id_afiliado"].nunique()

    df = pd.concat([importe,cantidad_ordenes,cantidad_afiliados],axis=1).reset_index()

    df["promedio por afiliado"] = df["importe"] / df["id_afiliado"]
    df["promedio por receta"] = df["importe"] / df["cantidad"]

    suma_especialidad = df.groupby("deno")["promedio por afiliado"].sum()

    num_prestador_esp = df.groupby("deno")["desc_pre_nombre"].nunique()

    media_especialidad = (suma_especialidad/num_prestador_esp).reset_index().rename(columns= {0: "media por especialidad"})

    df = df.merge(media_especialidad)

    df["Diferencia respecto de la media"] = ((df["promedio por afiliado"] / df["media por especialidad"]) -1 )*100

    df = df.round(2)

    df = df[['id_prestador_efector', 'desc_pre_nombre', 'deno',  'media por especialidad',  'Diferencia respecto de la media',
            'id_afiliado', 'cantidad', 'promedio por afiliado',
           'promedio por receta', 'importe' ]]

    df.columns = ["N° Prestador", "Médico", "Especialidad", "Media por especialidad", "Diferencia respecto de la media", "Afil. Usuarios", "Recetas", "Promedio por afiliado", "Promedio por receta", "A cargo de SMMP"]

    directory = "metrica_farmacia"
    file = f"Métrica Farmacia {j}.xlsx"
    df.to_excel(os.path.join(directory,file))