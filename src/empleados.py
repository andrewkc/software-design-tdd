"""Reglas de CU-03 independientes de la base de datos."""


def validar_jefe(jefe: dict) -> None:
    if jefe["rol"] != "jefe" or not jefe["activo"] or jefe["bodega_id"] is None:
        raise PermissionError("Solo un jefe activo con bodega puede gestionar empleados")


def incorporar(jefe: dict, empleado: dict) -> dict:
    validar_jefe(jefe)
    if empleado["rol"] != "empleado" or not empleado["activo"]:
        raise ValueError("La cuenta debe ser de un empleado activo")
    if empleado["bodega_id"] is not None:
        raise ValueError("El empleado ya está asignado a una bodega")
    return {**empleado, "bodega_id": jefe["bodega_id"]}


def retirar(jefe: dict, empleado: dict) -> dict:
    validar_jefe(jefe)
    if empleado["rol"] != "empleado":
        raise ValueError("La cuenta no corresponde a un empleado")
    if empleado["bodega_id"] != jefe["bodega_id"]:
        raise ValueError("El empleado no pertenece a la bodega del jefe")
    return {**empleado, "bodega_id": None}
