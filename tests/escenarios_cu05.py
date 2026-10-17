from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from src.venta import registrar_venta

FECHA = date(2026, 9, 27)
VENCE_LEJANO = date(2026, 10, 10)
RESPONSABLE = "Ana"
PRECIO_REGULAR = 1000
PRECIO_PROMOCION = 800


def lote(**cambios) -> dict:
    base = {
        "id": "L1",
        "stock": 5,
        "perecible": True,
        "vence": VENCE_LEJANO,
        "deteriorado": False,
        "bloqueado": False,
    }
    base.update(cambios)
    return base


def promocion(**cambios) -> dict:
    base = {
        "precio_centavos": PRECIO_PROMOCION,
        "inicio": date(2026, 9, 25),
        "fin": date(2026, 9, 30),
        "activa": True,
        "aprobada": True,
    }
    base.update(cambios)
    return base


@dataclass(frozen=True)
class Escenario:
    id: str
    flujo: str
    descripcion: str
    lote: dict
    cantidad: int
    fecha: date = FECHA
    precio_regular: int = PRECIO_REGULAR
    promocion: dict | None = None
    revision_hoy: bool = False
    procede: bool = True
    stock_final: int | None = None
    precio_unitario: int | None = None
    motivo: str | None = None
    ref: str = ""


@dataclass(frozen=True)
class Resultado:
    procede: bool
    entrada: dict
    lote: dict | None
    movimiento: dict | None
    motivo: str | None


def ejecutar(escenario: Escenario, registrar=registrar_venta) -> Resultado:
    entrada = dict(escenario.lote)

    try:
        nuevo_lote, movimiento = registrar(
            lote=entrada,
            cantidad=escenario.cantidad,
            fecha_venta=escenario.fecha,
            precio_regular_centavos=escenario.precio_regular,
            promocion=escenario.promocion,
            responsable=RESPONSABLE,
            revision_hoy=escenario.revision_hoy,
        )
    except ValueError as error:
        return Resultado(False, entrada, None, None, str(error))

    return Resultado(True, entrada, nuevo_lote, movimiento, None)


def _procede(id, flujo, descripcion, stock_final, precio_unitario, **datos):
    return Escenario(
        id=id,
        flujo=flujo,
        descripcion=descripcion,
        procede=True,
        stock_final=stock_final,
        precio_unitario=precio_unitario,
        **datos,
    )


def _rechaza(id, descripcion, motivo, **datos):
    return Escenario(
        id=id,
        flujo="rechazo",
        descripcion=descripcion,
        procede=False,
        motivo=motivo,
        **datos,
    )


PRINCIPAL = "flujo principal"
PRECIO = "selección de precio"
LIMITE = "límites del lote"

