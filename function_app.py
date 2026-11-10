
import logging
import os
import re
import time
from contextlib import closing

import azure.functions as func
import pyodbc

app = func.FunctionApp()
logger = logging.getLogger(__name__)

_TABLE_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

# Ordem de carregamento respeitando as foreign keys
TABLES = [
    "fila",
    "categoria",
    "cliente_organizacao",
    "sla",
    "analista",
    "solicitante",
    "chamado",
    "chamado_sla",
    "chamado_status_historico",
    "csat_avaliacao",
]


# ============================================================
# CONEXÃO SQL SERVER
# ============================================================

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

    missing_settings = [
        name
        for name, value in settings.items()
        if not value
    ]

    if missing_settings:
        raise RuntimeError(
            "Configurações SQL ausentes: "
            + ", ".join(missing_settings)
        )

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


# ============================================================
# VALIDAÇÃO DE IDENTIFICADORES SQL
# ============================================================

def _quote_identifier(identifier: str) -> str:

    if not _TABLE_NAME_PATTERN.fullmatch(identifier):
        raise ValueError(
            f"Identificador SQL inválido: {identifier}"
        )

    return f"[{identifier}]"


# ============================================================
# METADADOS DA TABELA DE DESTINO
# ============================================================

def _get_target_metadata(
    cursor: pyodbc.Cursor,
    table_name: str,
) -> tuple[list[str], list[str]]:

    object_name = f"itsm.{table_name}"

    # Identifica as colunas da chave primária
    cursor.execute(
        """
        SELECT c.name
        FROM sys.indexes i
        INNER JOIN sys.index_columns ic
            ON i.object_id = ic.object_id
           AND i.index_id = ic.index_id
        INNER JOIN sys.columns c
            ON ic.object_id = c.object_id
           AND ic.column_id = c.column_id
        WHERE i.object_id = OBJECT_ID(?)
          AND i.is_primary_key = 1
        ORDER BY ic.key_ordinal;
        """,
        object_name,
    )

    primary_keys = [row[0] for row in cursor.fetchall()]

    if not primary_keys:
        raise RuntimeError(
            f"Tabela {object_name} não possui chave primária."
        )

    # Identifica as colunas IDENTITY
    cursor.execute(
        """
        SELECT name
        FROM sys.columns
        WHERE object_id = OBJECT_ID(?)
          AND is_identity = 1;
        """,
        object_name,
    )

    identity_columns = [
        row[0] for row in cursor.fetchall()
    ]

    return primary_keys, identity_columns


# ============================================================
# UPSERT NO BANCO DE DESTINO
# ============================================================

def _upsert_target_table(
    table_name: str,
    columns: list[str],
    rows: list[tuple[object, ...]],
) -> int:

    if not rows:
        logger.info(
            "Tabela itsm.%s sem registros para carregar",
            table_name,
        )
        return 0

    quoted_table = _quote_identifier(table_name)

    target_settings = (
        "TARGET_HOST",
        "TARGET_DATABASE",
        "TARGET_USER",
        "TARGET_PASSWORD",
    )

    with closing(_get_sql_connection(target_settings)) as connection:

        cursor = connection.cursor()

        try:
            primary_keys, identity_columns = _get_target_metadata(
                cursor,
                table_name,
            )

            missing_keys = [
                key
                for key in primary_keys
                if key not in columns
            ]

            if missing_keys:
                raise RuntimeError(
                    f"Chaves primárias ausentes em {table_name}: "
                    + ", ".join(missing_keys)
                )

            # Colunas utilizadas para atualização
            update_columns = [
                column
                for column in columns
                if column not in primary_keys
                and column not in identity_columns
            ]

            quoted_columns = ", ".join(
                _quote_identifier(column)
                for column in columns
            )

            source_columns = quoted_columns

            primary_key_condition = " AND ".join(
                (
                    f"target.{_quote_identifier(key)} = "
                    f"source.{_quote_identifier(key)}"
                )
                for key in primary_keys
            )

            update_clause = ", ".join(
                (
                    f"target.{_quote_identifier(column)} = "
                    f"source.{_quote_identifier(column)}"
                )
                for column in update_columns
            )

            insert_values = ", ".join(
                f"source.{_quote_identifier(column)}"
                for column in columns
            )

            placeholders = ", ".join(
                "?" for _ in columns
            )

            update_sql = ""

            if update_columns:
                update_sql = (
                    f"WHEN MATCHED THEN UPDATE SET {update_clause}"
                )

            merge_sql = f"""
                MERGE itsm.{quoted_table} WITH (HOLDLOCK) AS target

                USING (
                    VALUES ({placeholders})
                ) AS source ({source_columns})

                ON {primary_key_condition}

                {update_sql}

                WHEN NOT MATCHED BY TARGET THEN
                    INSERT ({quoted_columns})
                    VALUES ({insert_values});
            """

            # IDENTITY_INSERT somente quando necessário
            has_identity = any(
                column in columns
                for column in identity_columns
            )

            if has_identity:
                logger.info(
                    "Ativando IDENTITY_INSERT para itsm.%s",
                    table_name,
                )

                cursor.execute(
                    f"SET IDENTITY_INSERT itsm.{quoted_table} ON;"
                )

            logger.info(
                "Iniciando MERGE na tabela itsm.%s (%d registros)",
                table_name,
                len(rows),
            )

            cursor.fast_executemany = True
            cursor.executemany(merge_sql, rows)

            if has_identity:
                cursor.execute(
                    f"SET IDENTITY_INSERT itsm.{quoted_table} OFF;"
                )

            connection.commit()

            logger.info(
                "MERGE concluído em itsm.%s (%d registros)",
                table_name,
                len(rows),
            )

            return len(rows)

        except Exception:

            connection.rollback()

            logger.exception(
                "Erro no MERGE da tabela itsm.%s",
                table_name,
            )

            raise

        finally:
            cursor.close()


