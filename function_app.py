import logging
import azure.functions as func
import os
import pyodbc

app = func.FunctionApp()

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_chamado(myTimer: func.TimerRequest) -> None:
    #importar as variaveis de ambeinte 
    host_sql = os.getenv("HOST")
    database_sql = os.getenv("DATABASE")
    user_sql = os.getenv("USER")
    password_sql = os.getenv("PASSWORD")

    #como criar uma connection string usando pyodbc
    conn = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={host_sql};"
        f"DATABASE={database_sql};"
        f"UID={user_sql};"
        f"PWD={password_sql};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )

    # Criar conexão com o banco
    with pyodbc.connect(conn) as connection:
        cursor = connection.cursor()
        # Fazer um select * na tabela
        cursor.execute("SELECT * FROM itsm.analista;")
        rows = cursor.fetchall()
        
        # Imprimir os dados da tabela usando logging.info
        for row in rows:
            logging.info(row)

    # Fazer o deploy