# PASO 1: Importo librerias
from datetime import timedelta, datetime
from airflow import models
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from sqlalchemy import create_engine
import boto3
import pandas as pd
import io
import psycopg2

# PASO 2:Defino las tasks
yesterday = datetime.today()-timedelta(days=1)
hoy = datetime.today()

## COMPLETE AWS_ACCESS_KEY ID AND SECRET EVERYWHERE


def CargaAdvAct(**context):
    s3 = boto3.client("s3", aws_access_key_id='', aws_secret_access_key='')
    bucket_name = "bucketdatacruda2"
    s3_object = "advertiser_ids"
    obj = s3.get_object(Bucket=bucket_name, Key=s3_object)
    pd_ads = pd.read_csv(obj['Body'])
    # Convertir el DataFrame a formato CSV
    csv_data = pd_ads.to_csv(index=False)
    # Guardar la cadena CSV en el contexto de ejecución
    context['ti'].xcom_push(key='pd_ads', value=csv_data)
    #print(pd_ads)

def CargaView(**context):
    s3 = boto3.client("s3", aws_access_key_id='', aws_secret_access_key='')
    bucket_name = "bucketdatacruda2"
    s3_object = "ads_views"
    obj = s3.get_object(Bucket=bucket_name, Key=s3_object)
    pd_view = pd.read_csv(obj['Body'])
    pd_view=pd_view[pd_view['date']==yesterday.strftime('%Y-%m-%d')] #solo ayer
    # Obtener la cadena CSV del contexto de ejecución
    csv_data = context['ti'].xcom_pull(key='pd_ads')
    # Convertir la cadena CSV de vuelta a DataFrame
    pd_ads = pd.read_csv(io.StringIO(csv_data))
    pd_view_act=pd.merge(pd_view, pd_ads, how='inner', on='advertiser_id')
    
    # Convertir el DataFrame a formato CSV
    csv_data_view = pd_view_act.to_csv(index=False)
    # Guardar la cadena CSV en el contexto de ejecución
    context['ti'].xcom_push(key='pd_view_act', value=csv_data_view)
    #print(pd_view_act)
    
def CargaProd(**context):
    s3 = boto3.client("s3", aws_access_key_id='', aws_secret_access_key='')
    bucket_name = "bucketdatacruda2"
    s3_object = "product_views"
    obj = s3.get_object(Bucket=bucket_name, Key=s3_object)
    pd_prod = pd.read_csv(obj['Body'])
    pd_prod=pd_prod[pd_prod['date']==yesterday.strftime('%Y-%m-%d')] #solo ayer
    # Obtener la cadena CSV del contexto de ejecución
    csv_data = context['ti'].xcom_pull(key='pd_ads')
    # Convertir la cadena CSV de vuelta a DataFrame
    pd_ads = pd.read_csv(io.StringIO(csv_data))
    pd_prod_act=pd.merge(pd_prod, pd_ads, how='inner', on='advertiser_id')
    
    # Convertir el DataFrame a formato CSV
    csv_data_prod = pd_prod_act.to_csv(index=False)
    # Guardar la cadena CSV en el contexto de ejecución
    context['ti'].xcom_push(key='pd_prod_act', value=csv_data_prod)
    #print(pd_view_act)

def ModeloCTR(**context): 
    # Obtener la cadena CSV del contexto de ejecución
    csv_data_view = context['ti'].xcom_pull(key='pd_view_act')
    # Convertir la cadena CSV de vuelta a DataFrame
    pd_view_act = pd.read_csv(io.StringIO(csv_data_view))
       
    #genera el ranking por producto
    df_grouped_view_click = pd_view_act[pd_view_act['type']=='click'].groupby(['advertiser_id', 'product_id']).size().reset_index(name='count')
    df_grouped_view_all = pd_view_act.groupby(['advertiser_id', 'product_id']).size().reset_index(name='count')
    df_grouped_view_prop=pd.merge(df_grouped_view_all, df_grouped_view_click, how='left', on=['advertiser_id', 'product_id'])
    df_grouped_view_prop.fillna(0, inplace=True)
    df_grouped_view_prop['prop']=round(df_grouped_view_prop['count_y']/df_grouped_view_prop['count_x'],4)
    
    df_grouped_view_prop = df_grouped_view_prop.sort_values(['advertiser_id', 'prop','count_x'], ascending=False)
    
    rank_dict = {}
    for empresa in df_grouped_view_prop['advertiser_id'].unique():
        rank_dict[empresa] = {}
        products = df_grouped_view_prop[df_grouped_view_prop['advertiser_id'] == empresa]['product_id']
        for i, product in enumerate(products):
            rank_dict[empresa][product] = i+1
    
    df_grouped_view_prop['ranking'] = df_grouped_view_prop.apply(lambda row: rank_dict[row['advertiser_id']][row['product_id']], axis=1)
    #Ranking por producto
    df_rank_ctr= df_grouped_view_prop[df_grouped_view_prop['ranking']<=20]
    # Convertir el DataFrame a formato CSV
    csv_data_ctr = df_rank_ctr.to_csv(index=False)
    # Guardar la cadena CSV en el contexto de ejecución
    context['ti'].xcom_push(key='df_rank_ctr', value=csv_data_ctr)

