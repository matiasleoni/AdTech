import psycopg2

conn=psycopg2.connect(
    database="postgres",
    user="postgres",
    password="postgres",
    host="udesa-test-1.cx0iptcte3wy.us-east-1.rds.amazonaws.com",
    port='5432'
)

cur=conn.cursor()


# Definir la consulta para crear la tabla
create_table_modeltop = '''
    CREATE TABLE modeltop (
        advertiser_id VARCHAR(20),
        product_id VARCHAR(6),
        fecha VARCHAR(12)
    )
'''
create_table_modelctr = '''
    CREATE TABLE modelctr (
        advertiser_id VARCHAR(20),
        product_id VARCHAR(6),
        fecha VARCHAR(12)
    )
'''

# Ejecutar la consulta para crear la tabla
cur.execute(create_table_modeltop)
cur.execute(create_table_modelctr)

#genero un registro de prueba
cur.execute("""INSERT INTO modelctr (advertiser_id,product_id,fecha) VALUES ('HC26ZE93SA4WWA0BRFM6', '73c363','2023-01-01');""")
cur.execute("""INSERT INTO modeltop (advertiser_id,product_id,fecha) VALUES ('HC26ZE93SA4WWA0BRFM6', '73c363','2023-01-01');""")


# Confirmar los cambios en la base de datos
conn.commit()

cur.execute("""SELECT * FROM modelctr """)
rows=cur.fetchall()
for row in rows:
    print(row)
cur.execute("""SELECT * FROM modeltop """)
rows=cur.fetchall()
for row in rows:
    print(row)
# Cerrar el cursor y la conexión
cur.close()
conn.close()

print('Finalizó sin error')


#Desde consola $ 
#python3 LeerSQL.py