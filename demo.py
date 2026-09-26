"""Demostracion reproducible del registro de una venta desde un lote."""

from datetime import date

from src.venta import registrar_venta


FECHA_VENTA = date(2026, 9, 27)


def lote(deteriorado=False):
    return {
        "id": "L1",
        "stock": 5,
        "perecible": True,
        "vence": date(2026, 10, 1),
        "deteriorado": deteriorado,
        "bloqueado": False,
    }


def main():
    promocion = {
        "precio_centavos": 800,
        "inicio": date(2026, 9, 25),
        "fin": date(2026, 9, 30),
        "activa": True,
        "aprobada": True,
    }

    disponible = lote()
    nuevo_lote, movimiento = registrar_venta(
        lote=disponible,
        cantidad=2,
        fecha_venta=FECHA_VENTA,
        precio_regular_centavos=1000,
        promocion=promocion,
        responsable="empleado_1",
    )
    print("Venta aprobada")
    print(f"Stock original: {disponible['stock']}")
    print(f"Stock nuevo: {nuevo_lote['stock']}")
    print(f"Movimiento: {movimiento}")
    total_centavos = movimiento["total_centavos"]
    print(f"Total: S/ {total_centavos // 100},{total_centavos % 100:02d}")

    deteriorado = lote(deteriorado=True)
    try:
        registrar_venta(
            lote=deteriorado,
            cantidad=2,
            fecha_venta=FECHA_VENTA,
            precio_regular_centavos=1000,
            promocion=promocion,
            responsable="empleado_1",
        )
    except ValueError as error:
        print("Venta rechazada")
        print(f"Motivo: {error}")
        print(f"Stock conservado: {deteriorado['stock']}")
    else:
        raise AssertionError("El lote deteriorado debio ser rechazado")


if __name__ == "__main__":
    main()
