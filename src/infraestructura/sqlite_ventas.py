"""Adaptador SQLite; las reglas de venta viven fuera de este módulo."""

import sqlite3
from datetime import date

from src.repositorio_ventas import OperacionVenta


def crear_esquema(conexion: sqlite3.Connection) -> None:
    conexion.executescript(
        """
        CREATE TABLE IF NOT EXISTS lotes (
            id TEXT PRIMARY KEY,
            stock INTEGER NOT NULL,
            perecible INTEGER NOT NULL,
            vence TEXT,
            deteriorado INTEGER NOT NULL,
            bloqueado INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            motivo TEXT NOT NULL,
            lote_id TEXT NOT NULL REFERENCES lotes(id),
            cantidad INTEGER NOT NULL,
            responsable TEXT NOT NULL,
            precio_unitario_centavos INTEGER NOT NULL,
            total_centavos INTEGER NOT NULL
        );
        """
    )


class RepositorioVentasSQLite:
    def __init__(self, conexion: sqlite3.Connection):
        self.conexion = conexion

    def ejecutar(self, lote_id: str, operacion: OperacionVenta) -> tuple[dict, dict]:
        self.conexion.execute("BEGIN IMMEDIATE")
        try:
            fila = self.conexion.execute(
                "SELECT id, stock, perecible, vence, deteriorado, bloqueado "
                "FROM lotes WHERE id = ?",
                (lote_id,),
            ).fetchone()
            if fila is None:
                raise ValueError(f"No existe el lote {lote_id}")

            lote = {
                "id": fila[0],
                "stock": fila[1],
                "perecible": bool(fila[2]),
                "vence": date.fromisoformat(fila[3]) if fila[3] else None,
                "deteriorado": bool(fila[4]),
                "bloqueado": bool(fila[5]),
            }
            nuevo_lote, movimiento = operacion(lote)
            self.conexion.execute(
                "UPDATE lotes SET stock = ? WHERE id = ?",
                (nuevo_lote["stock"], lote_id),
            )
            self.conexion.execute(
                "INSERT INTO movimientos "
                "(motivo, lote_id, cantidad, responsable, precio_unitario_centavos, total_centavos) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    movimiento["motivo"],
                    movimiento["lote_id"],
                    movimiento["cantidad"],
                    movimiento["responsable"],
                    movimiento["precio_unitario_centavos"],
                    movimiento["total_centavos"],
                ),
            )
            self.conexion.commit()
            return nuevo_lote, movimiento
        except Exception:
            self.conexion.rollback()
            raise
