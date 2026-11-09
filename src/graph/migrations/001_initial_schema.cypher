// Schema inicial para a demonstração acadêmica.
CREATE CONSTRAINT document_id_unique IF NOT EXISTS
FOR (n:Document) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS
FOR (n:Chunk) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT entity_id_unique IF NOT EXISTS
FOR (n:Entity) REQUIRE n.id IS UNIQUE;

CREATE INDEX document_uri_idx IF NOT EXISTS
FOR (n:Document) ON (n.uri);

CREATE INDEX entity_type_idx IF NOT EXISTS
FOR (n:Entity) ON (n.entity_type);

CREATE FULLTEXT INDEX chunk_text_fulltext IF NOT EXISTS
FOR (n:Chunk) ON EACH [n.text];

CREATE VECTOR INDEX chunk_embedding_vector IF NOT EXISTS
FOR (n:Chunk) ON n.embedding
OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}};
