from datetime import date, timedelta

import pytest

from src.validacion import estado_lote, validar_venta

HOY = date(2026, 10, 1)


def lote(
    stock: int = 5,
    perecible: bool = True,
    vence: date | None = None,
    deteriorado: bool = False,
    bloqueado: bool = False,
) -> dict:
    return {
        "id": "L1",
        "stock": stock,
        "perecible": perecible,
        "vence": vence,
        "deteriorado": deteriorado,
        "bloqueado": bloqueado,
    }


def lote_vendible(stock: int = 5) -> dict:
    return lote(stock=stock, vence=HOY + timedelta(days=10))


def test_fecha_lejana_es_normal_y_muestra_la_fecha():
    estado, texto = estado_lote(lote(vence=HOY + timedelta(days=10)), HOY)

    assert estado == "NORMAL"
    assert texto == "Vence el 11/10/2026"


def test_tres_dias_antes_es_proximo():
    estado, texto = estado_lote(lote(vence=HOY + timedelta(days=3)), HOY)

    assert estado == "PROXIMO"
    assert texto == "Vence en 3 días: revisar lote"


def test_un_dia_antes_es_proximo():
    estado, texto = estado_lote(lote(vence=HOY + timedelta(days=1)), HOY)

    assert estado == "PROXIMO"
    assert texto == "Vence en 1 días: revisar lote"


def test_vence_hoy():
    estado, texto = estado_lote(lote(vence=HOY), HOY)

    assert estado == "HOY"
    assert texto == "Vence hoy: revisar antes de vender"


def test_fecha_pasada_es_vencido():
    estado, texto = estado_lote(lote(vence=HOY - timedelta(days=1)), HOY)

    assert estado == "VENCIDO"
    assert texto == "Vencido: retirar de la venta"


def test_lote_deteriorado_queda_bloqueado():
    estado, texto = estado_lote(
        lote(vence=HOY + timedelta(days=10), deteriorado=True), HOY
    )

    assert estado == "BLOQUEADO"
    assert texto == "En observación: revisar y retirar de la venta"


def test_lote_marcado_bloqueado_queda_bloqueado():
    estado, texto = estado_lote(
        lote(vence=HOY + timedelta(days=10), bloqueado=True), HOY
    )

    assert estado == "BLOQUEADO"
    assert texto == "En observación: revisar y retirar de la venta"


def test_el_bloqueo_tiene_prioridad_sobre_el_vencimiento():
    estado, _ = estado_lote(
        lote(vence=HOY - timedelta(days=5), deteriorado=True), HOY
    )

    assert estado == "BLOQUEADO"


def test_perecible_sin_fecha_registrada():
    estado, texto = estado_lote(lote(perecible=True, vence=None), HOY)

    assert estado == "SIN_FECHA"
    assert texto == "Fecha sin verificar: revisar lote"


def test_producto_sin_fecha_aplicable_es_normal():
    estado, texto = estado_lote(lote(perecible=False, vence=None), HOY)

    assert estado == "NORMAL"
    assert texto == "Fecha no aplicable"


def test_venta_valida_no_lanza_error():
    assert validar_venta(lote_vendible(), 2, HOY) is None


def test_cantidad_cero_es_rechazada():
    with pytest.raises(ValueError, match="cantidad"):
        validar_venta(lote_vendible(), 0, HOY)


def test_cantidad_negativa_es_rechazada():
    with pytest.raises(ValueError, match="cantidad"):
        validar_venta(lote_vendible(), -1, HOY)


def test_cantidad_mayor_al_stock_es_rechazada():
    with pytest.raises(ValueError, match="stock"):
        validar_venta(lote_vendible(stock=5), 6, HOY)


def test_cantidad_igual_al_stock_es_aceptada():
    assert validar_venta(lote_vendible(stock=5), 5, HOY) is None


def test_lote_bloqueado_no_se_puede_vender():
    bloqueado = lote(vence=HOY + timedelta(days=10), bloqueado=True)

    with pytest.raises(ValueError, match="observación"):
        validar_venta(bloqueado, 1, HOY)


def test_lote_deteriorado_no_se_puede_vender():
    deteriorado = lote(vence=HOY + timedelta(days=10), deteriorado=True)

    with pytest.raises(ValueError, match="observación"):
        validar_venta(deteriorado, 1, HOY)


def test_lote_vencido_no_se_puede_vender():
    vencido = lote(vence=HOY - timedelta(days=1))

    with pytest.raises(ValueError, match="Vencido"):
        validar_venta(vencido, 1, HOY)


def test_perecible_sin_fecha_no_se_puede_vender():
    sin_fecha = lote(perecible=True, vence=None)

    with pytest.raises(ValueError, match="Fecha sin verificar"):
        validar_venta(sin_fecha, 1, HOY)


def test_vence_hoy_sin_revision_es_rechazado():
    with pytest.raises(ValueError, match="revisión"):
        validar_venta(lote(vence=HOY), 1, HOY)


def test_vence_hoy_con_revision_es_aceptado():
    assert validar_venta(lote(vence=HOY), 1, HOY, revision_hoy=True) is None


def test_la_revision_no_habilita_un_lote_deteriorado():
    deteriorado = lote(vence=HOY, deteriorado=True)

    with pytest.raises(ValueError, match="observación"):
        validar_venta(deteriorado, 1, HOY, revision_hoy=True)


def test_lote_proximo_a_vencer_se_puede_vender():
    proximo = lote(vence=HOY + timedelta(days=2))

    assert validar_venta(proximo, 1, HOY) is None
