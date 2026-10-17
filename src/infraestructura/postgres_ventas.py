"""Adaptador PostgreSQL; las reglas de venta viven fuera de este módulo."""

import psycopg

from src.repositorio_ventas import OperacionVenta


class RepositorioVentasPostgres:
    def __init__(self, conexion: psycopg.Connection):
        if not conexion.autocommit:
            raise ValueError("La conexión PostgreSQL debe usar autocommit=True")
        self.conexion = conexion

    def ejecutar(self, lote_id: str, operacion: OperacionVenta) -> tuple[dict, dict]:
        with self.conexion.transaction():
            fila = self.conexion.execute(
                "SELECT id, stock, perecible, vence, deteriorado, bloqueado "
                "FROM lotes WHERE id = %s FOR UPDATE",
                (lote_id,),
            ).fetchone()
            if fila is None:
                raise ValueError(f"No existe el lote {lote_id}")

            lote = dict(
                zip(
                    ("id", "stock", "perecible", "vence", "deteriorado", "bloqueado"),
                    fila,
                )
            )
            nuevo_lote, movimiento = operacion(lote)
            self.conexion.execute(
                "UPDATE lotes SET stock = %s WHERE id = %s",
                (nuevo_lote["stock"], lote_id),
            )
            self.conexion.execute(
                "INSERT INTO movimientos "
                "(motivo, lote_id, cantidad, responsable, precio_unitario_centavos, total_centavos) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (
                    movimiento["motivo"],
                    movimiento["lote_id"],
                    movimiento["cantidad"],
                    movimiento["responsable"],
                    movimiento["precio_unitario_centavos"],
                    movimiento["total_centavos"],
                ),
            )
        return nuevo_lote, movimiento
