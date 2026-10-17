from datetime import date
import os
from pathlib import Path
from uuid import uuid4

import psycopg
from psycopg import sql
import pytest

from src.infraestructura.postgres_ventas import RepositorioVentasPostgres
from src.venta_aplicacion import registrar_venta_persistida


FECHA_VENTA = date(2026, 9, 27)
ESQUEMA_SQL = Path(__file__).resolve().parents[1] / "db" / "schema.sql"


@pytest.fixture
def conexion_pg():
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Configura TEST_DATABASE_URL para las pruebas PostgreSQL")

    esquema = f"test_ventas_{uuid4().hex}"
    with psycopg.connect(url, autocommit=True) as conexion:
        conexion.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(esquema)))
        try:
            conexion.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(esquema)))
            for sentencia in ESQUEMA_SQL.read_text(encoding="utf-8").split(";"):
                if sentencia.strip():
                    conexion.execute(sentencia)
            conexion.execute(
                "INSERT INTO lotes (id, stock, perecible, vence, deteriorado, bloqueado) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                ("L1", 5, True, date(2026, 10, 1), False, False),
            )
            yield conexion
        finally:
            conexion.execute("SET search_path TO public")
            conexion.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(esquema)))


def test_aplicacion_usa_el_contrato_sin_conocer_postgres():
    class RepositorioFalso:
        def ejecutar(self, lote_id, operacion):
            assert lote_id == "L1"
            return operacion(
                {
                    "id": lote_id,
                    "stock": 5,
                    "perecible": True,
                    "vence": date(2026, 10, 1),
                    "deteriorado": False,
                    "bloqueado": False,
                }
            )

    lote, movimiento = registrar_venta_persistida(
        RepositorioFalso(), "L1", 2, FECHA_VENTA, 1000, None, "Ana"
    )

    assert lote["stock"] == 3
    assert movimiento["total_centavos"] == 2000


def test_postgres_guarda_lote_y_movimiento_en_una_venta(conexion_pg):
    lote, movimiento = registrar_venta_persistida(
        RepositorioVentasPostgres(conexion_pg), "L1", 2, FECHA_VENTA, 1000, None, "Ana"
    )

    assert lote["stock"] == 3
    assert movimiento["lote_id"] == "L1"
    assert conexion_pg.execute("SELECT stock FROM lotes WHERE id = 'L1'").fetchone() == (3,)
    assert conexion_pg.execute(
        "SELECT cantidad, total_centavos FROM movimientos"
    ).fetchall() == [(2, 2000)]


def test_venta_rechazada_no_guarda_cambios(conexion_pg):
    with pytest.raises(ValueError, match="stock"):
        registrar_venta_persistida(
            RepositorioVentasPostgres(conexion_pg),
            "L1", 6, FECHA_VENTA, 1000, None, "Ana",
        )

    assert conexion_pg.execute("SELECT stock FROM lotes WHERE id = 'L1'").fetchone() == (5,)
    assert conexion_pg.execute("SELECT COUNT(*) FROM movimientos").fetchone() == (0,)


def test_error_al_guardar_movimiento_revierte_el_stock(conexion_pg):
    conexion_pg.execute(
        "ALTER TABLE movimientos ADD CONSTRAINT responsable_valido "
        "CHECK (responsable <> 'fallar')"
    )

    with pytest.raises(psycopg.errors.CheckViolation):
        registrar_venta_persistida(
            RepositorioVentasPostgres(conexion_pg),
            "L1", 2, FECHA_VENTA, 1000, None, "fallar",
        )

    assert conexion_pg.execute("SELECT stock FROM lotes WHERE id = 'L1'").fetchone() == (5,)
    assert conexion_pg.execute("SELECT COUNT(*) FROM movimientos").fetchone() == (0,)
