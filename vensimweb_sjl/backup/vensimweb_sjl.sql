-- vensimweb_sjl.sql  ·  Sistema de Gestion de Residuos Solidos SJL
-- Config de graficas (5 subsistemas) + datos reales observados + escenarios simulados guardados

CREATE DATABASE IF NOT EXISTS vensimweb_sjl DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE vensimweb_sjl;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS simulacion_datos;
DROP TABLE IF EXISTS simulaciones;
DROP TABLE IF EXISTS datos_reales;
DROP TABLE IF EXISTS generacion_config;
DROP TABLE IF EXISTS recoleccion_config;
DROP TABLE IF EXISTS disposicion_config;
DROP TABLE IF EXISTS valorizacion_config;
DROP TABLE IF EXISTS financiamiento_config;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE generacion_config (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    nivel    VARCHAR(100) NOT NULL,
    titulo   VARCHAR(150),
    grupo    VARCHAR(60),
    eje_x    VARCHAR(100) DEFAULT 'Año',
    eje_y    VARCHAR(100),
    unidad   VARCHAR(40),
    color    VARCHAR(20),
    posicion INT
);

CREATE TABLE recoleccion_config (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    nivel    VARCHAR(100) NOT NULL,
    titulo   VARCHAR(150),
    grupo    VARCHAR(60),
    eje_x    VARCHAR(100) DEFAULT 'Año',
    eje_y    VARCHAR(100),
    unidad   VARCHAR(40),
    color    VARCHAR(20),
    posicion INT
);

CREATE TABLE disposicion_config (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    nivel    VARCHAR(100) NOT NULL,
    titulo   VARCHAR(150),
    grupo    VARCHAR(60),
    eje_x    VARCHAR(100) DEFAULT 'Año',
    eje_y    VARCHAR(100),
    unidad   VARCHAR(40),
    color    VARCHAR(20),
    posicion INT
);

CREATE TABLE valorizacion_config (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    nivel    VARCHAR(100) NOT NULL,
    titulo   VARCHAR(150),
    grupo    VARCHAR(60),
    eje_x    VARCHAR(100) DEFAULT 'Año',
    eje_y    VARCHAR(100),
    unidad   VARCHAR(40),
    color    VARCHAR(20),
    posicion INT
);

CREATE TABLE financiamiento_config (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    nivel    VARCHAR(100) NOT NULL,
    titulo   VARCHAR(150),
    grupo    VARCHAR(60),
    eje_x    VARCHAR(100) DEFAULT 'Año',
    eje_y    VARCHAR(100),
    unidad   VARCHAR(40),
    color    VARCHAR(20),
    posicion INT
);

CREATE TABLE datos_reales (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    subsistema VARCHAR(40) NOT NULL,
    nivel      VARCHAR(100) NOT NULL,
    anio       INT NOT NULL,
    valor      DOUBLE,
    fuente     VARCHAR(160),
    UNIQUE KEY uq_real (subsistema, nivel, anio)
);

