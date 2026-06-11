# SISFARMA 💊

Sistema de gestión y control para farmacias desarrollado en el entorno de bases de datos relacionales.

## 👥 Integrantes
* Jhon Alexander Flores Condori
* Alberto Fabricio Lescano Taype
* Shantall Milagros Sulla Otazu
* Nick Rommel Valdivia Sulla

---

## 🗄️ Arquitectura de la Base de Datos

El diseño de la base de datos se encuentra en `src/database/schema.sql` y está implementado bajo el motor **InnoDB** de **MySQL** utilizando la codificación `utf8mb4`. 

El sistema se compone de **15 tablas** estructuradas estratégicamente para garantizar la consistencia de los datos mediante restricciones de integridad referencial.

### 📊 Diccionario de Tablas por Módulos

### 📁 1. Módulo de Catálogos Base
*   **`CATEGORIA`** ➔ Clasificación principal de los productos (ej. Analgésicos, Antibióticos).
*   **`PROVEEDOR`** ➔ Registro de laboratorios y distribuidoras que surten a la farmacia.
*   **`CLIENTE`** ➔ Registro de compradores para la emisión de comprobantes e historial médico.

---

### 👥 2. Módulo de Personal y Usuarios
*   **`USUARIO`** ➔ Credenciales y roles del personal (Administradores, Farmacéuticos) con jerarquía de supervisión integrada.

---

### 📦 3. Módulo de Productos y Control de Stock
*   **`MEDICAMENTO`** ➔ Catálogo central con la información comercial y descripción de cada fármaco.
*   **`LOTE`** ➔ Trazabilidad sanitaria; controla la procedencia y la fecha de vencimiento específica de los productos.
*   **`INVENTARIO`** ➔ Control físico de existencias en almacén y umbrales de stock mínimo para reposición.
*   **`ALERTA`** ➔ Sistema automático que notifica productos próximos a vencer o desabastecidos.

---

### 💰 4. Módulo de Operaciones de Venta
*   **`VENTA`** ➔ Cabecera que consolida el movimiento comercial (fecha, total, cliente e ID del cajero).
*   **`DETALLE_VENTA`** ➔ Desglose línea por línea de los medicamentos vendidos, cantidades y precios cobrados.
*   **`PAGO`** ➔ Registro del flujo de caja; define el monto exacto y el método utilizado (Efectivo, Tarjeta, Yape/Plin).
*   **`HISTORIAL_VENTA`** ➔ Bitácora de auditoría médica (registro de recetas presentadas, descuentos aplicados o notas especiales).

---

### 🚚 5. Módulo de Abastecimiento y Auditoría
*   **`COMPRA`** ➔ Órdenes de pedido general emitidas hacia los proveedores autorizados.
*   **`DETALLE_COMPRA`** ➔ Lista detallada de los medicamentos solicitados, cantidades y costo de adquisición.
*   **`REPORTE`** ➔ Almacenamiento de informes gerenciales generados por los administradores para la toma de decisiones.

## 🔗 Relaciones y Flujos de Datos

Las tablas no trabajan de forma aislada; se conectan mediante claves foráneas (`FOREIGN KEY`) para modelar los procesos reales de una farmacia:

### 1. El Núcleo del Producto (`MEDICAMENTO` ➔ `LOTE` ➔ `INVENTARIO`)
* Un **medicamento** pertenece a una única **categoría** (`id_categoria`).
* Para evitar problemas sanitarios, los medicamentos se dividen en **lotes** (`LOTE`). Esta tabla usa una **clave primaria compuesta** `PRIMARY KEY (numero_lote, id_medicamento)`. 
* El **inventario** se fusiona directamente con los lotes para saber exactamente cuántas unidades quedan de una caja específica que vence en una fecha determinada.

### 2. El Flujo Comercial de Ventas (`VENTA` ➔ `DETALLE_VENTA` ➔ `PAGO`)
Cuando se realiza una venta, la base de datos ejecuta una estructura Maestro-Detalle:
* **`VENTA` (Maestro):** Registra el "cuándo" y el "quién". Fusiona en una sola fila la fecha, el total, el **cliente** (`id_cliente`) que compra y el **usuario** (`id_usuario`) que atiende en caja.
* **`DETALLE_VENTA` (Detalle):** Se fusiona con la venta principal (`id_venta`) y con el catálogo de productos (`id_medicamento`). Permite que una sola venta contenga múltiples medicamentos con sus respectivas cantidades.
* **`PAGO`:** Se acopla de manera única (`id_venta INT UNIQUE`) a la venta mediante una relación de uno a uno (1:1), guardando el método y monto cobrado.

### 3. El Flujo de Abastecimiento (`COMPRA` ➔ `DETALLE_COMPRA`)
Sigue la misma lógica maestro-detalle de las ventas, pero mirando hacia los proveedores:
* La **compra** consolida qué trabajador (`id_usuario`) la solicitó y a qué distribuidora (`id_proveedor`).
* El **detalle de la compra** especifica cuántas unidades de qué medicamento se están pidiendo y a qué precio se adquirieron para calcular los costos del negocio.

### 4. Jerarquía de Empleados (Autorelación en `USUARIO`)
* La tabla `USUARIO` posee una relación reflexiva (consigo misma) a través del campo `id_supervisor`. Esto permite estructurar organigramas donde un usuario de rango superior (como un administrador) supervisa a los farmacéuticos.

---

