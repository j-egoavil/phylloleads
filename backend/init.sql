-- Schema PostgreSQL para Phylloleads (scrapers + lead scoring)

CREATE TABLE companies (
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
CREATE TABLE company_details (
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

CREATE TABLE social_profiles (
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
CREATE TABLE lead_sources (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT REFERENCES companies(id) ON DELETE CASCADE,
    source_type VARCHAR(50),
    source_url TEXT,
    raw_data JSONB,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE filters (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    weight INT DEFAULT 1
);
CREATE TABLE company_filter_results (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT REFERENCES companies(id) ON DELETE CASCADE,
    filter_id BIGINT REFERENCES filters(id) ON DELETE CASCADE,
    passed BOOLEAN,
    score NUMERIC(10,2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE lead_scores (
    company_id BIGINT PRIMARY KEY REFERENCES companies(id) ON DELETE CASCADE,
    total_score NUMERIC(10,2),
    priority VARCHAR(20),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE contacts (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT REFERENCES companies(id) ON DELETE CASCADE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    position VARCHAR(150),
    email VARCHAR(255),
    phone VARCHAR(50),
    linkedin_url TEXT
);
CREATE INDEX idx_companies_name ON companies(name);
CREATE INDEX idx_companies_email ON companies(email);
CREATE INDEX idx_companies_city ON companies(city);
CREATE INDEX idx_companies_niche ON companies(search_niche);
CREATE INDEX idx_companies_active ON companies(is_active);
CREATE INDEX idx_company_details_phone ON company_details(phone);
CREATE INDEX idx_company_details_website ON company_details(website);
CREATE INDEX idx_social_username ON social_profiles(username);
CREATE INDEX idx_lead_scores_priority ON lead_scores(priority);