def ModeloTopProduct(**context):
    # Obtener la cadena CSV del contexto de ejecución
    csv_data_prod= context['ti'].xcom_pull(key='pd_prod_act')
    # Convertir la cadena CSV de vuelta a DataFrame
    pd_prod_act = pd.read_csv(io.StringIO(csv_data_prod))
     
    #genera el ranking por producto
    df_grouped_prod = pd_prod_act.groupby(['advertiser_id', 'product_id']).size().reset_index(name='count')
    df_sorted_prod = df_grouped_prod.sort_values(['advertiser_id', 'count'], ascending=False)

    #genera el ranking
    rank_dict = {}
    for empresa in df_sorted_prod['advertiser_id'].unique():
        rank_dict[empresa] = {}
        products = df_sorted_prod[df_sorted_prod['advertiser_id'] == empresa]['product_id']
        for i, product in enumerate(products):
            rank_dict[empresa][product] = i+1
    
    df_sorted_prod['ranking'] = df_sorted_prod.apply(lambda row: rank_dict[row['advertiser_id']][row['product_id']], axis=1)
    
    #Ranking por producto
    df_rank_top= df_sorted_prod[df_sorted_prod['ranking']<=20]
    # Convertir el DataFrame a formato CSV
    csv_data_top = df_rank_top.to_csv(index=False)
    # Guardar la cadena CSV en el contexto de ejecución
    context['ti'].xcom_push(key='df_rank_top', value=csv_data_top)
 
def GrabaModelCTR(**context):
    # Obtener la cadena CSV del contexto de ejecución
    csv_df_rank_ctr = context['ti'].xcom_pull(key='df_rank_ctr')
    # Convertir la cadena CSV de vuelta a DataFrame
    pd_modelctr = pd.read_csv(io.StringIO(csv_df_rank_ctr))
    pd_modelctr = pd_modelctr[['advertiser_id', 'product_id']]
    pd_modelctr['fecha']=hoy.strftime('%Y-%m-%d')
    
    conn=psycopg2.connect(
    database="postgres",
    user="postgres",
    password="postgres",
    host="udesa-test-1.cx0iptcte3wy.us-east-1.rds.amazonaws.com",
    port='5432'
    )
    
    cursor = conn.cursor()
    
   
    # Genera la cadena de texto de la consulta
    insert_query = "INSERT INTO modelctr (advertiser_id, product_id, fecha) VALUES"

    # Agrega una cadena de texto con marcadores de posición para los valores
    values = ", ".join(["%s"] * len(pd_modelctr.columns))

    # Combina la consulta y los valores
    insert_query += " (" + values + ")"

    # Ejecuta la consulta para insertar los datos
    cursor.executemany(insert_query, pd_modelctr.values.tolist())
    
    conn.commit()
    print("Datos insertados correctamente Modelo CTR.")
   
    # Cerrar la conexión
    cursor.close()
    conn.close()


def GrabaModelTOP(**context):
    # Obtener la cadena CSV del contexto de ejecución
    csv_df_rank_top = context['ti'].xcom_pull(key='df_rank_top')
    # Convertir la cadena CSV de vuelta a DataFrame
    pd_modeltop = pd.read_csv(io.StringIO(csv_df_rank_top))
    pd_modeltop = pd_modeltop[['advertiser_id', 'product_id']]
    pd_modeltop['fecha']=hoy.strftime('%Y-%m-%d')
    
    conn=psycopg2.connect(
    database="postgres",
    user="postgres",
    password="postgres",
    host="udesa-test-1.cx0iptcte3wy.us-east-1.rds.amazonaws.com",
    port='5432'
    )
    
    cursor = conn.cursor()
    
   
    # Genera la cadena de texto de la consulta
    insert_query = "INSERT INTO modeltop (advertiser_id, product_id, fecha) VALUES"

    # Agrega una cadena de texto con marcadores de posición para los valores
    values = ", ".join(["%s"] * len(pd_modeltop.columns))

    # Combina la consulta y los valores
    insert_query += " (" + values + ")"

    # Ejecuta la consulta para insertar los datos
    cursor.executemany(insert_query, pd_modeltop.values.tolist())
    
    conn.commit()
    print("Datos insertados correctamente Modelo TOP.")
   
    # Cerrar la conexión
    cursor.close()
    conn.close()
    
# PASO 3: Setea los argumentos por default 
default_dag_args = {
'owner': 'EquipoMaBePa',
'start_date': yesterday
}
# PASO 4: Define DAG
with models.DAG(
dag_id='bash_completo3',
description='Intento =)',
#schedule_interval=timedelta(days=1),
schedule_interval='@daily',
default_args=default_dag_args) as dag:

# PASO 5: Operadores
    CargaAdv_OP = PythonOperator(
    task_id='CargaAdvertisersActivos',
    python_callable=CargaAdvAct,
    provide_context=True
    )
    
    CargaView_OP = PythonOperator(
    task_id='CargaView_FiltraActivos_ayer',
    python_callable=CargaView,
    provide_context=True
    )
        
    CargaProd_OP = PythonOperator(
    task_id='CargaProd_FiltraActivos_ayer',
    python_callable=CargaProd,
    provide_context=True
    )
   
    ModeloCTR_OP = PythonOperator(
    task_id='CorreModelo_CTR',
    python_callable=ModeloCTR,
    provide_context=True
    )   
    ModeloTOP_OP = PythonOperator(
    task_id='CorreModelo_TOP',
    python_callable=ModeloTopProduct,
    provide_context=True
    )
    
    GrabaModelCTR_OP = PythonOperator(
    task_id='GrabaModelo_CTR',
    python_callable=GrabaModelCTR,
    provide_context=True
    )     
    GrabaModelTOP_OP = PythonOperator(
    task_id='GrabaModelo_TOP',
    python_callable=GrabaModelTOP,
    provide_context=True
    )   

# PASO 6:  DAG dependencias
CargaAdv_OP >> CargaView_OP
CargaAdv_OP >> CargaProd_OP
CargaView_OP >> ModeloCTR_OP
CargaProd_OP >> ModeloTOP_OP
ModeloCTR_OP >> GrabaModelCTR_OP
ModeloTOP_OP >> GrabaModelTOP_OP