"""Contrato de persistencia usado por la aplicación, sin detalles de base de datos."""

from typing import Callable, Protocol


OperacionVenta = Callable[[dict], tuple[dict, dict]]


class RepositorioVentas(Protocol):
    def ejecutar(self, lote_id: str, operacion: OperacionVenta) -> tuple[dict, dict]:
        """Aplica la operación y guarda lote y movimiento en una transacción."""
