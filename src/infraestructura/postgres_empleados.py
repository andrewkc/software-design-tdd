"""Persistencia PostgreSQL para CU-03."""

import psycopg

from src.empleados import validar_jefe
from src.repositorio_empleados import OperacionEmpleado


CAMPOS_CUENTA = ("id", "nombre", "correo", "rol", "activo", "bodega_id")


def _cuenta(fila: tuple | None) -> dict | None:
    return dict(zip(CAMPOS_CUENTA, fila)) if fila is not None else None


def _obtener_cuenta(
    conexion: psycopg.Connection, cuenta_id: str, bloquear: bool = False
) -> dict | None:
    consulta = (
        "SELECT id, nombre, correo, rol, activo, bodega_id "
        "FROM cuentas WHERE id = %s"
    )
    if bloquear:
        consulta += " FOR UPDATE"
    return _cuenta(conexion.execute(consulta, (cuenta_id,)).fetchone())


class RepositorioEmpleadosPostgres:
    def __init__(self, conexion: psycopg.Connection):
        if not conexion.autocommit:
            raise ValueError("La conexión PostgreSQL debe usar autocommit=True")
        self.conexion = conexion

    def ejecutar(
        self, jefe_id: str, empleado_id: str, operacion: OperacionEmpleado
    ) -> dict:
        with self.conexion.transaction():
            jefe = _obtener_cuenta(self.conexion, jefe_id, bloquear=True)
            if jefe is None:
                raise ValueError("La cuenta del jefe no existe")
            validar_jefe(jefe)

            empleado = _obtener_cuenta(self.conexion, empleado_id, bloquear=True)
            if empleado is None:
                raise ValueError("La cuenta del empleado no existe")

            actualizado = operacion(jefe, empleado)
            self.conexion.execute(
                "UPDATE cuentas SET bodega_id = %s WHERE id = %s",
                (actualizado["bodega_id"], empleado_id),
            )
        return actualizado

    def listar(self, jefe_id: str) -> list[dict]:
        with self.conexion.transaction():
            jefe = _obtener_cuenta(self.conexion, jefe_id, bloquear=True)
            if jefe is None:
                raise ValueError("La cuenta del jefe no existe")
            validar_jefe(jefe)
            filas = self.conexion.execute(
                "SELECT id, nombre, correo, rol, activo, bodega_id "
                "FROM cuentas WHERE bodega_id = %s AND rol = 'empleado' "
                "ORDER BY nombre, id",
                (jefe["bodega_id"],),
            ).fetchall()
        return [_cuenta(fila) for fila in filas]
