from datetime import date


def _promocion_vigente(promocion: dict, fecha_venta: date) -> bool:
    return (
        promocion["aprobada"]
        and promocion["activa"]
        and promocion["inicio"] <= fecha_venta <= promocion["fin"]
    )


def precio_aplicado(
    precio_regular_centavos: int,
    promocion: dict | None,
    fecha_venta: date,
) -> int:
    
    if promocion is not None and _promocion_vigente(promocion, fecha_venta):
        return promocion["precio_centavos"]

    return precio_regular_centavos
