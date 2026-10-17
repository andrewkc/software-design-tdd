"""Coordina una venta persistida sin conocer la tecnología de almacenamiento."""

from datetime import date

from src.repositorio_ventas import RepositorioVentas
from src.venta import registrar_venta


def registrar_venta_persistida(
    repositorio: RepositorioVentas,
    lote_id: str,
    cantidad: int,
    fecha_venta: date,
    precio_regular_centavos: int,
    promocion: dict | None,
    responsable: str,
    revision_hoy: bool = False,
) -> tuple[dict, dict]:
    return repositorio.ejecutar(
        lote_id,
        lambda lote: registrar_venta(
            lote=lote,
            cantidad=cantidad,
            fecha_venta=fecha_venta,
            precio_regular_centavos=precio_regular_centavos,
            promocion=promocion,
            responsable=responsable,
            revision_hoy=revision_hoy,
        ),
    )
