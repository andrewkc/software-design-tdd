# TDD aplicado a ventas y empleados de bodegas

Trabajo del Grupo 2 del curso Diseño de Software. Aplicamos **Test-Driven Development (TDD)** a una parte de CU-05 (venta desde un lote) y a CU-03 (asignación de empleados a una bodega).

## Integrantes

- Diaz Ysla, Walter Alexander
- Champi Hinojosa, Miguel Angel
- Cahuana Condori, Kelvin Andreí

## Problema y alcance

Antes de registrar una salida por venta comprobamos la cantidad solicitada, el stock y el estado del lote. Después seleccionamos el precio regular o una promoción aprobada y vigente. La operación devuelve un lote nuevo con el stock reducido una sola vez y un movimiento con responsable, cantidad, precio y total. Si la validación falla, el lote original permanece intacto.

La lógica de venta funciona en memoria. Un adaptador PostgreSQL separado guarda el lote actualizado y el movimiento cuando se necesita persistencia. No incluye múltiples productos o lotes por venta, permisos, cancelaciones ni mermas. No cubre todo CU-05.

## Metodología y tecnologías

Usamos Python 3.10 o superior, pytest, PostgreSQL, Docker Compose y Git. Organizamos el trabajo en ciclos **RED → GREEN → REFACTOR**: primero definimos un comportamiento mediante una prueba, después escribimos el código necesario para pasarla y finalmente mejoramos el diseño con la suite en verde. Los cuatro módulos de negocio separan validación, selección de precio, movimiento e integración.

| Módulo | Responsabilidad |
| --- | --- |
| `src/validacion.py` | Determinar el estado del lote y rechazar ventas inválidas. |
| `src/precios.py` | Seleccionar el precio aplicable. |
| `src/movimientos.py` | Devolver el nuevo lote y el movimiento de salida. |
| `src/venta.py` | Ejecutar validación, precio y movimiento en ese orden. |
| `src/repositorio_ventas.py` | Definir el contrato de persistencia, sin importar una base de datos. |
| `src/venta_aplicacion.py` | Coordinar la venta con cualquier repositorio que cumpla el contrato. |
| `src/infraestructura/postgres_ventas.py` | Guardar lotes y movimientos en PostgreSQL de forma transaccional. |
| `db/schema.sql` | Definir las tablas, separado del código de negocio. |
| `src/empleados.py` | Validar incorporación y retiro de empleados sin acceder a PostgreSQL. |
| `src/empleados_aplicacion.py` | Incorporar, listar y retirar empleados mediante un repositorio. |
| `src/infraestructura/postgres_empleados.py` | Aplicar CU-03 sobre las cuentas de PostgreSQL en una transacción. |
| `db/002_cu03.sql` | Crear bodegas y cuentas necesarias para CU-03. |

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

## Separación de la base de datos

`registrar_venta` y las reglas de negocio no importan PostgreSQL. La aplicación depende del contrato `RepositorioVentas`; solo el adaptador en `src/infraestructura/` conoce las consultas SQL. Docker Compose inicia PostgreSQL y ejecuta `db/schema.sql` al crear el volumen por primera vez:

```powershell
docker compose up -d --wait
```

La base queda disponible en `127.0.0.1:5434` (puerto configurable con `POSTGRES_HOST_PORT`). Para registrar una venta persistida:

```python
import psycopg
from datetime import date

from src.infraestructura.postgres_ventas import RepositorioVentasPostgres
from src.venta_aplicacion import registrar_venta_persistida

with psycopg.connect(
    "postgresql://bodegas:bodegas@127.0.0.1:5434/bodegas", autocommit=True
) as conexion:
    conexion.execute(
        "INSERT INTO lotes (id, stock, perecible, vence, deteriorado, bloqueado) "
        "VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
        ("L1", 5, True, date(2026, 10, 1), False, False),
    )
    nuevo_lote, movimiento = registrar_venta_persistida(
        RepositorioVentasPostgres(conexion), "L1", 2, date(2026, 9, 27),
        1000, None, "Ana",
    )
```

El adaptador bloquea el lote durante la transacción, aplica las reglas y guarda ambos resultados; si la venta falla, revierte la transacción. La conexión debe crearse con `autocommit=True`. El esquema se inicializa solo en un volumen vacío de Docker.

## CU-03 Gestión de empleados

CU-03 trabaja con cuentas de empleado ya existentes, como indica su precondición. El jefe activo puede consultar los empleados de su bodega, incorporar una cuenta activa sin asignación o retirar una cuenta de su bodega. Retirar elimina la asignación, conserva la cuenta y no borra los movimientos anteriores. La base impide que una cuenta esté asignada a dos bodegas a la vez.

En una base nueva, Docker Compose ejecuta `db/002_cu03.sql` al iniciar el volumen. Si ya existe un volumen creado antes de incorporar CU-03, aplica la migración una vez con este comando; es repetible:

```powershell
docker compose up -d --wait
docker compose exec -T db psql -U bodegas -d bodegas -v ON_ERROR_STOP=1 -f /docker-entrypoint-initdb.d/02-cu03.sql
```

Con una bodega, un jefe asignado y una cuenta de empleado ya registrados, el uso desde Python es:

```python
import psycopg

from src.empleados_aplicacion import incorporar_empleado, listar_empleados, retirar_empleado
from src.infraestructura.postgres_empleados import RepositorioEmpleadosPostgres

with psycopg.connect(
    "postgresql://bodegas:bodegas@127.0.0.1:5434/bodegas", autocommit=True
) as conexion:
    repositorio = RepositorioEmpleadosPostgres(conexion)
    incorporar_empleado(repositorio, "jefe_1", "empleado_1")
    empleados = listar_empleados(repositorio, "jefe_1")
    retirar_empleado(repositorio, "jefe_1", "empleado_1")
```

CU-01 todavía no crea las cuentas desde la aplicación y el proyecto aún no tiene pantalla ni inicio de sesión. Las funciones de CU-03 reciben el identificador de un jefe existente y verifican su rol, estado y bodega en PostgreSQL.

## Pruebas

```powershell
python -m pytest -p no:cacheprovider -q
```

Para incluir las tres pruebas de integración con PostgreSQL, inicia Docker Compose y configura la conexión de pruebas antes de ejecutar el comando:

```powershell
$env:TEST_DATABASE_URL = "postgresql://bodegas:bodegas@127.0.0.1:5434/bodegas"
python -m pytest -p no:cacheprovider -q
```

La suite contiene **55 pruebas**: las 38 existentes y 17 de CU-03. Ocho pruebas de integración requieren PostgreSQL y se omiten si `TEST_DATABASE_URL` no está configurada. El comando `-p no:cacheprovider` evita crear archivos de caché; no cambia las pruebas.

## Documentación y evidencias

- [Evidencias TDD y resultados](docs/evidencias.md)
- [Contrato técnico](docs/contrato.md)
- [Conclusiones del equipo](docs/conclusiones.md)
- [Validación](docs/persona-1.md), [precios e integración](docs/persona-2.md) y [movimientos](docs/persona-3.md)
