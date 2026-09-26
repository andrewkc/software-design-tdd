from datetime import date

from src.precios import precio_aplicado


FECHA_VENTA = date(2026, 9, 27)
PRECIO_REGULAR = 1000
PROMOCION_VIGENTE = {
    "precio_centavos": 800,
    "inicio": date(2026, 9, 25),
    "fin": date(2026, 9, 30),
    "activa": True,
    "aprobada": True,
}


def test_sin_promocion_aplica_precio_regular():
    assert precio_aplicado(PRECIO_REGULAR, None, FECHA_VENTA) == PRECIO_REGULAR


def test_promocion_aprobada_y_vigente_aplica_precio_promocional():
    assert (
        precio_aplicado(PRECIO_REGULAR, PROMOCION_VIGENTE, FECHA_VENTA)
        == PROMOCION_VIGENTE["precio_centavos"]
    )


def test_promocion_vencida_aplica_precio_regular():
    promocion_vencida = {
        **PROMOCION_VIGENTE,
        "fin": date(2026, 9, 26),
    }

    assert precio_aplicado(PRECIO_REGULAR, promocion_vencida, FECHA_VENTA) == PRECIO_REGULAR


def test_promocion_no_aprobada_aplica_precio_regular():
    promocion_pendiente = {**PROMOCION_VIGENTE, "aprobada": False}

    assert precio_aplicado(PRECIO_REGULAR, promocion_pendiente, FECHA_VENTA) == PRECIO_REGULAR


def test_promocion_inactiva_aplica_precio_regular():
    promocion_inactiva = {**PROMOCION_VIGENTE, "activa": False}

    assert precio_aplicado(PRECIO_REGULAR, promocion_inactiva, FECHA_VENTA) == PRECIO_REGULAR
