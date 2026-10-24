import sys
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')

print("Loading all-MiniLM-L6-v2 embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "neo4jpassword"))

def create_vector_index(session):
    print("Ensuring vector index exists...")
    index_query = """
    CREATE VECTOR INDEX session_embeddings IF NOT EXISTS
    FOR (s:Session) ON (s.embedding)
    OPTIONS {indexConfig: {
      `vector.dimensions`: 384,
      `vector.similarity_function`: 'cosine'
    }}
    """
    session.run(index_query)

def generate_embeddings():
    with driver.session() as session:
        create_vector_index(session)
        
        print("Fetching Session nodes missing embeddings in chunks...", flush=True)
        
        # Process in chunks of 5000 to avoid loading 500MB+ into RAM at once
        while True:
            fetch_query = "MATCH (s:Session) WHERE s.embedding IS NULL RETURN elementId(s) AS id, s.patient_utterance AS p_text, s.therapist_utterance AS t_text LIMIT 5000"
            results = session.run(fetch_query).data()
            
            if not results:
                print("All sessions now have embeddings!", flush=True)
                break
                
            print(f"Generating embeddings for batch of {len(results)} sessions...", flush=True)
            
            update_query = """
            UNWIND $batch AS row
            MATCH (s) WHERE elementId(s) = row.id
            SET s.embedding = row.embedding
            """
            
            batch_size = 500
            for i in range(0, len(results), batch_size):
                chunk = results[i:i+batch_size]
                texts = [str(r['p_text'] or "") + " " + str(r['t_text'] or "") for r in chunk]
                
                vectors = model.encode(texts, batch_size=128, show_progress_bar=False).tolist()
                
                update_data = [{"id": r['id'], "embedding": v} for r, v in zip(chunk, vectors)]
                session.run(update_query, {"batch": update_data})
                print(f"  Processed {min(i+batch_size, len(results))}/{len(results)} in this chunk", flush=True)

if __name__ == "__main__":
    generate_embeddings()
    driver.close()
    print("Done!")

