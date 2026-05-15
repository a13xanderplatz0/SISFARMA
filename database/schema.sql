-- Creación de la base de datos de Farmacia (PostgreSQL)

CREATE TABLE CATEGORIA (
    id_categoria SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

CREATE TABLE PROVEEDOR (
    id_proveedor SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    telefono VARCHAR(20),
    direccion VARCHAR(255)
);

CREATE TABLE CLIENTE (
    id_cliente SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    telefono VARCHAR(20),
    direccion VARCHAR(255)
);

CREATE TABLE USUARIO (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    rol VARCHAR(50) NOT NULL,
    contrasena VARCHAR(255),
    id_supervisor INT REFERENCES USUARIO(id_usuario) ON DELETE SET NULL
);

CREATE TABLE MEDICAMENTO (
    id_medicamento SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    precio NUMERIC(10,2) NOT NULL,
    descripcion TEXT,
    id_categoria INT NOT NULL REFERENCES CATEGORIA(id_categoria) ON DELETE RESTRICT
);

CREATE TABLE LOTE (
    numero_lote VARCHAR(50) NOT NULL,
    id_medicamento INT NOT NULL REFERENCES MEDICAMENTO(id_medicamento) ON DELETE RESTRICT,
    fecha_vencimiento DATE,
    PRIMARY KEY (numero_lote, id_medicamento)
);

CREATE TABLE INVENTARIO (
    id_inventario SERIAL PRIMARY KEY,
    stock INT NOT NULL,
    stock_minimo INT,
    numero_lote VARCHAR(50) NOT NULL,
    id_medicamento INT NOT NULL,
    FOREIGN KEY (numero_lote, id_medicamento) REFERENCES LOTE(numero_lote, id_medicamento) ON DELETE RESTRICT
);

CREATE TABLE ALERTA (
    id_alerta SERIAL PRIMARY KEY,
    mensaje TEXT,
    tipo VARCHAR(50),
    id_medicamento INT NOT NULL REFERENCES MEDICAMENTO(id_medicamento) ON DELETE CASCADE,
    id_inventario INT REFERENCES INVENTARIO(id_inventario) ON DELETE SET NULL
);

CREATE TABLE VENTA (
    id_venta SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    total NUMERIC(10,2) NOT NULL,
    id_cliente INT NOT NULL REFERENCES CLIENTE(id_cliente) ON DELETE RESTRICT,
    id_usuario INT NOT NULL REFERENCES USUARIO(id_usuario) ON DELETE RESTRICT
);

CREATE TABLE DETALLE_VENTA (
    id_detalle_venta SERIAL PRIMARY KEY,
    cantidad INT NOT NULL,
    precio_unitario NUMERIC(10,2) NOT NULL,
    id_venta INT NOT NULL REFERENCES VENTA(id_venta) ON DELETE CASCADE,
    id_medicamento INT NOT NULL REFERENCES MEDICAMENTO(id_medicamento) ON DELETE RESTRICT
);

CREATE TABLE PAGO (
    id_pago SERIAL PRIMARY KEY,
    monto NUMERIC(10,2) NOT NULL,
    metodo VARCHAR(50) NOT NULL,
    id_venta INT NOT NULL UNIQUE REFERENCES VENTA(id_venta) ON DELETE CASCADE
);

CREATE TABLE HISTORIAL_VENTA (
    id_historial SERIAL PRIMARY KEY,
    descripcion TEXT,
    id_cliente INT NOT NULL REFERENCES CLIENTE(id_cliente) ON DELETE CASCADE,
    id_venta INT NOT NULL REFERENCES VENTA(id_venta) ON DELETE CASCADE
);

CREATE TABLE COMPRA (
    id_compra SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente' CHECK (estado IN ('pendiente','recibida','anulada')),
    id_proveedor INT NOT NULL REFERENCES PROVEEDOR(id_proveedor) ON DELETE RESTRICT,
    id_usuario INT NOT NULL REFERENCES USUARIO(id_usuario) ON DELETE RESTRICT
);

CREATE TABLE DETALLE_COMPRA (
    id_detalle_compra SERIAL PRIMARY KEY,
    precio NUMERIC(10,2) NOT NULL,
    cantidad INT NOT NULL,
    id_compra INT NOT NULL REFERENCES COMPRA(id_compra) ON DELETE CASCADE,
    id_medicamento INT NOT NULL REFERENCES MEDICAMENTO(id_medicamento) ON DELETE RESTRICT
);

CREATE TABLE REPORTE (
    id_reporte SERIAL PRIMARY KEY,
    tipo VARCHAR(100) NOT NULL,
    fecha_generacion DATE,
    id_usuario INT NOT NULL REFERENCES USUARIO(id_usuario) ON DELETE RESTRICT
);
