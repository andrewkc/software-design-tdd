from datetime import date
import sqlite3

import pytest

from src.infraestructura.sqlite_ventas import RepositorioVentasSQLite, crear_esquema
from src.venta_aplicacion import registrar_venta_persistida


FECHA_VENTA = date(2026, 9, 27)


def preparar_conexion():
    conexion = sqlite3.connect(":memory:")
    crear_esquema(conexion)
    conexion.execute(
        "INSERT INTO lotes VALUES (?, ?, ?, ?, ?, ?)",
        ("L1", 5, 1, "2026-10-01", 0, 0),
    )
    conexion.commit()
    return conexion


def test_aplicacion_usa_el_contrato_sin_conocer_sqlite():
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


def test_sqlite_guarda_lote_y_movimiento_en_una_venta():
    with preparar_conexion() as conexion:
        lote, movimiento = registrar_venta_persistida(
            RepositorioVentasSQLite(conexion), "L1", 2, FECHA_VENTA, 1000, None, "Ana"
        )

        assert lote["stock"] == 3
        assert movimiento["lote_id"] == "L1"
        assert conexion.execute("SELECT stock FROM lotes WHERE id = 'L1'").fetchone() == (3,)
        assert conexion.execute(
            "SELECT cantidad, total_centavos FROM movimientos"
        ).fetchall() == [(2, 2000)]


def test_venta_rechazada_no_guarda_cambios():
    with preparar_conexion() as conexion:
        with pytest.raises(ValueError, match="stock"):
            registrar_venta_persistida(
                RepositorioVentasSQLite(conexion),
                "L1", 6, FECHA_VENTA, 1000, None, "Ana",
            )

        assert conexion.execute("SELECT stock FROM lotes WHERE id = 'L1'").fetchone() == (5,)
        assert conexion.execute("SELECT COUNT(*) FROM movimientos").fetchone() == (0,)


def test_error_al_guardar_movimiento_revierte_el_stock():
    with preparar_conexion() as conexion:
        conexion.execute(
            "CREATE TRIGGER impedir_movimiento BEFORE INSERT ON movimientos "
            "BEGIN SELECT RAISE(ABORT, 'error al guardar'); END"
        )
        conexion.commit()

        with pytest.raises(sqlite3.IntegrityError, match="error al guardar"):
            registrar_venta_persistida(
                RepositorioVentasSQLite(conexion),
                "L1", 2, FECHA_VENTA, 1000, None, "Ana",
            )

        assert conexion.execute("SELECT stock FROM lotes WHERE id = 'L1'").fetchone() == (5,)
        assert conexion.execute("SELECT COUNT(*) FROM movimientos").fetchone() == (0,)
