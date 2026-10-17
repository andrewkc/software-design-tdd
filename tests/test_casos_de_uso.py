import pytest

from tests.escenarios_cu05 import (
    ESCENARIOS,
    PRECIO_REGULAR,
    QUE_PROCEDEN,
    QUE_SE_RECHAZAN,
    RESPONSABLE,
    ejecutar,
    lote,
    vender_hasta_agotar,
)


def ids(escenarios):
    return [escenario.id for escenario in escenarios]


@pytest.mark.parametrize("escenario", QUE_PROCEDEN, ids=ids(QUE_PROCEDEN))
def test_la_venta_procede_con_el_stock_y_el_precio_esperados(escenario):
    resultado = ejecutar(escenario)

    assert resultado.procede, resultado.motivo
    assert resultado.lote["stock"] == escenario.stock_final
    assert resultado.movimiento["precio_unitario_centavos"] == escenario.precio_unitario
    assert resultado.movimiento["total_centavos"] == (
        escenario.cantidad * escenario.precio_unitario
    )


@pytest.mark.parametrize("escenario", QUE_PROCEDEN, ids=ids(QUE_PROCEDEN))
def test_el_movimiento_registra_la_salida_por_venta(escenario):
    movimiento = ejecutar(escenario).movimiento

    assert movimiento["motivo"] == "venta"
    assert movimiento["lote_id"] == escenario.lote["id"]
    assert movimiento["cantidad"] == escenario.cantidad
    assert movimiento["responsable"] == RESPONSABLE


@pytest.mark.parametrize("escenario", QUE_PROCEDEN, ids=ids(QUE_PROCEDEN))
def test_el_lote_nuevo_solo_cambia_el_stock(escenario):
    nuevo_lote = ejecutar(escenario).lote

    esperado = {**escenario.lote, "stock": escenario.stock_final}

    assert nuevo_lote == esperado


@pytest.mark.parametrize(
    "escenario", QUE_SE_RECHAZAN, ids=ids(QUE_SE_RECHAZAN)
)
def test_la_venta_se_rechaza_con_el_motivo_esperado(escenario):
    resultado = ejecutar(escenario)

    assert not resultado.procede
    assert escenario.motivo in resultado.motivo


@pytest.mark.parametrize(
    "escenario", QUE_SE_RECHAZAN, ids=ids(QUE_SE_RECHAZAN)
)
def test_una_venta_rechazada_no_genera_movimiento_ni_lote_nuevo(escenario):
    resultado = ejecutar(escenario)

    assert resultado.movimiento is None
    assert resultado.lote is None


@pytest.mark.parametrize("escenario", ESCENARIOS, ids=ids(ESCENARIOS))
def test_el_lote_de_entrada_nunca_se_modifica(escenario):
    resultado = ejecutar(escenario)

    assert resultado.entrada == escenario.lote


def test_vender_hasta_agotar_el_lote_y_rechazar_la_ultima_venta():
    primera, segunda, tercera = [r for _, r in vender_hasta_agotar()]

    assert primera.procede and primera.lote["stock"] == 3
    assert segunda.procede and segunda.lote["stock"] == 0
    assert not tercera.procede
    assert "stock" in tercera.motivo


def test_las_ventas_encadenadas_descuentan_el_stock_total_una_sola_vez():
    pasos = [resultado for _, resultado in vender_hasta_agotar()]
    vendido = sum(r.movimiento["cantidad"] for r in pasos if r.procede)
    cobrado = sum(r.movimiento["total_centavos"] for r in pasos if r.procede)

    assert vendido == lote()["stock"]
    assert cobrado == lote()["stock"] * PRECIO_REGULAR


def test_el_catalogo_tiene_identificadores_unicos():
    assert len(set(ids(ESCENARIOS))) == len(ESCENARIOS)


def test_el_catalogo_cubre_ventas_que_proceden_y_que_se_rechazan():
    assert QUE_PROCEDEN
    assert QUE_SE_RECHAZAN
