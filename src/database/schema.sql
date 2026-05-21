

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
(1, 'Carlos Mendoza', 'Administrador', '$2y$10$E9dfX8yKj92...', NULL),
(2, 'Ana Gómez', 'Farmacéutico', '$2y$10$R7tY1vOpQm3...', 1),
(3, 'Luis Torres', 'Farmacéutico', '$2y$10$Z4vWp2nLm90...', 1),
(4, 'María Delgado', 'Farmacéutico', '$2y$10$X9wK2bN1mOp...', 1),
(5, 'Jorge Ramírez', 'Administrador', '$2y$10$P3qL7vT5xZm...', 2);

INSERT INTO PROVEEDOR (id_proveedor, nombre, telefono, direccion) VALUES
(1, 'Droguería FarmaSalud S.A.', '+51 987654321', 'Av. De la Salud 123, Lima'),
(2, 'Laboratorios Medicor', '+51 912345678', 'Calle Industrial 456, Arequipa'),
(3, 'Distribuidora BioGénesis', '+51 934567890', 'Jr. Los Olivos 789, Trujillo'),
(4, 'PharmaNorte Perú', '+51 945678123', 'Av. Central 990, Chiclayo'),
(5, 'Suministros Médicos Globales', '+51 956789456', 'Calle Las Magnolias 105, Cusco');

INSERT INTO COMPRA (id_compra, fecha, estado, id_proveedor, id_usuario) VALUES
(1, '2026-05-10', 'recibida', 1, 1),   -- Compra a FarmaSalud registrada por Carlos
(2, '2026-05-18', 'pendiente', 2, 2),  -- Compra a Medicor registrada por Ana
(3, '2026-05-21', 'anulada', 3, 3),    -- Compra a BioGénesis registrada por Luis
(4, '2026-05-22', 'recibida', 4, 4),   -- Compra a PharmaNorte registrada por María
(5, '2026-05-23', 'pendiente', 5, 2);  -- Compra a Suministros Globales registrada por Ana