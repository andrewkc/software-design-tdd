import os
from pathlib import Path
from uuid import uuid4

import psycopg
from psycopg import sql
import pytest

from src.empleados import incorporar, retirar
from src.empleados_aplicacion import (
    incorporar_empleado,
    listar_empleados,
    retirar_empleado,
)
from src.infraestructura.postgres_empleados import RepositorioEmpleadosPostgres


RAIZ = Path(__file__).resolve().parents[1]


def cuenta(identificador, rol, bodega_id=None, activo=True):
    return {
        "id": identificador,
        "nombre": identificador,
        "correo": f"{identificador}@ejemplo.com",
        "rol": rol,
        "activo": activo,
        "bodega_id": bodega_id,
    }


def test_incorporar_asigna_bodega_sin_modificar_la_cuenta_original():
    jefe = cuenta("jefe_1", "jefe", "B1")
    empleado = cuenta("empleado_1", "empleado")

    resultado = incorporar(jefe, empleado)

    assert resultado["bodega_id"] == "B1"
    assert resultado["activo"] is True
    assert empleado["bodega_id"] is None


@pytest.mark.parametrize(
    "jefe",
    [
        cuenta("admin", "administrador"),
        cuenta("jefe_inactivo", "jefe", "B1", activo=False),
        cuenta("jefe_sin_bodega", "jefe"),
    ],
)
def test_solo_un_jefe_activo_de_bodega_puede_gestionar_empleados(jefe):
    with pytest.raises(PermissionError):
        incorporar(jefe, cuenta("empleado_1", "empleado"))


@pytest.mark.parametrize(
    "empleado",
    [
        cuenta("empleado_inactivo", "empleado", activo=False),
        cuenta("otro_jefe", "jefe", "B2"),
        cuenta("admin", "administrador"),
    ],
)
def test_incorporar_requiere_una_cuenta_activa_de_empleado(empleado):
    with pytest.raises(ValueError):
        incorporar(cuenta("jefe_1", "jefe", "B1"), empleado)


@pytest.mark.parametrize("bodega_id", ["B1", "B2"])
def test_no_se_incorpora_una_cuenta_ya_asignada(bodega_id):
    with pytest.raises(ValueError):
        incorporar(
            cuenta("jefe_1", "jefe", "B1"),
            cuenta("empleado_1", "empleado", bodega_id),
        )


def test_retirar_desasigna_sin_desactivar_la_cuenta():
    empleado = cuenta("empleado_1", "empleado", "B1", activo=False)

    resultado = retirar(cuenta("jefe_1", "jefe", "B1"), empleado)

    assert resultado["bodega_id"] is None
    assert resultado["activo"] is False
    assert empleado["bodega_id"] == "B1"


@pytest.mark.parametrize("bodega_id", [None, "B2"])
def test_no_se_retira_un_empleado_fuera_de_la_bodega(bodega_id):
    with pytest.raises(ValueError):
        retirar(
            cuenta("jefe_1", "jefe", "B1"),
            cuenta("empleado_1", "empleado", bodega_id),
        )


@pytest.fixture
def conexion_pg():
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Configura TEST_DATABASE_URL para las pruebas PostgreSQL")

    esquema = f"test_empleados_{uuid4().hex}"
    with psycopg.connect(url, autocommit=True) as conexion:
        conexion.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(esquema)))
        try:
            conexion.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(esquema)))
            for archivo in ("schema.sql", "002_cu03.sql"):
                for sentencia in (RAIZ / "db" / archivo).read_text(encoding="utf-8").split(";"):
                    if sentencia.strip():
                        conexion.execute(sentencia)
            conexion.execute("INSERT INTO bodegas (id, nombre) VALUES ('B1', 'Bodega 1'), ('B2', 'Bodega 2')")
            conexion.execute(
                "INSERT INTO cuentas (id, nombre, correo, rol, activo, bodega_id) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                ("jefe_1", "Jefe Uno", "jefe1@ejemplo.com", "jefe", True, "B1"),
            )
            conexion.execute(
                "INSERT INTO cuentas (id, nombre, correo, rol, activo, bodega_id) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                ("jefe_2", "Jefe Dos", "jefe2@ejemplo.com", "jefe", True, "B2"),
            )
            conexion.execute(
                "INSERT INTO cuentas (id, nombre, correo, rol, activo, bodega_id) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                ("empleado_1", "Empleado Uno", "empleado1@ejemplo.com", "empleado", True, None),
            )
            yield conexion
        finally:
            conexion.execute("SET search_path TO public")
            conexion.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(esquema)))


