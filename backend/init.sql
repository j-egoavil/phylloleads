CREATE TABLE companies (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255),
    website VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    city VARCHAR(100),
    country VARCHAR(100),
    industry VARCHAR(100),
    employee_count INT,
    annual_revenue NUMERIC(15,2),
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
CREATE INDEX idx_social_username ON social_profiles(username);
CREATE INDEX idx_lead_scores_priority ON lead_scores(priority);