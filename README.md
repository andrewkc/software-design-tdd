# CU-05: registrar una venta desde un lote

Trabajo del Grupo 2 para demostrar TDD sobre una parte acotada del caso de uso CU-05. El flujo valida el lote, obtiene el precio aplicable y registra un movimiento con el stock resultante.

## Flujo

`registrar_venta` ejecuta las operaciones en este orden:

1. `validar_venta` verifica cantidad, stock, vencimiento y estado del lote.
2. `precio_aplicado` selecciona el precio promocional vigente o el regular.
3. `crear_movimiento` devuelve un lote nuevo y el movimiento de salida.

Si la validación rechaza la venta, no se calcula el precio ni se crea un movimiento. El lote original no se modifica.

## Contrato

- Las fechas son objetos `datetime.date`.
- Los precios son enteros en centavos (`1000` representa S/ 10,00).
- Un lote deteriorado, bloqueado, vencido o perecible sin fecha no se vende.
- Un lote que vence el día de la venta requiere `revision_hoy=True`; esta marca registra una revisión humana, no certifica inocuidad.
- Una promoción solo aplica si está aprobada, activa y vigente en el intervalo inclusivo `inicio <= fecha_venta <= fin`.
- El movimiento descuenta la cantidad exactamente una vez y conserva el lote original.

## Módulos

- `src/validacion.py`: estado del lote y validación de la venta.
- `src/precios.py`: selección del precio promocional o regular.
- `src/movimientos.py`: cálculo del nuevo stock y registro del movimiento.
- `src/venta.py`: integración de validación, precio y movimiento.

## Pruebas

La suite contiene 34 pruebas unitarias y de integración.

```powershell
python -m pip install pytest
python -m pytest -p no:cacheprovider -q
```

## Alcance

La demostración es en memoria. No incluye persistencia, ventas con varios productos o lotes, concurrencia, permisos, cancelaciones ni registro de mermas. No representa la implementación completa de CU-05.

## Documentación

- [Registro TDD y módulos](docs/README.md)
- [Ciclo de validación de persona 1](docs/persona-1-validacion.md)
- [Evidencias](docs/evidencias.md)
