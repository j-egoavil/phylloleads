-- ============================================================================
-- Schema PostgreSQL para Phylloleads (scrapers + lead scoring)
-- ============================================================================

-- Tabla de empresas base
CREATE TABLE IF NOT EXISTS companies (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    url VARCHAR(1000),
    nit VARCHAR(100),
    rues VARCHAR(100),
    city VARCHAR(200),
    country VARCHAR(100) DEFAULT 'Colombia',
    is_active BOOLEAN DEFAULT true,
    status VARCHAR(50),
    company_size VARCHAR(50),
    search_niche VARCHAR(200),
    industry VARCHAR(100),
    employee_count INT,
    annual_revenue NUMERIC(15,2),
    email VARCHAR(255),
    website VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scraped_at TIMESTAMP,
    UNIQUE(url)
);

-- Tabla de detalles enriquecidos de empresas (Google Maps, Páginas Amarillas, etc.)
CREATE TABLE IF NOT EXISTS company_details (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT UNIQUE REFERENCES companies(id) ON DELETE CASCADE,
    phone VARCHAR(50),
    website VARCHAR(500),
    address TEXT,
    latitude NUMERIC(10,8),
    longitude NUMERIC(11,8),
    google_maps_url VARCHAR(1000),
    source VARCHAR(100),
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de perfiles sociales
CREATE TABLE IF NOT EXISTS social_profiles (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT REFERENCES companies(id) ON DELETE CASCADE,
    platform VARCHAR(50),
    username VARCHAR(255),
    profile_url TEXT,
    followers INT,
    following INT,
    posts INT,
    bio TEXT,
    verified BOOLEAN DEFAULT FALSE,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de fuentes de leads
CREATE TABLE IF NOT EXISTS lead_sources (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT REFERENCES companies(id) ON DELETE CASCADE,
    source_type VARCHAR(50),
    source_url TEXT,
    raw_data JSONB,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de filtros
CREATE TABLE IF NOT EXISTS filters (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    weight INT DEFAULT 1
);

-- Tabla de resultados de filtros
CREATE TABLE IF NOT EXISTS company_filter_results (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT REFERENCES companies(id) ON DELETE CASCADE,
    filter_id BIGINT REFERENCES filters(id) ON DELETE CASCADE,
    passed BOOLEAN,
    score NUMERIC(10,2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de puntuaciones de leads
CREATE TABLE IF NOT EXISTS lead_scores (
    company_id BIGINT PRIMARY KEY REFERENCES companies(id) ON DELETE CASCADE,
    total_score NUMERIC(10,2),
    priority VARCHAR(20),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de contactos
CREATE TABLE IF NOT EXISTS contacts (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT REFERENCES companies(id) ON DELETE CASCADE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    position VARCHAR(150),
    email VARCHAR(255),
    phone VARCHAR(50),
    linkedin_url TEXT
);

-- Tabla de resultados de scoring (histórico)
CREATE TABLE IF NOT EXISTS lead_results (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT REFERENCES companies(id) ON DELETE CASCADE,
    fechadecalculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resultado JSONB,
    score NUMERIC(10,2)
);

-- ============================================================================
-- ÍNDICES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);
CREATE INDEX IF NOT EXISTS idx_companies_email ON companies(email);
CREATE INDEX IF NOT EXISTS idx_companies_city ON companies(city);
CREATE INDEX IF NOT EXISTS idx_companies_niche ON companies(search_niche);
CREATE INDEX IF NOT EXISTS idx_companies_active ON companies(is_active);
CREATE INDEX IF NOT EXISTS idx_company_details_phone ON company_details(phone);
CREATE INDEX IF NOT EXISTS idx_company_details_website ON company_details(website);
CREATE INDEX IF NOT EXISTS idx_lead_results_company_id ON lead_results(company_id);
CREATE INDEX IF NOT EXISTS idx_lead_results_score ON lead_results(score);

-- ============================================================================
-- Datos iniciales de ejemplo
-- ============================================================================

-- Insertar empresa de prueba
INSERT INTO companies (name, city, email, status, is_active, company_size)
VALUES ('Veterinaria Test', 'Bogotá', 'test@vet.com', 'active', true, 'small')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- FIN DEL SCHEMA
-- ============================================================================
