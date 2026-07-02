CREATE DATABASE IF NOT EXISTS vensimweb_sjl;
USE vensimweb_sjl;

CREATE TABLE generacion_config (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    nivel    VARCHAR(100) NOT NULL,
    titulo   VARCHAR(150),
    eje_x    VARCHAR(100),
    eje_y    VARCHAR(100),
    color    VARCHAR(20),
    posicion INT
);

CREATE TABLE recoleccion_config (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    nivel    VARCHAR(100) NOT NULL,
    titulo   VARCHAR(150),
    eje_x    VARCHAR(100),
    eje_y    VARCHAR(100),
    color    VARCHAR(20),
    posicion INT
);

CREATE TABLE disposicion_config (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    nivel    VARCHAR(100) NOT NULL,
    titulo   VARCHAR(150),
    eje_x    VARCHAR(100),
    eje_y    VARCHAR(100),
    color    VARCHAR(20),
    posicion INT
);

CREATE TABLE valorizacion_config (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    nivel    VARCHAR(100) NOT NULL,
    titulo   VARCHAR(150),
    eje_x    VARCHAR(100),
    eje_y    VARCHAR(100),
    color    VARCHAR(20),
    posicion INT
);

CREATE TABLE financiamiento_config (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    nivel    VARCHAR(100) NOT NULL,
    titulo   VARCHAR(150),
    eje_x    VARCHAR(100),
    eje_y    VARCHAR(100),
    color    VARCHAR(20),
    posicion INT
);

-- Datos de ejemplo
INSERT INTO generacion_config (nivel, titulo, eje_x, eje_y, color, posicion) VALUES
('Poblacion',                   'Población de SJL',                        'Año', 'Habitantes', '#2F7A6E', 1),
('GPC',                         'Generación per cápita',                   'Año', 'kg/hab/día', '#C98A1F', 2),
('generacion_bruta',            'Generación bruta total',                  'Año', 'ton/día',    '#C4502E', 3),
('Generacion_organicos',        'Generación de residuos orgánicos',        'Año', 'ton/día',    '#1D9E75', 4),
('Generacion_reciclables',      'Generación de residuos reciclables',      'Año', 'ton/día',    '#6F5BA8', 5),
('Generacion_no_aprovechables', 'Generación de residuos no aprovechables', 'Año', 'ton/día',    '#888780', 6);

INSERT INTO recoleccion_config (nivel, titulo, eje_x, eje_y, color, posicion) VALUES
('Residuos_dispersos',     'Residuos dispersos acumulados', 'Año', 'ton',        '#C4502E', 1),
('cobertura_recoleccion',  'Cobertura de recolección',      'Año', '%',          '#2F7A6E', 2),
('Compactadores',          'Flota: Compactadores',          'Año', 'unidades',   '#6F5BA8', 3),
('Volquetes',              'Flota: Volquetes',              'Año', 'unidades',   '#C98A1F', 4),
('Barandas',               'Flota: Barandas',               'Año', 'unidades',   '#1D9E75', 5),
('Flota_operativa',        'Flota operativa total',         'Año', 'unidades',   '#3A2E1F', 6);

INSERT INTO disposicion_config (nivel, titulo, eje_x, eje_y, color, posicion) VALUES
('Volumen_relleno_total',   'Volumen total en rellenos',     'Año', 'm³',        '#888780', 1),
('Volumen_Portillo',        'Relleno Portillo Grande',       'Año', 'm³',        '#C98A1F', 2),
('Volumen_Huaycoloro',      'Relleno Huaycoloro',            'Año', 'm³',        '#D85A30', 3),
('vida_util_remanente',     'Vida útil remanente',           'Año', 'años',      '#2F7A6E', 4),
('costo_unit_disposicion',  'Costo unitario de disposición', 'Año', 'US$/ton',   '#E24B4A', 5);

INSERT INTO valorizacion_config (nivel, titulo, eje_x, eje_y, color, posicion) VALUES
('Recicladores_formalizados', 'Recicladores formalizados',         'Año', 'personas',  '#6F5BA8', 1),
('valorizacion_total',        'Toneladas valorizadas',              'Año', 'ton/año',   '#1D9E75', 2),
('tasa_reciclaje',            'Tasa de reciclaje formal',           'Año', '%',         '#2F7A6E', 3),
('ingreso_reciclaje',         'Ingreso por reciclaje',              'Año', 'S//año',    '#C98A1F', 4),
('potencial_reciclaje',       'Potencial físico de reciclaje',      'Año', 'ton/año',   '#888780', 5),
('brecha_reciclaje',          'Brecha entre potencial y realidad',  'Año', 'ton/año',   '#C4502E', 6);

INSERT INTO financiamiento_config (nivel, titulo, eje_x, eje_y, color, posicion) VALUES
('Presupuesto_disponible',  'Presupuesto disponible',       'Año', 'S/',        '#2F7A6E', 1),
('Morosidad',               'Tasa de morosidad',            'Año', '%',         '#C4502E', 2),
('recaudacion_efectiva',    'Recaudación efectiva',         'Año', 'S//año',    '#C98A1F', 3),
('deficit_financiero',      'Déficit financiero',           'Año', 'S//año',    '#E24B4A', 4),
('presupuesto_per_capita',  'Presupuesto per cápita',       'Año', 'S//hab',    '#6F5BA8', 5);