> **Políticas de Integridad (Borrado en Cascada):**
> El diseño de la base de datos protege la información crítica. Si se elimina una `VENTA` o una `COMPRA`, sus respectivos detalles (`DETALLE_VENTA`, `DETALLE_COMPRA`), pagos e historiales se borrarán automáticamente en cascada (`ON DELETE CASCADE`). Sin embargo, no se puede eliminar un medicamento del catálogo si este tiene lotes vigentes o stock en inventario (`ON DELETE RESTRICT`).

## 🛠️ Configuración del entorno local

1. Copia `.env.example` a `.env`.
2. Actualiza las credenciales MySQL con el usuario y la contraseña válidos para tu servidor local.
   - Si `root` no puede autenticarse, crea un usuario MySQL dedicado y usa esas credenciales.
3. Si tu servidor MySQL usa un plugin de autenticación distinto, ajusta `MYSQL_AUTH_PLUGIN`.
4. Ejecuta el script de inicialización de la base de datos:

```bash
python -m src.database.setup
```

5. Inicia la aplicación Flask:

```bash
python app.py
```

## 📦 Dependencias que deben instalar tus compañeros

1. Instalar Python 3.11 o 3.12 (o 3.13 si ya está probado en el equipo).
2. Instalar MySQL Server (MySQL 8.x recomendado) y dejar el servicio ejecutando.
3. Instalar dependencias de Python desde el proyecto:

```bash
pip install -r requirements.txt
```

4. Copiar `.env.example` a `.env` y actualizar las credenciales:

```bash
cp .env.example .env
```

5. Ajustar el archivo `.env` con los valores correctos de MySQL.
6. Ejecutar la inicialización de la base de datos:

```bash
python -m src.database.setup
```

7. Ejecutar la aplicación:

```bash
python app.py
```

### 🔧 Requisitos específicos de MySQL

- MySQL Server debe estar instalado y corriendo.
- El usuario y la contraseña en `.env` deben ser válidos para el servidor.
- Si MySQL usa `caching_sha2_password`, dejar `MYSQL_AUTH_PLUGIN=caching_sha2_password`.
- Si usan otro plugin, ajustar `MYSQL_AUTH_PLUGIN` en `.env`.


# Reporte Comparativo de Optimización de Rendimiento
**Laboratorio:** El Desafío de Rendimiento

Este documento contiene el análisis técnico del comportamiento de tres consultas sobre un dataset de 100,001 registros generados en PostgreSQL.

---

## 1. Ejecución Inicial (Sin Modificaciones)

Se evaluó el estado inicial de la base de datos obteniendo los siguientes planes de ejecución mediante `EXPLAIN ANALYZE`:

* **Consulta 1 (`WHERE correo = 'carlos.mendoza@api.com'`):** 
  * Plan: `Seq Scan` (Sequential Scan)
  * Costo teórico: `0.00..1834.09`
  * Tiempo real: `19.411 ms`
  * **Análisis:** Obliga al motor a examinar linealmente las 100,001 filas.

* **Consulta 2 (`WHERE apellido = 'Apellido_45' AND estado = 'Activo'`):** 
  * Plan: `Seq Scan`
  * Costo teórico: `0.00..1954.30`
  * Tiempo real: `19.067 ms`
  * **Análisis:** Al no existir estructuras secundarias, evalúa toda la tabla.

* **Consulta 3 (`WHERE estado = 'Activo'`):** 
  * Plan: `Seq Scan`
  * Costo teórico: `0.00..1834.09`
  * Tiempo real: `24.148 ms`
  * **Análisis:** Recorrido completo para hallar coincidencias generales.

---

## 2. Cálculo de la Selectividad

Aplicamos la fórmula analítica (Selectividad = Filas devueltas / Total de filas) para evaluar matemáticamente la viabilidad de los índices:

### Caso Consulta 1 (Correo)
* **Cálculo:** 1 / 100,001 = 0.0000099
* **Selectividad:** **~0.001%**
* **Evaluación:** Altamente Positiva. La selectividad tiende a cero, lo que exige la inclusión de un índice de acceso directo.

### Caso Consulta 2 (Apellido y Estado)
Los apellidos se repiten en ciclos de 100 (aprox. 1,000 filas por apellido) y el 80% están activos.
* **Cálculo esperable:** 800 / 100,001 = 0.00799
* **Selectividad:** **~0.8%**
* **Evaluación:** Positiva. Al representar menos del 1% del volumen total, una clave de búsqueda evitará procesar más de 99,000 registros.

### Caso Consulta 3 (Estado)
Por el diseño del script (`i % 5 = 0`), el 80% de la tabla es 'Activo'.
* **Cálculo:** 80,000 / 100,001 = 0.799
* **Selectividad:** **~80%**
* **Evaluación:** Negativa. Cuando se recupera la gran mayoría de la tabla, el costo de usar un índice es mayor que leer la tabla secuencialmente de forma directa.

---

## 3. Propuesta y Creación de Índices

Atendiendo a las conclusiones analíticas, se aplicó la siguiente optimización:

```sql
-- 1. Índice Simple (Para la consulta de Correo - Altamente selectiva)
CREATE UNIQUE INDEX idx_usuarios_correo ON usuarios (correo);

-- 2. Índice Compuesto (Para la consulta de Apellido y Estado - Selectiva)
CREATE INDEX idx_usuarios_apellido_estado ON usuarios (apellido, estado);

-- 3. Para la consulta de Estado: Ninguno (Evaluación Negativa)