# ============================================================
# EXTRAÇÃO DO BANCO DE ORIGEM
# ============================================================

def _extract_table(table_name: str) -> int:

    if table_name not in TABLES:
        raise ValueError(
            f"Tabela não autorizada: {table_name}"
        )

    logger.info(
        "Iniciando extração de itsm.%s",
        table_name,
    )

    start_time = time.monotonic()

    quoted_table = _quote_identifier(table_name)

    query = f"SELECT * FROM itsm.{quoted_table};"

    source_settings = (
        "HOST",
        "DATABASE",
        "USER",
        "PASSWORD",
    )

    try:

        with closing(
            _get_sql_connection(source_settings)
        ) as connection:

            cursor = connection.cursor()

            try:
                cursor.execute(query)

                rows = cursor.fetchall()

                columns = [
                    column[0]
                    for column in cursor.description
                ]

            finally:
                cursor.close()

        logger.info(
            "Extraídos %d registros de itsm.%s",
            len(rows),
            table_name,
        )

        loaded_rows = _upsert_target_table(
            table_name,
            columns,
            rows,
        )

        elapsed_time = time.monotonic() - start_time

        logger.info(
            "Tabela itsm.%s finalizada. "
            "Registros: %d | Tempo: %.2f segundos",
            table_name,
            loaded_rows,
            elapsed_time,
        )

        return loaded_rows

    except Exception:

        logger.exception(
            "Falha na sincronização de itsm.%s",
            table_name,
        )

        raise


# ============================================================
# TIMER ÚNICO - SINCRONIZAÇÃO ITSM
# ============================================================

@app.timer_trigger(
    schedule="0 0 0 * * *",
    arg_name="myTimer",
    run_on_startup=False,
    use_monitor=True,
)
def extract_all_tables(myTimer: func.TimerRequest) -> None:

    start_time = time.monotonic()

    total_records = 0
    completed_tables = 0

    logger.info(
        "============================================"
    )
    logger.info(
        "INICIANDO SINCRONIZAÇÃO COMPLETA DO ITSM"
    )
    logger.info(
        "Total de tabelas: %d",
        len(TABLES),
    )
    logger.info(
        "============================================"
    )

    if myTimer.past_due:
        logger.warning(
            "Execução do timer iniciada com atraso."
        )

    for index, table_name in enumerate(TABLES, start=1):

        logger.info(
            "--------------------------------------------"
        )
        logger.info(
            "Processando tabela %d/%d: itsm.%s",
            index,
            len(TABLES),
            table_name,
        )

        try:

            loaded_rows = _extract_table(table_name)

            total_records += loaded_rows
            completed_tables += 1

            logger.info(
                "SUCESSO: itsm.%s | %d registros",
                table_name,
                loaded_rows,
            )

        except Exception:

            logger.exception(
                "SINCRONIZAÇÃO INTERROMPIDA "
                "NA TABELA itsm.%s",
                table_name,
            )

            logger.error(
                "Tabelas concluídas antes da falha: %d/%d",
                completed_tables,
                len(TABLES),
            )

            # Interrompe para não violar dependências
            raise

    elapsed_time = time.monotonic() - start_time

    logger.info(
        "============================================"
    )
    logger.info(
        "SINCRONIZAÇÃO ITSM CONCLUÍDA COM SUCESSO"
    )
    logger.info(
        "Tabelas processadas: %d",
        completed_tables,
    )
    logger.info(
        "Total de registros processados: %d",
        total_records,
    )
    logger.info(
        "Tempo total: %.2f segundos",
        elapsed_time,
    )
    logger.info(
        "============================================"
    )
