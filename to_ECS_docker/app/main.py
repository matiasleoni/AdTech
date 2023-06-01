from fastapi import FastAPI
import datetime
import json
import psycopg2

app = FastAPI()

contador_consultas_modelo = 0
contador_consultas_advertiser = 0

def translate_modelo(Modelo):
    '''
    INPUT: el modelo que el usuario de la API pone en la web adress. Valores esperados 
    según consigna: TopCTR, TopProduct
    OUTPUT: nombre de la tabla correspondiente de SQL (modeltop, modelctr). Si el nombre
    del input no es el esperado se devuelve igual.
    '''
    if Modelo.lower() == 'topctr':
        tabla = 'modeltop'
    elif Modelo.lower() == 'topproduct':
        tabla = 'modelctr'
    else:
        tabla = Modelo
    return tabla

### Configuración de la base de datos del servicio RDS de AWS
db_conf = {"database": "postgres",
    "user": "postgres",
    "password": "postgres",
    "host": "udesa-test-1.cx0iptcte3wy.us-east-1.rds.amazonaws.com",
    "port": '5432'}

from fastapi.responses import HTMLResponse

### get en el ROOT de la API. Debería dar instrucciones
@app.get("/")
async def root():
   ret='''
<html>
<body>
<h2>Hola Usuario!</h2>
<p>Para la documentación técnica de la API visitar /docs. <p/>
<p>En /recommendations/&lt ADV &gt/&lt Model&gt se puede obtener el top 20 de recomendaciones
en la fecha de hoy para un dado advertiser donde &ltADV&gt es el ID del advertiser y &lt Model&gt puede ser 
o bien "TopCTR" o "TopModel". <p/>
<p>En /history/&lt ADV&gt se pueden obtener las recomendaciones de los últimos 7 días para un dado 
advertiser. <p/>
<p>En /stats<a/> se puede obtener: <p/>
<ul>
    <li> Número de advertisers activos. </li>
    <li> Número de consultas al feature /recommendation </li>
    <li> Número de consultas al feature /history </li>
    <li> Recomendaciones para cada cliente dónde ambos modelos coinciden.</li>
</ul>

</body>
</html>
'''
   return HTMLResponse(content=ret)
#    return {"message": "Hello World, trial {}.".format(1)}


### get de la API para obtener recomendaciones dado un advertiser y un modelo
@app.get("/recommendations/{ADV}/{Modelo}")
def reco(ADV, Modelo):
    global contador_consultas_modelo

    filter_date = (datetime.date.today()-0*datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    tabla = translate_modelo(Modelo)

    Query = " SELECT DISTINCT Product_ID FROM {} WHERE Advertiser_ID = '{}' AND fecha = '{}';".format(tabla,ADV, filter_date)
    #Query = " SELECT * FROM tabla  WHERE fecha = '{}';".format(filter_date)

    engine = None
    try:
        engine = psycopg2.connect(**db_conf)
        consulta=engine.cursor()
        consulta.execute(Query)
        rows = consulta.fetchall()
        lista_productos = []
        for row in rows:
            lista_productos.append(row[0])
        result = {ADV: lista_productos}
        consulta.close()
    except psycopg2.DatabaseError as error:
        result = {ADV: error.pgerror.split("\n")[0]+". Ingrese TopCTR o TopProduct."}
        #print(error.pgerror.split("\n")[0])
    finally:
        if engine is not None:
            engine.close()

    #dic_answer = {str(ADV): recomendaciones[str(Modelo)][str(ADV)]}
    dic_answer = result
    json_answer = json.dumps(dic_answer)
    contador_consultas_modelo += 1
    #return json_answer
    return dic_answer


### get de la API para obtener recomendaciones dado un advertiser y un modelo
@app.get("/history/{ADV}")
def historic(ADV):
    global contador_consultas_advertiser
    filter_dates_list = [(datetime.date.today()-num*datetime.timedelta(days=1)).strftime("%Y-%m-%d") for num in range(7)]
    filter_dates = str(filter_dates_list).replace("[","(").replace("]",")")
    

    query = f"""SELECT DISTINCT fecha, 'modeltop' as modelo, product_id from modeltop
    WHERE fecha IN{filter_dates} AND advertiser_id= '{ADV}'
    UNION
    SELECT DISTINCT fecha, 'modelctr' as modelo, product_id from modelctr
    WHERE fecha IN{filter_dates} AND advertiser_id= '{ADV}'"""

    engine = None
    try:
        engine = psycopg2.connect(**db_conf)
        consulta=engine.cursor()
        consulta.execute(query)
        rows = consulta.fetchall()
        lista_productos = []
        for row in rows:
            lista_productos.append(row)
        #result = {ADV: lista_productos}
        result = lista_productos
        consulta.close()
    except psycopg2.DatabaseError as error:
        result = {"Problema en la base de datos": "Consulte administrador."}
    finally:
        if engine is not None:
            engine.close()
    
    if type(result) == dict:
        dic_out = result
    elif type(result) == list:
        dic_out = {}
        for date in filter_dates_list:
            lista1 = []
            lista2 = []
            for line in result:
                if line[0] == date and line[1] == 'modeltop':
                    lista1.append(line[2])
                elif line[0] == date and line[1] == 'modelctr':
                    lista2.append(line[2])

            dic_out[date] = {"TopProduct": lista1, "TopCTR": lista2}

    contador_consultas_advertiser += 1
    return dic_out



@app.get("/stats")
def stats():
    #contador_consultas_modelo
      
    filter_date = (datetime.date.today()-0*datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    query1 = """WITH prov AS(
        SELECT DISTINCT advertiser_id FROM modeltop
        UNION
        SELECT DISTINCT advertiser_id FROM modelctr)
        SELECT COUNT(*) FROM prov"""
    query2 = f"""SELECT DISTINCT modelctr.advertiser_id, 
        modelctr.product_id as reco_ctr,
        modeltop.product_id as reco_top
    FROM modelctr
    JOIN modeltop ON modelctr.advertiser_id = modeltop.advertiser_id
    WHERE modelctr.product_id = modeltop.product_id
        and modelctr.fecha = '{filter_date}'
        and modeltop.fecha = '{filter_date}'
    ORDER BY advertiser_id"""
    
    engine = None
    try:
        engine = psycopg2.connect(**db_conf)
        consulta=engine.cursor()
        consulta.execute(query1)
        rows1 = consulta.fetchall()
        cantidad_advs = rows1[0][0]
        consulta.execute(query2)
        repetidos = consulta.fetchall()
        consulta.close()
    except psycopg2.DatabaseError as error:
        cantidad_advs = {"Problema en la base de datos": "Consulte administrador."}
        #print(error.pgerror.split("\n")[0])
    finally:
        if engine is not None:
            engine.close()
    
    lista_unicos = []
    for row in repetidos:
        lista_unicos.append(row[0])
    lista_unicos = set(lista_unicos)
    dic_out2 = {}
    for elem in lista_unicos:
        lista3 = []
        for row in repetidos:
            if row[0] == elem:
                lista3.append(row[1])
        dic_out2[elem]=lista3

    return {'Cantidad de advertisers':cantidad_advs, 
            "Número consultas /recommendations/": contador_consultas_modelo,
            "Número consultas /history/": contador_consultas_advertiser,
            "Advertiser con recos coincidentes": dic_out2 }

