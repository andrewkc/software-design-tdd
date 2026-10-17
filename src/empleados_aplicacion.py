"""Casos de uso de empleados que dependen del contrato de repositorio."""

from src.empleados import incorporar, retirar
from src.repositorio_empleados import RepositorioEmpleados


def incorporar_empleado(
    repositorio: RepositorioEmpleados, jefe_id: str, empleado_id: str
) -> dict:
    return repositorio.ejecutar(jefe_id, empleado_id, incorporar)


def retirar_empleado(
    repositorio: RepositorioEmpleados, jefe_id: str, empleado_id: str
) -> dict:
    return repositorio.ejecutar(jefe_id, empleado_id, retirar)


def listar_empleados(repositorio: RepositorioEmpleados, jefe_id: str) -> list[dict]:
    return repositorio.listar(jefe_id)
