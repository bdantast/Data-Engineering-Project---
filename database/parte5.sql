CREATE TABLE IF NOT EXISTS vendas (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id),
    vendedor_id INTEGER REFERENCES vendedores(id),
    data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valor_total NUMERIC(12,2) NOT NULL,
    desconto NUMERIC(10,2) DEFAULT 0,
    forma_pagamento VARCHAR(30),
    status VARCHAR(20) DEFAULT 'Concluida'
);

-- Tabela de Itens da Venda

