import argparse
import sys
from datetime import date

from src.validacion import estado_lote
from tests.escenarios_cu05 import (
    ESCENARIOS,
    FECHA,
    POR_ID,
    PRECIO_REGULAR,
    Escenario,
    ejecutar,
    lote,
    promocion,
    vender_hasta_agotar,
)


def soles(centavos):
    return f"S/ {centavos // 100},{centavos % 100:02d}"


def detalle(resultado):
    if not resultado.procede:
        return resultado.motivo

    movimiento = resultado.movimiento
    return (
        f"stock {resultado.entrada['stock']} -> {resultado.lote['stock']} | "
        f"precio {soles(movimiento['precio_unitario_centavos'])} | "
        f"total {soles(movimiento['total_centavos'])}"
    )


def coincide(escenario, resultado):
    if resultado.procede != escenario.procede:
        return False

    if escenario.procede:
        return (
            resultado.lote["stock"] == escenario.stock_final
            and resultado.movimiento["precio_unitario_centavos"]
            == escenario.precio_unitario
        )

    return escenario.motivo in resultado.motivo


def decision(resultado):
    return "PROCEDE  " if resultado.procede else "RECHAZADA"


def mostrar_escenarios(escenarios):
    fallas = 0
    flujo = None

    for escenario in escenarios:
        if escenario.flujo != flujo:
            flujo = escenario.flujo
            print(f"\n{flujo.upper()}")

        resultado = ejecutar(escenario)
        ok = coincide(escenario, resultado)
        fallas += not ok
        marca = "ok   " if ok else "FALLA"
        print(f"  [{marca}] {decision(resultado)} {escenario.id:<40} {detalle(resultado)}")

    proceden = sum(1 for e in escenarios if e.procede)
    print(
        f"\n{len(escenarios)} escenarios: {proceden} deben proceder, "
        f"{len(escenarios) - proceden} deben rechazarse, {fallas} no coinciden."
    )
    return 1 if fallas else 0


def mostrar_uno(identificador):
    if identificador not in POR_ID:
        print(f"No existe el escenario '{identificador}'. Use --lista para verlos.")
        return 2

    escenario = POR_ID[identificador]
    resultado = ejecutar(escenario)
    esperado = "debe proceder" if escenario.procede else "debe rechazarse"

    print(f"{escenario.id}\n  {escenario.descripcion}")
    print(f"  Modelado:  {escenario.ref}")
    print(f"  Esperado:  {esperado}")
    print(f"  Obtenido:  {decision(resultado).strip()}  {detalle(resultado)}")
    print(f"  Coincide:  {'sí' if coincide(escenario, resultado) else 'NO'}")
    return 0


def mostrar_secuencia():
    print("VENDER HASTA AGOTAR EL LOTE (cada venta usa el lote que dejó la anterior)")

    for etiqueta, resultado in vender_hasta_agotar():
        print(f"  {decision(resultado)} {etiqueta:<24} {detalle(resultado)}")

    return 0


def fecha_o_ninguna(texto):
    return None if texto == "ninguna" else date.fromisoformat(texto)


def promocion_desde(texto, sin_aprobar, inactiva):
    if texto is None:
        return None

    precio, inicio, fin = texto.split(":")
    return promocion(
        precio_centavos=int(precio),
        inicio=date.fromisoformat(inicio),
        fin=date.fromisoformat(fin),
        aprobada=not sin_aprobar,
        activa=not inactiva,
    )


def probar_caso_propio(args):
    vence = fecha_o_ninguna(args.vence)
    datos_lote = lote(
        stock=args.stock,
        vence=vence,
        perecible=not args.no_perecible,
        deteriorado=args.deteriorado,
        bloqueado=args.bloqueado,
    )
    escenario = Escenario(
        id="propio",
        flujo="propio",
        descripcion="",
        lote=datos_lote,
        cantidad=args.cantidad,
        fecha=date.fromisoformat(args.fecha),
        precio_regular=args.precio,
        promocion=promocion_desde(args.promocion, args.sin_aprobar, args.inactiva),
        revision_hoy=args.revision,
    )

    estado, texto = estado_lote(datos_lote, escenario.fecha)
    resultado = ejecutar(escenario)

    print(f"Lote:       stock {args.stock}, vence {vence or 'sin fecha'}")
    print(f"Estado:     {estado} - {texto}")
    print(f"Venta:      {args.cantidad} unidades el {escenario.fecha}, precio regular {soles(args.precio)}")
    if escenario.promocion:
        oferta = escenario.promocion
        print(
            f"Promoción:  {soles(oferta['precio_centavos'])} del {oferta['inicio']} al {oferta['fin']}, "
            f"{'aprobada' if oferta['aprobada'] else 'SIN aprobar'}, "
            f"{'activa' if oferta['activa'] else 'INACTIVA'}"
        )
    print(f"Resultado:  {decision(resultado).strip()}")
    print(f"            {detalle(resultado)}")
    return 0


def crear_parser():
    parser = argparse.ArgumentParser(
        description="Prueba el caso de uso CU-05 (venta desde un lote). "
        "Sin argumentos corre todos los escenarios."
    )
    parser.add_argument("--lista", action="store_true", help="lista los escenarios")
    parser.add_argument("-e", "--escenario", metavar="ID", help="corre un escenario")
    parser.add_argument("--secuencia", action="store_true", help="vende hasta agotar el lote")

    subparsers = parser.add_subparsers(dest="orden")
    propio = subparsers.add_parser("propio", help="prueba un caso con sus propios datos")
    propio.add_argument("--stock", type=int, default=5)
    propio.add_argument("--cantidad", type=int, default=2)
    propio.add_argument("--vence", default="2026-10-10", help="AAAA-MM-DD o 'ninguna'")
    propio.add_argument("--fecha", default=FECHA.isoformat(), help="fecha de la venta")
    propio.add_argument("--precio", type=int, default=PRECIO_REGULAR, help="en centavos")
    propio.add_argument("--promocion", metavar="PRECIO:INICIO:FIN")
    propio.add_argument("--sin-aprobar", action="store_true")
    propio.add_argument("--inactiva", action="store_true")
    propio.add_argument("--deteriorado", action="store_true")
    propio.add_argument("--bloqueado", action="store_true")
    propio.add_argument("--no-perecible", action="store_true")
    propio.add_argument("--revision", action="store_true", help="revisión del día registrada")
    return parser


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    args = crear_parser().parse_args(argv)

    if args.lista:
        for escenario in ESCENARIOS:
            print(f"{escenario.id:<40} {escenario.ref:<46} {escenario.descripcion}")
        return 0

    if args.escenario:
        return mostrar_uno(args.escenario)

    if args.secuencia:
        return mostrar_secuencia()

    if args.orden == "propio":
        return probar_caso_propio(args)

    return mostrar_escenarios(ESCENARIOS)


if __name__ == "__main__":
    sys.exit(main())
