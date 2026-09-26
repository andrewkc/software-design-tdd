from datetime import date


def precio_aplicado(
    precio_regular_centavos: int,
    promocion: dict | None,
    fecha_venta: date,
) -> int:
    """Devuelve el precio promocional vigente o el precio regular, en centavos."""
    if (
        promocion is not None
        and promocion["aprobada"]
        and promocion["activa"]
        and promocion["inicio"] <= fecha_venta <= promocion["fin"]
    ):
        return promocion["precio_centavos"]

    return precio_regular_centavos
