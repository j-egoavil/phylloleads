CREATE TABLE LeadResults (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT REFERENCES companies(id),
    fechadecalculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resultado JSONB,
    score NUMERIC(100,0)
    
);