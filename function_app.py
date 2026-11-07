import logging
import os
import re

import azure.functions as func
import pyodbc

app = func.FunctionApp()
logger = logging.getLogger(__name__)

_TABLE_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_SOURCE_TABLES = {
    "analista",
    "categoria",
    "chamado",
    "chamado_sla",
    "chamado_status_historico",
    "cliente_organizacao",
    "csat_avaliacao",
    "fila",
    "sla",
    "solicitante",
}


def _get_sql_connection(
    setting_names: tuple[str, str, str, str],
) -> pyodbc.Connection:
    host_name, database_name, user_name, password_name = setting_names
    settings = {
        "host": os.getenv(host_name),
        "database": os.getenv(database_name),
        "user": os.getenv(user_name),
        "password": os.getenv(password_name),
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


def _quote_identifier(identifier: str) -> str:
    if not _TABLE_NAME_PATTERN.fullmatch(identifier):
        raise ValueError(f"Identificador SQL inválido: {identifier}")
    return f"[{identifier}]"


def _upsert_target_table(
    table_name: str, columns: list[str], rows: list[tuple[object, ...]]
) -> int:
    if not rows:
        logger.info("Tabela itsm.%s sem registros para carregar", table_name)
        return 0

    quoted_table = _quote_identifier(table_name)
    quoted_columns = ", ".join(_quote_identifier(column) for column in columns)
    source_columns = ", ".join(_quote_identifier(column) for column in columns)
    primary_key = _quote_identifier(columns[0])
    update_columns = columns[1:]
    update_clause = ", ".join(
        f"target.{_quote_identifier(column)} = source.{_quote_identifier(column)}"
        for column in update_columns
    )
    insert_values = ", ".join(
        f"source.{_quote_identifier(column)}" for column in columns
    )
    update_sql = (
        f"WHEN MATCHED THEN UPDATE SET {update_clause}" if update_clause else ""
    )
    merge_sql = (
        f"MERGE itsm.{quoted_table} AS target "
        f"USING (VALUES ({', '.join('?' for _ in columns)})) "
        f"AS source ({source_columns}) "
        f"ON target.{primary_key} = source.{primary_key} "
        f"{update_sql} "
        f"WHEN NOT MATCHED BY TARGET THEN "
        f"INSERT ({quoted_columns}) VALUES ({insert_values});"
    )

    with _get_sql_connection(
        ("TARGET_HOST", "TARGET_DATABASE", "TARGET_USER", "TARGET_PASSWORD")
    ) as connection:
        cursor = connection.cursor()
        cursor.execute(f"SET IDENTITY_INSERT itsm.{quoted_table} ON;")
        try:
            cursor.fast_executemany = True
            cursor.executemany(merge_sql, rows)
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.execute(f"SET IDENTITY_INSERT itsm.{quoted_table} OFF;")
            connection.commit()

    logger.info("Tabela itsm.%s carregada (%d linhas)", table_name, len(rows))
    return len(rows)


def _extract_table(table_name: str) -> None:
    if table_name not in _SOURCE_TABLES:
        raise ValueError(f"Tabela não autorizada: {table_name}")

    logger.info("Iniciando extração de itsm.%s", table_name)
    query = f"SELECT * FROM itsm.[{table_name}];"

    try:
        with _get_sql_connection(
            ("HOST", "DATABASE", "USER", "PASSWORD")
        ) as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]

        _upsert_target_table(table_name, columns, rows)
        logger.info("Extração de itsm.%s concluída", table_name)
    except Exception:
        logger.exception("Erro ao extrair itsm.%s", table_name)
        raise


@app.timer_trigger(
    schedule="0 0 0 * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_analistas(myTimer: func.TimerRequest) -> None:
    _extract_table("analista")


@app.timer_trigger(
    schedule="0 0 0 * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_categoria(myTimer: func.TimerRequest) -> None:
    _extract_table("categoria")


@app.timer_trigger(
    schedule="0 0 0 * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_chamado(myTimer: func.TimerRequest) -> None:
    _extract_table("chamado")


@app.timer_trigger(
    schedule="0 0 0 * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_chamado_sla(myTimer: func.TimerRequest) -> None:
    _extract_table("chamado_sla")


@app.timer_trigger(
    schedule="0 0 0 * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_chamado_status_historico(myTimer: func.TimerRequest) -> None:
    _extract_table("chamado_status_historico")


@app.timer_trigger(
    schedule="0 0 0 * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_cliente_organizacao(myTimer: func.TimerRequest) -> None:
    _extract_table("cliente_organizacao")


@app.timer_trigger(
    schedule="0 0 0 * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_csat_avaliacao(myTimer: func.TimerRequest) -> None:
    _extract_table("csat_avaliacao")


@app.timer_trigger(
    schedule="0 0 0 * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_fila(myTimer: func.TimerRequest) -> None:
    _extract_table("fila")


@app.timer_trigger(
    schedule="0 0 0 * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_sla(myTimer: func.TimerRequest) -> None:
    _extract_table("sla")


@app.timer_trigger(
    schedule="0 0 0 * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_solicitante(myTimer: func.TimerRequest) -> None:
    _extract_table("solicitante")
