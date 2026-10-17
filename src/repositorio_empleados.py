"""Contrato de CU-03 usado por la aplicación, sin detalles de almacenamiento."""

from typing import Callable, Protocol


OperacionEmpleado = Callable[[dict, dict], dict]


class RepositorioEmpleados(Protocol):
    def ejecutar(
        self, jefe_id: str, empleado_id: str, operacion: OperacionEmpleado
    ) -> dict:
        """Valida y actualiza la asignación en una transacción."""

    def listar(self, jefe_id: str) -> list[dict]:
        """Devuelve empleados asignados a la bodega de un jefe autorizado."""
