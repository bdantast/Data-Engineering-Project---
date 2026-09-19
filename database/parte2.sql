CREATE TABLE IF NOT EXISTS clientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150),
    telefone VARCHAR(20),
    cpf VARCHAR(14),
    cidade VARCHAR(80),
    estado VARCHAR(2),
    data_cadastro DATE DEFAULT CURRENT_DATE
);

-- Tabela de Produtos

