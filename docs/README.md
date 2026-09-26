# Persona-2: selección de precio promocional

## Objetivo

`precio_aplicado(precio_regular_centavos, promocion, fecha_venta)` selecciona el importe unitario aplicable a la venta. Los precios son enteros en centavos para evitar errores de punto flotante: `1000` equivale a S/ 10,00.

Se usa `promocion["precio_centavos"]` únicamente cuando la promoción existe, está aprobada y activa, y la fecha de venta está dentro del intervalo inclusivo `inicio <= fecha_venta <= fin`. Si no se cumplen esas condiciones, se devuelve el precio regular. Los datos numéricos y fechas se reciben como válidos, según el contrato acordado.

## Pruebas

`tests/test_precios.py` comprueba:

- Sin promoción, se conserva el precio regular.
- Una promoción aprobada, activa y vigente aplica su precio.
- Una promoción vencida conserva el precio regular.
- Una promoción sin aprobación conserva el precio regular.
- Una promoción inactiva conserva el precio regular.

## Ciclo TDD registrado

Los siguientes resultados se obtuvieron ejecutando pytest con Python 3.13.5 y pytest 8.3.4.

### RED

Primero se escribieron las cinco pruebas. La primera ejecución falló durante la importación porque todavía no existía `src.precios`:

```text
collected 0 items / 1 error
ModuleNotFoundError: No module named 'src.precios'
1 error
```

Comando usado:

```bash
python -m pytest tests/test_precios.py
```

En el entorno de trabajo, el comando `pytest` no añadió la raíz del repositorio a la ruta de importación y falló antes, buscando `src`. Al invocar pytest como módulo con el Python de Miniconda, la importación llegó al módulo aún inexistente `src.precios`; ese fue el fallo RED esperado. El comando usado fue:

```powershell
& 'C:\Users\KELVIN\miniconda3\python.exe' -m pytest tests/test_precios.py
```

### GREEN

Se implementó la selección directa: verificar presencia, aprobación, actividad y fechas, y devolver el precio promocional o el regular.

```text
collected 5 items
 tests/test_precios.py ..... [100%]
5 passed in 0.04s
```

### REFACTOR

Se extrajo la condición de aprobación, actividad y vigencia a `_promocion_vigente`, dejando `precio_aplicado` enfocado en escoger el importe. La interfaz pública y el comportamiento no cambiaron.

```text
collected 5 items
 tests/test_precios.py ..... [100%]
5 passed in 0.04s
```

## Archivos

- `src/precios.py`: selección del precio.
- `tests/test_precios.py`: pruebas unitarias de la selección.
- `README.md`: descripción general de esta entrega de persona-2.

