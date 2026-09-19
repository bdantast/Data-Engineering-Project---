CREATE TABLE IF NOT EXISTS vendedores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    regiao VARCHAR(60),
    data_admissao DATE DEFAULT CURRENT_DATE
);

-- Tabela de Vendas

