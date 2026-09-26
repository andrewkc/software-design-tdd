# CU-05: precio de venta desde un lote

Trabajo de **persona-2**, rama `persona-2`, para el laboratorio de Diseño de Software. Esta entrega implementa la selección de precio de una venta: utiliza el precio de una promoción solo si está aprobada, activa y vigente en la fecha de venta.

## Alcance de esta entrega

- `src/precios.py`: función `precio_aplicado`.
- `tests/test_precios.py`: cinco pruebas unitarias.
- `docs/README.md`: explicación del módulo y registro de su ciclo TDD.

La función recibe importes enteros en centavos (`1000` representa S/ 10,00) y fechas `datetime.date`. Esta parte no registra ventas ni modifica lotes. La integración con validación y movimientos corresponde a una etapa posterior del trabajo grupal.

## Ejecutar las pruebas

Con Python y pytest instalados, desde la raíz del repositorio:

```bash
python -m pytest tests/test_precios.py
```

## Ejemplo

```python
from datetime import date
from src.precios import precio_aplicado

promocion = {
    "precio_centavos": 800,
    "inicio": date(2026, 9, 25),
    "fin": date(2026, 9, 30),
    "activa": True,
    "aprobada": True,
}

precio = precio_aplicado(1000, promocion, date(2026, 9, 27))
# precio == 800 (S/ 8,00)
```

El contrato y la evidencia del ciclo están en [docs/README.md](docs/README.md).

## Ejecucion de pruebas

Instalar pytest si el entorno aun no lo tiene:

```bash
python -m pip install pytest
```

Ejecutar las pruebas de persona 2:

```bash
python -m pytest tests/test_precios.py
```

Resultado verificado en esta rama:

```text
5 passed
```
