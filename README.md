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


# 📄 Reporte de Optimización: `optimizacion.md`

Este documento contiene el análisis técnico del comportamiento de las tres consultas del laboratorio de rendimiento sobre un dataset de 100,001 registros generados en el motor MySQL.

---

## 1. Primer EXPLAIN (Sin Modificaciones)

Se evaluó el estado inicial de la base de datos sin alterar el esquema físico estructurado, obteniendo los siguientes planes de ejecución analíticos:

* **Consulta 1 (`WHERE correo = '...'`):** Tipo de acceso `ALL` (**Seq Scan**), evaluando **100,001 filas**. Obliga al motor a examinar linealmente toda la tabla.
* **Consulta 2 (`WHERE apellido = '...' AND estado = '...'`):** Tipo de acceso `ALL` (**Seq Scan**), evaluando **100,001 filas**. No existen estructuras secundarias para indexar cadenas parciales de texto.
* **Consulta 3 (`WHERE estado = 'Activo'`):** Tipo de acceso `ALL` (**Seq Scan**), evaluando **100,001 filas**. Recorrido completo para hallar coincidencias generales de estado.

---

## 2. Cálculo de la Selectividad

Aplicamos la fórmula analítica de selectividad requerida para evaluar de forma matemática en qué columnas es viable inyectar un índice y en cuáles es perjudicial:

$$\text{Selectividad} = \frac{\text{Filas devueltas por el filtro}}{\text{Total de filas en la tabla}}$$

### Caso Consulta 1 (Correo)
* **Filas resultantes:** 1
* **Filas totales:** 100,001
$$\text{Selectividad} = \frac{1}{100001} \approx 0.00000999 \text{ (0.001\%)} $$
* **Evaluación:** **Altamente Positiva**. La selectividad es muy inferior al umbral recomendado del 20%. Exige la inclusión de un índice de acceso directo.

### Caso Consulta 2 (Apellido y Estado)
* En el script de inserción, los apellidos se repiten uniformemente en ciclos de 100. Al haber 100,000 registros, hay 1,000 filas por cada apellido. Cerca del 80% están activos.
* **Filas resultantes:** ~800 filas.
* **Filas totales:** 100,001.
$$\text{Selectividad} = \frac{800}{100001} \approx 0.00799 \text{ (0.8\%)} $$
* **Evaluación:** **Positiva**. Al representar menos del 1% del volumen total de datos, el uso de una clave de búsqueda secundaria evitará procesar más de 99,000 registros innecesarios.

### Caso Consulta 3 (Estado)
* Por diseño del algoritmo de inserción (`CASE WHEN i % 5 = 0 THEN 'Inactivo' ELSE 'Activo' END`), el **80% de la tabla** posee el estado 'Activo'.
* **Filas resultantes:** ~80,000 filas.
* **Filas totales:** 100,001.
$$\text{Selectividad} = \frac{80000}{100001} \approx 0.80 \text{ (80\%)} $$
* **Evaluación:** **Negativa**. Cuando la consulta recupera la gran mayoría de la tabla (80%), el optimizador prefiere ignorar los índices (debido al coste excesivo de paginación aleatoria por registros dispersos) y opta por leer la tabla secuencialmente de forma directa.

---

## 3. Propuesta y Creación de Índices

Atendiendo a las conclusiones analíticas de selectividad, se aplicó la siguiente arquitectura física de indexación:

1. **Para Consulta 1:** Un **Índice Simple Único** por el campo de identidad unívoca (`correo`).
2. **Para Consulta 2:** Un **Índice Compuesto** que asocie en primera posición `apellido` y en segunda instancia `estado`, cubriendo de forma óptima el filtro multinivel.
3. **Para Consulta 3:** **Ninguno (Evaluación Negativa)**, ya que la creación de un índice sobre una columna de bajísima selectividad (baja variabilidad de estados en el negocio) desperdiciaría espacio de almacenamiento sin reportar beneficios.

```sql
-- 1. Optimización para la consulta de Correo
CREATE UNIQUE INDEX idx_usuarios_correo ON usuarios (correo);

-- 2. Optimización para la consulta compuesta de Apellido y Estado
CREATE INDEX idx_usuarios_apellido_estado ON usuarios (apellido, estado);
