"""Pruebas del modulo de validacion (persona 1, Grupo 2).

Ciclo 1 - estado_lote: estados que dependen de la fecha
  1.1 test_fecha_lejana_es_normal_y_muestra_la_fecha
  1.2 test_tres_dias_antes_es_proximo
  1.3 test_un_dia_antes_es_proximo
  1.4 test_vence_hoy
  1.5 test_fecha_pasada_es_vencido
"""

from datetime import date, timedelta

from validacion import estado_lote

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


def test_fecha_lejana_es_normal_y_muestra_la_fecha():
    # Fuera de la ventana de alerta de 3 dias acordada por el equipo.
    estado, texto = estado_lote(
        lote(vence=HOY + timedelta(days=10)), HOY
    )

    assert estado == "NORMAL"
    assert texto == "Vence el 11/10/2026"


def test_tres_dias_antes_es_proximo():
    estado, texto = estado_lote(lote(vence=HOY + timedelta(days=3)), HOY)

    assert estado == "PROXIMO"
    assert texto == "Vence en 3 días: revisar lote"


def test_un_dia_antes_es_proximo():
    # El acuerdo fija el texto como "Vence en X días", sin distinguir
    # el singular. Se respeta tal cual para no romper la integracion.
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
