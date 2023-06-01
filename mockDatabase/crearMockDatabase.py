import psycopg2

db_conf = {"database": "postgres",
    "user": "postgres",
    "password": "postgres",
    "host": "udesa-test-1.cx0iptcte3wy.us-east-1.rds.amazonaws.com",
    "port": '5432'}



engine = psycopg2.connect(**db_conf)
f = open('crearDatabaseFicticia.sql')
basecreacion = f.read()
f.close()

consulta=engine.cursor()
consulta.execute("""DROP TABLE IF EXISTS modelctr""")
consulta.execute("""DROP TABLE IF EXISTS modeltop""")
consulta.execute(basecreacion)
engine.commit()

consulta.execute("SELECT * FROM modeltop")
rows = consulta.fetchall()
print('TABLA MODELTOP')
i= 0
for row in rows:
    i+=1
    print(i, row)
consulta.execute("SELECT * FROM modelctr")
rows = consulta.fetchall()
print('TABLA CTR')
i=0
for row in rows:
    i+=1
    print(i,row)

    consulta.close()
    engine.close()