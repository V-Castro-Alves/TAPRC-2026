import csv
import io
import logging
import os
from datetime import UTC, datetime

import azure.functions as func
import pyodbc
from azure.storage.filedatalake import DataLakeServiceClient

app = func.FunctionApp()
logger = logging.getLogger(__name__)


def _get_sql_connection() -> pyodbc.Connection:
    settings = {
        "host": os.getenv("HOST"),
        "database": os.getenv("DATABASE"),
        "user": os.getenv("USER"),
        "password": os.getenv("PASSWORD"),
    }
    missing_settings = [name for name, value in settings.items() if not value]
    if missing_settings:
        raise RuntimeError("Configurações SQL ausentes: " + ", ".join(missing_settings))

    connection_string = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={settings['host']};"
        f"DATABASE={settings['database']};"
        f"UID={settings['user']};"
        f"PWD={settings['password']};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )
    return pyodbc.connect(connection_string)


def _write_bronze_csv(
    table_name: str, columns: list[str], rows: list[tuple[object, ...]]
) -> str:
    now = datetime.now(UTC)
    file_path = (
        f"{table_name}/{now:%Y}/{now:%m}/{now:%d}/{table_name}_{now:%Y%m%d_%H%M%S}.csv"
    )

    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(columns)
    writer.writerows(rows)

    connection_string = os.getenv("DATALAKE_CONNECTION_STRING")
    if not connection_string:
        raise RuntimeError("Configuração ausente: DATALAKE_CONNECTION_STRING")

    datalake = DataLakeServiceClient.from_connection_string(connection_string)
    file_client = datalake.get_file_system_client("bronze").get_file_client(file_path)
    file_client.upload_data(buffer.getvalue().encode("utf-8"), overwrite=True)

    logger.info(
        "Arquivo gravado em bronze/%s (%d linhas)",
        file_path,
        len(rows),
    )
    return file_path


def _extract_table(table_name: str) -> None:
    logger.info("Iniciando extração de itsm.%s", table_name)
    query = f"SELECT * FROM itsm.[{table_name}];"

    try:
        with _get_sql_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]

        _write_bronze_csv(table_name, columns, rows)
        logger.info("Extração de itsm.%s concluída", table_name)
    except Exception:
        logger.exception("Erro ao extrair itsm.%s", table_name)
        raise


@app.timer_trigger(
    schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_analistas(myTimer: func.TimerRequest) -> None:
    _extract_table("analista")


@app.timer_trigger(
    schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_categoria(myTimer: func.TimerRequest) -> None:
    _extract_table("categoria")


@app.timer_trigger(
    schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_chamado(myTimer: func.TimerRequest) -> None:
    _extract_table("chamado")


@app.timer_trigger(
    schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_chamado_sla(myTimer: func.TimerRequest) -> None:
    _extract_table("chamado_sla")


@app.timer_trigger(
    schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_chamado_status_historico(myTimer: func.TimerRequest) -> None:
    _extract_table("chamado_status_historico")


@app.timer_trigger(
    schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_cliente_organizacao(myTimer: func.TimerRequest) -> None:
    _extract_table("cliente_organizacao")


@app.timer_trigger(
    schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_csat_avaliacao(myTimer: func.TimerRequest) -> None:
    _extract_table("csat_avaliacao")


@app.timer_trigger(
    schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_fila(myTimer: func.TimerRequest) -> None:
    _extract_table("fila")


@app.timer_trigger(
    schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_sla(myTimer: func.TimerRequest) -> None:
    _extract_table("sla")


@app.timer_trigger(
    schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_solicitante(myTimer: func.TimerRequest) -> None:
    _extract_table("solicitante")
