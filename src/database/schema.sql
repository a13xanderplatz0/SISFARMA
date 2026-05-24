

CREATE TABLE CATEGORIA (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE PROVEEDOR (
    id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    telefono VARCHAR(20),
    direccion VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE CLIENTE (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    telefono VARCHAR(20),
    direccion VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE USUARIO (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    rol VARCHAR(50) NOT NULL,
    contrasena VARCHAR(255),
    id_supervisor INT,
    CONSTRAINT fk_usuario_supervisor
        FOREIGN KEY (id_supervisor) REFERENCES USUARIO(id_usuario) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE MEDICAMENTO (
    id_medicamento INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    descripcion TEXT,
    id_categoria INT NOT NULL,
    CONSTRAINT fk_medicamento_categoria
        FOREIGN KEY (id_categoria) REFERENCES CATEGORIA(id_categoria) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE LOTE (
    numero_lote VARCHAR(50) NOT NULL,
    id_medicamento INT NOT NULL,
    fecha_vencimiento DATE,
    PRIMARY KEY (numero_lote, id_medicamento),
    CONSTRAINT fk_lote_medicamento
        FOREIGN KEY (id_medicamento) REFERENCES MEDICAMENTO(id_medicamento) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE INVENTARIO (
    id_inventario INT AUTO_INCREMENT PRIMARY KEY,
    stock INT NOT NULL,
    stock_minimo INT,
    numero_lote VARCHAR(50) NOT NULL,
    id_medicamento INT NOT NULL,
    CONSTRAINT fk_inventario_lote
        FOREIGN KEY (numero_lote, id_medicamento) REFERENCES LOTE(numero_lote, id_medicamento) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE ALERTA (
    id_alerta INT AUTO_INCREMENT PRIMARY KEY,
    mensaje TEXT,
    tipo VARCHAR(50),
    id_medicamento INT NOT NULL,
    id_inventario INT,
    CONSTRAINT fk_alerta_medicamento
        FOREIGN KEY (id_medicamento) REFERENCES MEDICAMENTO(id_medicamento) ON DELETE CASCADE,
    CONSTRAINT fk_alerta_inventario
        FOREIGN KEY (id_inventario) REFERENCES INVENTARIO(id_inventario) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE VENTA (
    id_venta INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    id_cliente INT NOT NULL,
    id_usuario INT NOT NULL,
    CONSTRAINT fk_venta_cliente
        FOREIGN KEY (id_cliente) REFERENCES CLIENTE(id_cliente) ON DELETE RESTRICT,
    CONSTRAINT fk_venta_usuario
        FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE DETALLE_VENTA (
    id_detalle_venta INT AUTO_INCREMENT PRIMARY KEY,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    id_venta INT NOT NULL,
    id_medicamento INT NOT NULL,
    CONSTRAINT fk_detalle_venta_venta
        FOREIGN KEY (id_venta) REFERENCES VENTA(id_venta) ON DELETE CASCADE,
    CONSTRAINT fk_detalle_venta_medicamento
        FOREIGN KEY (id_medicamento) REFERENCES MEDICAMENTO(id_medicamento) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE PAGO (
    id_pago INT AUTO_INCREMENT PRIMARY KEY,
    monto DECIMAL(10,2) NOT NULL,
    metodo VARCHAR(50) NOT NULL,
    id_venta INT NOT NULL UNIQUE,
    CONSTRAINT fk_pago_venta
        FOREIGN KEY (id_venta) REFERENCES VENTA(id_venta) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE HISTORIAL_VENTA (
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    descripcion TEXT,
    id_cliente INT NOT NULL,
    id_venta INT NOT NULL,
    CONSTRAINT fk_historial_cliente
        FOREIGN KEY (id_cliente) REFERENCES CLIENTE(id_cliente) ON DELETE CASCADE,
    CONSTRAINT fk_historial_venta
        FOREIGN KEY (id_venta) REFERENCES VENTA(id_venta) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE COMPRA (
    id_compra INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    id_proveedor INT NOT NULL,
    id_usuario INT NOT NULL,
    CONSTRAINT chk_compra_estado CHECK (estado IN ('pendiente', 'recibida', 'anulada')),
    CONSTRAINT fk_compra_proveedor
        FOREIGN KEY (id_proveedor) REFERENCES PROVEEDOR(id_proveedor) ON DELETE RESTRICT,
    CONSTRAINT fk_compra_usuario
        FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE DETALLE_COMPRA (
    id_detalle_compra INT AUTO_INCREMENT PRIMARY KEY,
    precio DECIMAL(10,2) NOT NULL,
    cantidad INT NOT NULL,
    id_compra INT NOT NULL,
    id_medicamento INT NOT NULL,
    CONSTRAINT fk_detalle_compra_compra
        FOREIGN KEY (id_compra) REFERENCES COMPRA(id_compra) ON DELETE CASCADE,
    CONSTRAINT fk_detalle_compra_medicamento
        FOREIGN KEY (id_medicamento) REFERENCES MEDICAMENTO(id_medicamento) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE REPORTE (
    id_reporte INT AUTO_INCREMENT PRIMARY KEY,
    tipo VARCHAR(100) NOT NULL,
    fecha_generacion DATE,
    id_usuario INT NOT NULL,
    CONSTRAINT fk_reporte_usuario
        FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO USUARIO (id_usuario, nombre, rol, contrasena, id_supervisor) VALUES
(1, 'Juan Perez', 'Administrador', '1234', NULL),
(2, 'Ana Gómez', 'Administrador', 'AnaG12', NULL),
(3, 'Maria Torres', 'Farmacéutico', 'MariaT12', 1),
(4, 'María Delgado', 'Farmacéutico', 'MariaD34', 1),
(5, 'Jorge Ramírez', 'Farmacéutico', 'JorgeR31', 2);

INSERT INTO PROVEEDOR (id_proveedor, nombre, telefono, direccion) VALUES
(1, 'Laboratorios FarmaSalud S.A.', '+51 987654321', 'Av. De la Salud 123, Lima'),
(2, 'Laboratorios Medicor', '+51 912345678', 'Calle Industrial 456, Arequipa'),
(3, 'Distribuidora BioGénesis', '+51 934567890', 'Jr. Los Olivos 789, Trujillo'),
(4, 'PharmaNorte Perú', '+51 945678123', 'Av. Central 990, Chiclayo'),
(5, 'Suministros Médicos Globales', '+51 956789456', 'Calle Las Magnolias 105, Cusco');

INSERT INTO CATEGORIA (nombre) VALUES
('Analgesicos'),
('Antibioticos'),
('Antiinflamatorios'),
('Vitaminas'),
('Jarabes');

INSERT INTO MEDICAMENTO (nombre, precio, descripcion, id_categoria) VALUES
('Paracetamol 500mg', 5.50, 'Alivia dolor y fiebre', 1),
('Amoxicilina 500mg', 12.90, 'Antibiótico de amplio espectro', 2),
('Ibuprofeno 400mg', 8.70, 'Antiinflamatorio y analgésico', 3),
('Vitamina C', 15.00, 'Suplemento vitamínico', 4),
('Jarabe para la tos', 18.50, 'Jarabe expectorante', 5);

INSERT INTO LOTE (numero_lote, id_medicamento, fecha_vencimiento) VALUES
('LOT001', 1, '2027-05-10'),
('LOT002', 2, '2026-12-01'),
('LOT003', 3, '2027-03-15'),
('LOT004', 4, '2028-01-20'),
('LOT005', 5, '2026-11-30');

INSERT INTO INVENTARIO (stock, stock_minimo, numero_lote, id_medicamento) VALUES
(100, 20, 'LOT001', 1),
(50, 10, 'LOT002', 2),
(75, 15, 'LOT003', 3),
(120, 25, 'LOT004', 4),
(40, 10, 'LOT005', 5);

INSERT INTO CLIENTE (nombre, telefono, direccion) VALUES
('Ana López', '922334455', 'Av. Larco 456, Apt 301'),
('Pedro Infante', '933445566', 'Calle San Martín 789'),
('Sofía Castro', '944556677', 'Urb. El Sol Mza F Lote 12'),
('Diego Mendoza', '955667788', 'Av. Ejército 1010'),
('Lucía Fernández', '966778899', 'Pasaje Las Flores 14');


INSERT INTO VENTA (fecha, total, id_cliente, id_usuario) VALUES
('2026-05-21', 35.00, 1, 2),
('2026-05-21', 15.80, 2, 2),
('2026-05-21', 120.00, 3, 2),
('2026-05-21', 8.50, 4, 2),
('2026-05-21', 45.20, 5, 2);


INSERT INTO HISTORIAL_VENTA (descripcion, id_cliente, id_venta) VALUES
('Cliente presentó receta médica válida para la compra de antibióticos.', 1, 1),
('Se aplicó un 10% de descuento automático por campaña de adulto mayor.', 2, 2),
('Compra de tratamiento completo para 3 meses. Solicita envío de comprobante al correo.', 3, 3),
('Cliente olvidó su tarjeta de puntos del establecimiento, solicita acumulación manual.', 4, 4),
('Pedido realizado vía telefónica y recogido en mostrador por un familiar.', 5, 5);

UPDATE CLIENTE 
SET telefono = '999111222', direccion = 'Av. Siempre Viva 742'
WHERE id_cliente = 1;


UPDATE INVENTARIO 
SET stock = stock + 50 
WHERE numero_lote = 'LOT002' AND id_medicamento = 2;

UPDATE COMPRA 
SET estado = 'recibida' 
WHERE id_compra = 2;

UPDATE MEDICAMENTO 
SET precio = 6.20, descripcion = 'Alivia dolor moderado, fiebre y malestar general'
WHERE id_medicamento = 1;