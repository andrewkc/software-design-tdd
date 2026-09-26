# TDD aplicado al registro de ventas en bodegas

Trabajo del Grupo 2 del curso Diseño de Software. Aplicamos **Test-Driven Development (TDD)** a una parte de CU-05 del proyecto de bodegas: confirmar la venta de un producto desde un lote.

## Integrantes

- Diaz Ysla, Walter Alexander
- Champi Hinojosa, Miguel Angel
- Cahuana Condori, Kelvin Andreí

## Problema y alcance

Antes de registrar una salida por venta comprobamos la cantidad solicitada, el stock y el estado del lote. Después seleccionamos el precio regular o una promoción aprobada y vigente. La operación devuelve un lote nuevo con el stock reducido una sola vez y un movimiento con responsable, cantidad, precio y total. Si la validación falla, el lote original permanece intacto.

Esta implementación es una demostración en memoria de una venta de un producto desde un lote. No incluye base de datos, múltiples productos o lotes por venta, permisos, concurrencia, cancelaciones ni mermas. No cubre todo CU-05.

## Metodología y tecnologías

Usamos Python 3.10 o superior, pytest y Git. Organizamos el trabajo en ciclos **RED → GREEN → REFACTOR**: primero definimos un comportamiento mediante una prueba, después escribimos el código necesario para pasarla y finalmente mejoramos el diseño con la suite en verde. Los cuatro módulos separan validación, selección de precio, movimiento e integración.

| Módulo | Responsabilidad |
| --- | --- |
| `src/validacion.py` | Determinar el estado del lote y rechazar ventas inválidas. |
| `src/precios.py` | Seleccionar el precio aplicable. |
| `src/movimientos.py` | Devolver el nuevo lote y el movimiento de salida. |
| `src/venta.py` | Ejecutar validación, precio y movimiento en ese orden. |

Las fechas son objetos `datetime.date` y los importes son enteros en centavos. `1000` representa S/ 10,00. El [contrato técnico](docs/contrato.md) reúne las entradas, salidas y reglas compartidas.

## Instalación

Desde la raíz del repositorio:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

En macOS o Linux, el entorno se activa con `source .venv/bin/activate`. También es posible instalar la dependencia directamente con `python -m pip install -r requirements.txt`.

## Ejecución

La demostración muestra una venta promocional aceptada y una venta rechazada por deterioro:

```powershell
python demo.py
```

En la primera operación el stock pasa de 5 a 3 y el total es S/ 16,00. En la segunda se muestra el motivo del rechazo y el stock sigue en 5.

## Pruebas

```powershell
python -m pytest -p no:cacheprovider -q
```

La suite integrada contiene **34 pruebas**: 23 de validación, 5 de precios, 2 de movimientos y 4 de integración. Incluye casos normales, límites y errores. El comando `-p no:cacheprovider` evita crear archivos de caché; no cambia las pruebas.

## Documentación y evidencias

- [Evidencias TDD y resultados](docs/evidencias.md)
- [Contrato técnico](docs/contrato.md)
- [Conclusiones del equipo](docs/conclusiones.md)
- [Validación](docs/persona-1.md), [precios e integración](docs/persona-2.md) y [movimientos](docs/persona-3.md)
