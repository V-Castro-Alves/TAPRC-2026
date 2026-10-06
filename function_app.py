import logging
import azure.functions as func
import os
import pyodbc

app = func.FunctionApp()

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_analista(myTimer: func.TimerRequest) -> None:
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

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_categoria(myTimer: func.TimerRequest) -> None:
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
        cursor.execute("SELECT * FROM itsm.categoria;")
        rows = cursor.fetchall()
        
        # Imprimir os dados da tabela usando logging.info
        for row in rows:
            logging.info(row)

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
        cursor.execute("SELECT * FROM itsm.chamado;")
        rows = cursor.fetchall()
        
        # Imprimir os dados da tabela usando logging.info
        for row in rows:
            logging.info(row)

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_chamado_sla(myTimer: func.TimerRequest) -> None:
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
        cursor.execute("SELECT * FROM itsm.chamado_sla;")
        rows = cursor.fetchall()
        
        # Imprimir os dados da tabela usando logging.info
        for row in rows:
            logging.info(row)

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_chamado_status_historico(myTimer: func.TimerRequest) -> None:
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
        cursor.execute("SELECT * FROM itsm.chamado_status_historico;")
        rows = cursor.fetchall()
        
        # Imprimir os dados da tabela usando logging.info
        for row in rows:
            logging.info(row)

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_cliente_organizacao(myTimer: func.TimerRequest) -> None:
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
        cursor.execute("SELECT * FROM itsm.cliente_organizacao;")
        rows = cursor.fetchall()
        
        # Imprimir os dados da tabela usando logging.info
        for row in rows:
            logging.info(row)

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_csat_avaliacao(myTimer: func.TimerRequest) -> None:
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
        cursor.execute("SELECT * FROM itsm.csat_avaliacao;")
        rows = cursor.fetchall()
        
        # Imprimir os dados da tabela usando logging.info
        for row in rows:
            logging.info(row)

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_fila(myTimer: func.TimerRequest) -> None:
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
        cursor.execute("SELECT * FROM itsm.fila;")
        rows = cursor.fetchall()
        
        # Imprimir os dados da tabela usando logging.info
        for row in rows:
            logging.info(row)

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_sla(myTimer: func.TimerRequest) -> None:
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
        cursor.execute("SELECT * FROM itsm.sla;")
        rows = cursor.fetchall()
        
        # Imprimir os dados da tabela usando logging.info
        for row in rows:
            logging.info(row)

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_solicitante(myTimer: func.TimerRequest) -> None:
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
        cursor.execute("SELECT * FROM itsm.solicitante;")
        rows = cursor.fetchall()
        
        # Imprimir os dados da tabela usando logging.info
        for row in rows:
            logging.info(row)
