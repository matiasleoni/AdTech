import psycopg2

engine=psycopg2.connect(
    database="postgres",
    user="postgres",
    password="postgres",
    host="udesa-test-1.cx0iptcte3wy.us-east-1.rds.amazonaws.com",
    port='5432'
)

consulta=engine.cursor()
consulta.execute("""CREATE TABLE IF NOT EXISTS tablagrupo(id INT PRIMARY KEY); """)
consulta.execute("""INSERT INTO tablagrupo (ID) VALUES (4);""")

consulta.execute("""SELECT * FROM tablagrupo """)
rows=consulta.fetchall()
for row in rows:
    print(row)
consulta.close()
engine.close()

print('Finalizó sin error')


#Desde consola $ 
#python3 LeerSQL.py