ESCENARIOS = [
    _procede(
        "venta_a_precio_regular", PRINCIPAL,
        "Venta de 2 unidades de un lote vigente, sin promoción",
        3, PRECIO_REGULAR,
        lote=lote(), cantidad=2,
        ref="CU-05 flujo principal | RN-04, RN-05",
    ),
    _procede(
        "venta_con_promocion_vigente", PRINCIPAL,
        "Venta de 2 unidades con promoción aprobada y vigente: total S/ 16,00",
        3, PRECIO_PROMOCION,
        lote=lote(), cantidad=2, promocion=promocion(),
        ref="CU-05 flujo principal | RN-05, RN-09",
    ),
    _procede(
        "venta_de_una_unidad", PRINCIPAL,
        "La cantidad mínima válida es 1",
        4, PRECIO_REGULAR,
        lote=lote(), cantidad=1,
        ref="CU-05 flujo principal | RN-03, RN-04",
    ),
    _procede(
        "venta_de_todo_el_stock", PRINCIPAL,
        "Vender exactamente el stock disponible deja el lote en 0",
        0, PRECIO_REGULAR,
        lote=lote(), cantidad=5,
        ref="CU-05 flujo principal | RN-04",
    ),
    _procede(
        "producto_sin_fecha_aplicable", PRINCIPAL,
        "Un producto no perecible sin fecha de vencimiento se puede vender",
        3, PRECIO_REGULAR,
        lote=lote(perecible=False, vence=None), cantidad=2,
        ref="CU-05 flujo principal | RN-06",
    ),
    _procede(
        "promocion_en_su_primer_dia", PRECIO,
        "La promoción rige desde el día de inicio",
        3, PRECIO_PROMOCION,
        lote=lote(), cantidad=2, promocion=promocion(), fecha=date(2026, 9, 25),
        ref="CU-05 flujo principal | RN-09",
    ),
    _procede(
        "promocion_en_su_ultimo_dia", PRECIO,
        "La promoción rige hasta el día final, inclusive",
        3, PRECIO_PROMOCION,
        lote=lote(), cantidad=2, promocion=promocion(), fecha=date(2026, 9, 30),
        ref="CU-05 flujo principal | RN-09",
    ),
    _procede(
        "promocion_ya_vencida", PRECIO,
        "Un día después del fin de la promoción se cobra el precio regular",
        3, PRECIO_REGULAR,
        lote=lote(), cantidad=2, promocion=promocion(), fecha=date(2026, 10, 1),
        ref="CU-05 flujo principal | RN-09",
    ),
    _procede(
        "promocion_aun_no_iniciada", PRECIO,
        "Un día antes del inicio de la promoción se cobra el precio regular",
        3, PRECIO_REGULAR,
        lote=lote(), cantidad=2, promocion=promocion(), fecha=date(2026, 9, 24),
        ref="CU-05 flujo principal | RN-09",
    ),
    _procede(
        "promocion_no_aprobada", PRECIO,
        "Una promoción sin aprobación del jefe no se aplica",
        3, PRECIO_REGULAR,
        lote=lote(), cantidad=2, promocion=promocion(aprobada=False),
        ref="CU-05 flujo principal | RN-09, CU-08",
    ),
    _procede(
        "promocion_inactiva", PRECIO,
        "Una promoción marcada como inactiva no se aplica",
        3, PRECIO_REGULAR,
        lote=lote(), cantidad=2, promocion=promocion(activa=False),
        ref="CU-05 flujo principal | RN-09, CU-08-FA-05",
    ),
    _procede(
        "lote_que_vence_en_3_dias", LIMITE,
        "Dentro de la ventana de alerta la venta sigue permitida",
        3, PRECIO_REGULAR,
        lote=lote(vence=FECHA + timedelta(days=3)), cantidad=2,
        ref="CU-05 flujo principal | RN-06, CU-06",
    ),
    _procede(
        "lote_que_vence_en_1_dia", LIMITE,
        "A un día del vencimiento la venta sigue permitida",
        3, PRECIO_REGULAR,
        lote=lote(vence=FECHA + timedelta(days=1)), cantidad=2,
        ref="CU-05 flujo principal | RN-06, CU-06",
    ),
    _procede(
        "vence_hoy_con_revision", LIMITE,
        "El día del vencimiento procede si el personal registró la revisión",
        3, PRECIO_REGULAR,
        lote=lote(vence=FECHA), cantidad=2, revision_hoy=True,
        ref="CU-05 flujo principal | RN-06, contrato técnico",
    ),
    _rechaza(
        "cantidad_cero", "Cantidad 0: no hay nada que vender",
        "cantidad",
        lote=lote(), cantidad=0,
        ref="CU-05-EX-01 | RN-03",
    ),
    _rechaza(
        "cantidad_negativa", "Una cantidad negativa se rechaza",
        "cantidad",
        lote=lote(), cantidad=-1,
        ref="CU-05-EX-01 | RN-03",
    ),
    _rechaza(
        "cantidad_mayor_al_stock", "Se piden 6 y el lote tiene 5",
        "stock",
        lote=lote(), cantidad=6,
        ref="CU-05-EX-01 | RN-04",
    ),
    _rechaza(
        "lote_sin_stock", "Un lote agotado no admite ventas",
        "stock",
        lote=lote(stock=0), cantidad=1,
        ref="CU-05-EX-01 | RN-04",
    ),
    _rechaza(
        "lote_deteriorado", "Un lote marcado como deteriorado no se vende",
        "observación",
        lote=lote(deteriorado=True), cantidad=2,
        ref="CU-05-EX-02 | RN-06",
    ),
    _rechaza(
        "lote_bloqueado", "Un lote bloqueado por envase o conservación no se vende",
        "observación",
        lote=lote(bloqueado=True), cantidad=2,
        ref="CU-05-EX-02 | RN-06, contrato técnico",
    ),
    _rechaza(
        "lote_vencido_ayer", "Un día después de la fecha de vencimiento ya no se vende",
        "Vencido",
        lote=lote(vence=FECHA - timedelta(days=1)), cantidad=2,
        ref="CU-05-EX-02 | RN-06",
    ),
    _rechaza(
        "perecible_sin_fecha", "Un perecible sin fecha verificada no se vende",
        "Fecha sin verificar",
        lote=lote(vence=None), cantidad=2,
        ref="CU-05-EX-02 | RN-06, contrato técnico",
    ),
    _rechaza(
        "vence_hoy_sin_revision", "El día del vencimiento exige la revisión del personal",
        "revisión",
        lote=lote(vence=FECHA), cantidad=2,
        ref="CU-05-EX-02 | RN-06, contrato técnico",
    ),
    _rechaza(
        "deteriorado_que_vence_hoy_con_revision",
        "La revisión del día no habilita un lote deteriorado",
        "observación",
        lote=lote(vence=FECHA, deteriorado=True), cantidad=2, revision_hoy=True,
        ref="CU-05-EX-02 | RN-06",
    ),
    _rechaza(
        "bloqueado_que_vence_hoy_con_revision",
        "La revisión del día no habilita un lote bloqueado",
        "observación",
        lote=lote(vence=FECHA, bloqueado=True), cantidad=2, revision_hoy=True,
        ref="CU-05-EX-02 | RN-06, contrato técnico",
    ),
    _rechaza(
        "deteriorado_y_vencido",
        "El bloqueo por deterioro tiene prioridad sobre el vencimiento",
        "observación",
        lote=lote(vence=FECHA - timedelta(days=5), deteriorado=True), cantidad=2,
        ref="CU-05-EX-02 | RN-06",
    ),
    _rechaza(
        "rechazo_con_promocion_vigente",
        "Una promoción vigente no salva la venta de un lote deteriorado",
        "observación",
        lote=lote(deteriorado=True), cantidad=2, promocion=promocion(),
        ref="CU-05-EX-02 | RN-06, RN-09",
    ),
    _rechaza(
        "no_perecible_con_fecha_vencida",
        "Si hay fecha registrada se aplican las reglas de fecha aunque no sea perecible",
        "Vencido",
        lote=lote(perecible=False, vence=FECHA - timedelta(days=1)), cantidad=2,
        ref="CU-05-EX-02 | RN-06",
    ),
]

POR_ID = {escenario.id: escenario for escenario in ESCENARIOS}
QUE_PROCEDEN = [e for e in ESCENARIOS if e.procede]
QUE_SE_RECHAZAN = [e for e in ESCENARIOS if not e.procede]


def vender_hasta_agotar(registrar=registrar_venta) -> list[tuple[str, Resultado]]:
    pasos = []
    actual = lote()

    for etiqueta, cantidad in (
        ("Primera venta: 2 de 5", 2),
        ("Segunda venta: 3 de 3", 3),
        ("Tercera venta: 1 de 0", 1),
    ):
        entrada = dict(actual)

        try:
            nuevo_lote, movimiento = registrar(
                lote=entrada,
                cantidad=cantidad,
                fecha_venta=FECHA,
                precio_regular_centavos=PRECIO_REGULAR,
                promocion=None,
                responsable=RESPONSABLE,
            )
        except ValueError as error:
            pasos.append((etiqueta, Resultado(False, entrada, None, None, str(error))))
            continue

        pasos.append((etiqueta, Resultado(True, entrada, nuevo_lote, movimiento, None)))
        actual = nuevo_lote

    return pasos
