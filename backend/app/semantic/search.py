# Purpose:
# This file contains the core business logic for executing semantic similarity searches
# against the pgvector columns in the database.
#
# Why this file exists:
# It centralizes the initialization of the SentenceTransformer model and the SQLAlchemy
# query logic. Loading the ML model here ensures it only loads into memory once.
#
# In simple terms:
# This script takes a user's typed question, turns it into a mathematical vector, 
# and asks the database to find the closest matching datasets.

from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from app.db.semantic_models import DatasetRegistry

# Load model globally so it doesn't reload on every API request
model = SentenceTransformer("all-MiniLM-L6-v2")

def find_relevant_datasets(db: Session, user_query: str, limit: int = 3):
    # Convert the plain text query to a 384-dimensional vector
    query_embedding = model.encode(user_query, normalize_embeddings=True).tolist()
    
    # Perform L2 distance search (<-> operator in pgvector)
    results = db.query(DatasetRegistry).order_by(
        DatasetRegistry.embedding.l2_distance(query_embedding)
    ).limit(limit).all()
    
    return results