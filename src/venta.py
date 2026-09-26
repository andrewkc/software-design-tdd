from datetime import date

from src.movimientos import crear_movimiento
from src.precios import precio_aplicado
from src.validacion import validar_venta


def registrar_venta(
    lote: dict,
    cantidad: int,
    fecha_venta: date,
    precio_regular_centavos: int,
    promocion: dict | None,
    responsable: str,
    revision_hoy: bool = False,
) -> tuple[dict, dict]:
    validar_venta(
        lote=lote,
        cantidad=cantidad,
        fecha_venta=fecha_venta,
        revision_hoy=revision_hoy,
    )
    precio_unitario_centavos = precio_aplicado(
        precio_regular_centavos=precio_regular_centavos,
        promocion=promocion,
        fecha_venta=fecha_venta,
    )
    return crear_movimiento(
        lote=lote,
        cantidad=cantidad,
        precio_unitario_centavos=precio_unitario_centavos,
        responsable=responsable,
    )