CREATE TABLE simulaciones (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(120) NOT NULL,
    descripcion VARCHAR(255),
    creado      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE simulacion_datos (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    simulacion_id INT NOT NULL,
    nivel         VARCHAR(100) NOT NULL,
    anio          INT NOT NULL,
    valor         DOUBLE,
    FOREIGN KEY (simulacion_id) REFERENCES simulaciones(id) ON DELETE CASCADE
);

INSERT INTO generacion_config (nivel, titulo, grupo, eje_y, unidad, color, posicion) VALUES
('Poblacion', 'Población de SJL', 'Demografía', 'Habitantes', 'Habitantes', '#2F7A6E', 1),
('GPC', 'Generación per cápita', 'Indicador', 'kg/hab/día', 'kg/hab/día', '#C98A1F', 2),
('Generacion bruta', 'Generación bruta total', 'Agregado', 'ton/día', 'ton/día', '#C4502E', 3),
('Generacion organicos', 'Residuos orgánicos', 'Por tipo', 'ton/día', 'ton/día', '#1D9E75', 4),
('Generacion reciclables', 'Residuos reciclables', 'Por tipo', 'ton/día', 'ton/día', '#6F5BA8', 5),
('Generacion no aprovechables', 'Residuos no aprovechables', 'Por tipo', 'ton/día', 'ton/día', '#888780', 6);

INSERT INTO recoleccion_config (nivel, titulo, grupo, eje_y, unidad, color, posicion) VALUES
('cobertura recoleccion', 'Cobertura de recolección', 'Indicador', '%', '%', '#2F7A6E', 1),
('Residuos dispersos', 'Residuos dispersos acumulados', 'Estado', 'ton', 'ton', '#C4502E', 2),
('Flota operativa', 'Flota operativa total', 'Flota', 'unidades', 'unidades', '#3A2E1F', 3),
('Compactadores', 'Compactadores', 'Flota', 'unidades', 'unidades', '#6F5BA8', 4),
('Volquetes', 'Volquetes', 'Flota', 'unidades', 'unidades', '#C98A1F', 5),
('Barandas', 'Barandas', 'Flota', 'unidades', 'unidades', '#1D9E75', 6);

INSERT INTO disposicion_config (nivel, titulo, grupo, eje_y, unidad, color, posicion) VALUES
('vida util remanente', 'Vida útil remanente', 'Indicador', 'años', 'años', '#2F7A6E', 1),
('Volumen relleno total', 'Volumen total en rellenos', 'Agregado', 'm³', 'm³', '#888780', 2),
('Volumen Portillo', 'Relleno Portillo Grande', 'Por relleno', 'm³', 'm³', '#C98A1F', 3),
('Volumen Huaycoloro', 'Relleno Huaycoloro', 'Por relleno', 'm³', 'm³', '#D85A30', 4),
('costo unit disposicion', 'Costo unitario de disposición', 'Costo', 'US$/ton', 'US$/ton', '#E24B4A', 5);

INSERT INTO valorizacion_config (nivel, titulo, grupo, eje_y, unidad, color, posicion) VALUES
('tasa reciclaje', 'Tasa de reciclaje formal', 'Indicador', '%', '%', '#2F7A6E', 1),
('valorizacion total', 'Toneladas valorizadas', 'Resultado', 'ton/año', 'ton/año', '#1D9E75', 2),
('Recicladores formalizados', 'Recicladores formalizados', 'Actores', 'personas', 'personas', '#6F5BA8', 3),
('ingreso reciclaje', 'Ingreso por reciclaje', 'Económico', 'S//año', 'S//año', '#C98A1F', 4),
('potencial reciclaje', 'Potencial físico de reciclaje', 'Referencia', 'ton/año', 'ton/año', '#888780', 5),
('Discrep reciclaje', 'Brecha potencial vs real', 'Referencia', 'ton/año', 'ton/año', '#C4502E', 6);

INSERT INTO financiamiento_config (nivel, titulo, grupo, eje_y, unidad, color, posicion) VALUES
('presupuesto per capita', 'Presupuesto per cápita', 'Indicador', 'S//hab', 'S//hab', '#6F5BA8', 1),
('Presupuesto disponible', 'Presupuesto disponible', 'Estado', 'S/', 'S/', '#2F7A6E', 2),
('Morosidad', 'Tasa de morosidad', 'Riesgo', '%', '%', '#C4502E', 3),
('recaudacion efectiva', 'Recaudación efectiva', 'Ingreso', 'S//año', 'S//año', '#C98A1F', 4),
('deficit financiero', 'Déficit financiero', 'Riesgo', 'S//año', 'S//año', '#E24B4A', 5);

INSERT INTO datos_reales (subsistema, nivel, anio, valor, fuente) VALUES
('generacion', 'Poblacion', 2019, 1192191.0, 'INEI proyeccion distrital'),
('generacion', 'Poblacion', 2020, 1210178.0, 'INEI proyeccion distrital'),
('generacion', 'Poblacion', 2021, 1227205.0, 'INEI proyeccion distrital'),
('generacion', 'Poblacion', 2022, 1244467.0, 'INEI proyeccion distrital'),
('generacion', 'Poblacion', 2023, 1261967.0, 'INEI proyeccion distrital'),
('generacion', 'GPC', 2019, 0.8972, 'PIGARS SJL 2019-2023'),
('generacion', 'GPC', 2020, 0.9163, 'PIGARS SJL 2019-2023'),
('generacion', 'GPC', 2021, 0.9354, 'PIGARS SJL 2019-2023'),
('generacion', 'GPC', 2022, 0.9545, 'PIGARS SJL 2019-2023'),
('generacion', 'GPC', 2023, 0.9736, 'PIGARS SJL 2019-2023'),
('generacion', 'Generacion bruta', 2019, 996.19, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('generacion', 'Generacion bruta', 2020, 1016.73, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('generacion', 'Generacion bruta', 2021, 1047.54, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('generacion', 'Generacion bruta', 2022, 1068.08, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('generacion', 'Generacion bruta', 2023, 1088.62, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('generacion', 'Generacion organicos', 2019, 498.58, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('generacion', 'Generacion organicos', 2020, 508.86, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('generacion', 'Generacion organicos', 2021, 524.28, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('generacion', 'Generacion organicos', 2022, 534.56, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('generacion', 'Generacion organicos', 2023, 544.84, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('generacion', 'Generacion reciclables', 2019, 301.84, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('generacion', 'Generacion reciclables', 2020, 308.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('generacion', 'Generacion reciclables', 2021, 317.24, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('generacion', 'Generacion reciclables', 2022, 323.4, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('generacion', 'Generacion reciclables', 2023, 329.56, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('generacion', 'Generacion no aprovechables', 2019, 198.85, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('generacion', 'Generacion no aprovechables', 2020, 202.95, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('generacion', 'Generacion no aprovechables', 2021, 209.1, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('generacion', 'Generacion no aprovechables', 2022, 213.2, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('generacion', 'Generacion no aprovechables', 2023, 217.3, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('recoleccion', 'cobertura recoleccion', 2019, 0.3366, 'MML - Gerencia de Servicios a la Ciudad'),
('recoleccion', 'cobertura recoleccion', 2020, 0.655, 'MML - Gerencia de Servicios a la Ciudad'),
('recoleccion', 'cobertura recoleccion', 2021, 0.91, 'MML - Gerencia de Servicios a la Ciudad'),
('recoleccion', 'cobertura recoleccion', 2022, 0.93, 'MML - Gerencia de Servicios a la Ciudad'),
('recoleccion', 'cobertura recoleccion', 2023, 0.95, 'MML - Gerencia de Servicios a la Ciudad'),
('recoleccion', 'Residuos dispersos', 2019, 10890.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('recoleccion', 'Residuos dispersos', 2020, 241190.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('recoleccion', 'Residuos dispersos', 2021, 251271.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('recoleccion', 'Residuos dispersos', 2022, 150367.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('recoleccion', 'Residuos dispersos', 2023, 10201.46, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('recoleccion', 'Flota operativa', 2019, 52.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('recoleccion', 'Flota operativa', 2020, 95.25, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('recoleccion', 'Flota operativa', 2021, 153.78, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('recoleccion', 'Flota operativa', 2022, 228.65, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('recoleccion', 'Flota operativa', 2023, 337.75, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('recoleccion', 'Compactadores', 2019, 28.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('recoleccion', 'Compactadores', 2020, 42.14, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('recoleccion', 'Compactadores', 2021, 62.74, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('recoleccion', 'Compactadores', 2022, 89.81, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('recoleccion', 'Compactadores', 2023, 130.03, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('recoleccion', 'Volquetes', 2019, 15.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('recoleccion', 'Volquetes', 2020, 31.59, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('recoleccion', 'Volquetes', 2021, 53.49, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('recoleccion', 'Volquetes', 2022, 82.31, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('recoleccion', 'Volquetes', 2023, 121.41, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('recoleccion', 'Barandas', 2019, 9.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('recoleccion', 'Barandas', 2020, 22.09, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('recoleccion', 'Barandas', 2021, 38.79, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('recoleccion', 'Barandas', 2022, 60.46, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('recoleccion', 'Barandas', 2023, 89.78, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('disposicion', 'vida util remanente', 2019, 191.59, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('disposicion', 'vida util remanente', 2020, 81.48, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('disposicion', 'vida util remanente', 2021, 56.17, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('disposicion', 'vida util remanente', 2022, 59.63, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('disposicion', 'vida util remanente', 2023, 63.34, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('disposicion', 'Volumen relleno total', 2019, 38000000.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('disposicion', 'Volumen relleno total', 2020, 38589797.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('disposicion', 'Volumen relleno total', 2021, 39389846.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('disposicion', 'Volumen relleno total', 2022, 40237639.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('disposicion', 'Volumen relleno total', 2023, 41070053.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('disposicion', 'Volumen Portillo', 2019, 22000000.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('disposicion', 'Volumen Portillo', 2020, 22356368.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('disposicion', 'Volumen Portillo', 2021, 22849400.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('disposicion', 'Volumen Portillo', 2022, 23373465.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('disposicion', 'Volumen Portillo', 2023, 23887534.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('disposicion', 'Volumen Huaycoloro', 2019, 16000000.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('disposicion', 'Volumen Huaycoloro', 2020, 16233429.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('disposicion', 'Volumen Huaycoloro', 2021, 16540446.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('disposicion', 'Volumen Huaycoloro', 2022, 16864174.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('disposicion', 'Volumen Huaycoloro', 2023, 17182518.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('disposicion', 'costo unit disposicion', 2019, 16.07, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('disposicion', 'costo unit disposicion', 2020, 16.46, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('disposicion', 'costo unit disposicion', 2021, 16.95, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('disposicion', 'costo unit disposicion', 2022, 17.46, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('disposicion', 'costo unit disposicion', 2023, 17.96, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('valorizacion', 'tasa reciclaje', 2019, 0.0696, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('valorizacion', 'tasa reciclaje', 2020, 0.0861, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('valorizacion', 'tasa reciclaje', 2021, 0.1115, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('valorizacion', 'tasa reciclaje', 2022, 0.1377, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('valorizacion', 'tasa reciclaje', 2023, 0.161, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('valorizacion', 'valorizacion total', 2019, 29784.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('valorizacion', 'valorizacion total', 2020, 36576.94, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('valorizacion', 'valorizacion total', 2021, 47982.06, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('valorizacion', 'valorizacion total', 2022, 60078.7, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('valorizacion', 'valorizacion total', 2023, 71140.66, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('valorizacion', 'Recicladores formalizados', 2019, 680.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('valorizacion', 'Recicladores formalizados', 2020, 835.09, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('valorizacion', 'Recicladores formalizados', 2021, 1095.48, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('valorizacion', 'Recicladores formalizados', 2022, 1371.66, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('valorizacion', 'Recicladores formalizados', 2023, 1624.21, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('valorizacion', 'ingreso reciclaje', 2019, 25316400.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('valorizacion', 'ingreso reciclaje', 2020, 31090398.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('valorizacion', 'ingreso reciclaje', 2021, 40784756.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('valorizacion', 'ingreso reciclaje', 2022, 51066893.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('valorizacion', 'ingreso reciclaje', 2023, 60469559.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('financiamiento', 'presupuesto per capita', 2019, 36.1, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('financiamiento', 'presupuesto per capita', 2020, 70.25, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('financiamiento', 'presupuesto per capita', 2021, 91.75, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('financiamiento', 'presupuesto per capita', 2022, 121.12, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('financiamiento', 'presupuesto per capita', 2023, 160.4, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('financiamiento', 'Presupuesto disponible', 2019, 43000000.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('financiamiento', 'Presupuesto disponible', 2020, 84680741.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('financiamiento', 'Presupuesto disponible', 2021, 111930244.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('financiamiento', 'Presupuesto disponible', 2022, 149532905.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('financiamiento', 'Presupuesto disponible', 2023, 200416833.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('financiamiento', 'Morosidad', 2019, 0.8364, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('financiamiento', 'Morosidad', 2020, 0.7966, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('financiamiento', 'Morosidad', 2021, 0.6816, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('financiamiento', 'Morosidad', 2022, 0.5919, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('financiamiento', 'Morosidad', 2023, 0.5442, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('financiamiento', 'recaudacion efectiva', 2019, 25211088.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('financiamiento', 'recaudacion efectiva', 2020, 33783818.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('financiamiento', 'recaudacion efectiva', 2021, 51563044.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('financiamiento', 'recaudacion efectiva', 2022, 63501029.0, 'Estimacion municipal SJL (calibracion 2019-2023)'),
('financiamiento', 'recaudacion efectiva', 2023, 68990466.0, 'Estimacion municipal SJL (calibracion 2019-2023)');

