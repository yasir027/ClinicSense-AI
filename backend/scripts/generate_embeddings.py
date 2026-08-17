import os

import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


load_dotenv()

model = SentenceTransformer("all-MiniLM-L6-v2")

connection = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", "5432")),
    dbname=os.getenv("POSTGRES_DB", "clinicsense"),
    user=os.getenv("POSTGRES_USER", "clinicsense"),
    password=os.getenv("POSTGRES_PASSWORD", "devpassword"),
)

cursor = connection.cursor()


def vector_literal(values: list[float]) -> str:
    return "[" + ",".join(str(value) for value in values) + "]"


cursor.execute("""
    SELECT id, description
    FROM dataset_registry
    WHERE embedding IS NULL
""")

dataset_rows = cursor.fetchall()

for dataset_id, description in dataset_rows:
    embedding = model.encode(description, normalize_embeddings=True)
    cursor.execute(
        """
        UPDATE dataset_registry
        SET embedding = %s::vector
        WHERE id = %s
        """,
        (vector_literal(embedding.tolist()), dataset_id),
    )


cursor.execute("""
    SELECT id, term, definition
    FROM business_glossary
    WHERE embedding IS NULL
""")

glossary_rows = cursor.fetchall()

for glossary_id, term, definition in glossary_rows:
    text = f"{term}: {definition}"
    embedding = model.encode(text, normalize_embeddings=True)
    cursor.execute(
        """
        UPDATE business_glossary
        SET embedding = %s::vector
        WHERE id = %s
        """,
        (vector_literal(embedding.tolist()), glossary_id),
    )


connection.commit()

print(f"Dataset embeddings created: {len(dataset_rows)}")
print(f"Glossary embeddings created: {len(glossary_rows)}")

cursor.close()
connection.close()