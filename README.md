# CU-05: registrar una venta desde un lote

Trabajo del Grupo 2 para demostrar TDD sobre una parte acotada del caso de uso CU-05. El flujo valida el lote, obtiene el precio aplicable y registra un movimiento con el stock resultante.

## Contrato

- Las fechas son objetos `datetime.date`.
- Los precios son enteros en centavos (`1000` representa S/ 10,00).
- Los lotes bloqueados, deteriorados, vencidos o sin fecha requerida no se venden. Un lote que vence hoy requiere `revision_hoy=True`.
- Una promoción solo aplica si está aprobada, activa y vigente.
- Los movimientos producen un nuevo diccionario de lote; no modifican el original.

## Módulos

- `src/validacion.py`: estado del lote y validación de la venta.
- `src/precios.py`: selección del precio promocional o regular.
- `src/movimientos.py`: cálculo del nuevo stock y registro del movimiento.
- `src/venta.py`: integración de validación, precio y movimiento.

## Ejecutar

Instala pytest si hace falta y, desde la raíz del repositorio, ejecuta la suite:

```bash
python -m pip install pytest
python -m pytest -q
```

## Alcance

La demostración es en memoria. No incluye persistencia, ventas con varios productos o lotes, concurrencia, permisos, cancelaciones ni registro de mermas. No representa la implementación completa de CU-05.

## Documentación

- [Registro TDD y módulos](docs/README.md)
- [Ciclo de validación de persona 1](docs/persona-1-validacion.md)
- [Evidencias](docs/evidencias.md)