def test_postgres_incorporar_listar_y_retirar_sin_borrar_movimientos(conexion_pg):
    repositorio = RepositorioEmpleadosPostgres(conexion_pg)
    incorporado = incorporar_empleado(repositorio, "jefe_1", "empleado_1")

    assert incorporado["bodega_id"] == "B1"
    assert [empleado["id"] for empleado in listar_empleados(repositorio, "jefe_1")] == ["empleado_1"]
    assert listar_empleados(repositorio, "jefe_2") == []

    conexion_pg.execute(
        "INSERT INTO lotes (id, stock, perecible, vence, deteriorado, bloqueado) "
        "VALUES ('L1', 5, false, NULL, false, false)"
    )
    conexion_pg.execute(
        "INSERT INTO movimientos "
        "(motivo, lote_id, cantidad, responsable, precio_unitario_centavos, total_centavos) "
        "VALUES ('venta', 'L1', 1, 'empleado_1', 100, 100)"
    )

    retirado = retirar_empleado(repositorio, "jefe_1", "empleado_1")

    assert retirado["bodega_id"] is None
    assert listar_empleados(repositorio, "jefe_1") == []
    assert conexion_pg.execute("SELECT COUNT(*) FROM movimientos").fetchone() == (1,)
    assert conexion_pg.execute("SELECT activo FROM cuentas WHERE id = 'empleado_1'").fetchone() == (True,)


def test_postgres_rechaza_asignacion_ajena_sin_cambiar_la_cuenta(conexion_pg):
    repositorio = RepositorioEmpleadosPostgres(conexion_pg)
    incorporar_empleado(repositorio, "jefe_1", "empleado_1")

    with pytest.raises(ValueError):
        incorporar_empleado(repositorio, "jefe_2", "empleado_1")
    with pytest.raises(ValueError):
        retirar_empleado(repositorio, "jefe_2", "empleado_1")

    assert conexion_pg.execute(
        "SELECT bodega_id FROM cuentas WHERE id = 'empleado_1'"
    ).fetchone() == ("B1",)


def test_postgres_permite_reasignar_despues_del_retiro(conexion_pg):
    repositorio = RepositorioEmpleadosPostgres(conexion_pg)
    incorporar_empleado(repositorio, "jefe_1", "empleado_1")
    retirar_empleado(repositorio, "jefe_1", "empleado_1")

    resultado = incorporar_empleado(repositorio, "jefe_2", "empleado_1")

    assert resultado["bodega_id"] == "B2"
    assert listar_empleados(repositorio, "jefe_1") == []
    assert [empleado["id"] for empleado in listar_empleados(repositorio, "jefe_2")] == ["empleado_1"]


def test_postgres_no_incorpora_una_cuenta_inactiva(conexion_pg):
    repositorio = RepositorioEmpleadosPostgres(conexion_pg)
    conexion_pg.execute("UPDATE cuentas SET activo = false WHERE id = 'empleado_1'")

    with pytest.raises(ValueError):
        incorporar_empleado(repositorio, "jefe_1", "empleado_1")

    assert conexion_pg.execute(
        "SELECT bodega_id FROM cuentas WHERE id = 'empleado_1'"
    ).fetchone() == (None,)


def test_postgres_rechaza_jefe_inexistente_o_sin_permiso(conexion_pg):
    repositorio = RepositorioEmpleadosPostgres(conexion_pg)
    conexion_pg.execute(
        "INSERT INTO cuentas (id, nombre, correo, rol, activo, bodega_id) "
        "VALUES ('admin', 'Admin', 'admin@ejemplo.com', 'administrador', true, NULL)"
    )

    with pytest.raises(PermissionError):
        incorporar_empleado(repositorio, "admin", "empleado_1")
    with pytest.raises(ValueError):
        listar_empleados(repositorio, "inexistente")
    conexion_pg.execute("UPDATE cuentas SET activo = false WHERE id = 'jefe_1'")
    with pytest.raises(PermissionError):
        incorporar_empleado(repositorio, "jefe_1", "empleado_1")
    with pytest.raises(PermissionError):
        listar_empleados(repositorio, "jefe_1")

    assert conexion_pg.execute(
        "SELECT bodega_id FROM cuentas WHERE id = 'empleado_1'"
    ).fetchone() == (None,)
