# rag/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import chromadb
import logging
import requests # Importez requests

# --- Configuration et Initialisation (inchangées) ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

try:
    logger.info("Chargement du modèle BGE-M3...")
    model = SentenceTransformer('BAAI/bge-m3')
    logger.info("Modèle BGE-M3 chargé.")
except Exception as e:
    logger.error(f"Erreur chargement modèle: {e}")
    model = None

try:
    logger.info("Connexion à ChromaDB...")
    chroma_client = chromadb.HttpClient(host='db', port=8000)
    collection = chroma_client.get_or_create_collection(name="jackbot_collection")
    logger.info("Connecté à ChromaDB.")
except Exception as e:
    logger.error(f"Erreur connexion ChromaDB: {e}")
    collection = None

OLLAMA_API_URL = "http://ollama:11434/api/chat" # URL pour contacter Ollama en interne

# --- Modèles de données Pydantic ---
class Document(BaseModel):
    id: str
    text: str

class ChatQuery(BaseModel):
    text: str
    system_prompt: str # On reçoit le system prompt du frontend

# --- Endpoints ---

# Cet endpoint reste utile pour ajouter des documents à votre base
@app.post("/api/add-document")
async def add_document(doc: Document):
    # ... (code inchangé)
    if not model or not collection:
        raise HTTPException(status_code=503, detail="Service non initialisé.")
    try:
        embedding = model.encode(doc.text).tolist()
        collection.add(embeddings=[embedding], documents=[doc.text], ids=[doc.id])
        logger.info(f"Document ajouté: {doc.id}")
        return {"status": "success", "id": doc.id}
    except Exception as e:
        logger.error(f"Erreur ajout document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === LE NOUVEL ENDPOINT CENTRAL POUR LE CHAT RAG ===
@app.post("/api/ask-jackbot")
async def ask_jackbot(query: ChatQuery):
    if not model or not collection:
        raise HTTPException(status_code=503, detail="Service non initialisé.")

    try:
        # --- ÉTAPE 1: RÉCUPÉRATION (Retrieval) ---
        logger.info(f"Recherche de documents pour: '{query.text}'")
        query_embedding = model.encode(query.text).tolist()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3 # Récupérer les 3 documents les plus pertinents
        )
        
        retrieved_docs = results.get('documents', [[]])[0]
        context = "\n".join(retrieved_docs)
        logger.info(f"Contexte trouvé:\n{context}")

        # --- ÉTAPE 2: AUGMENTATION ---
        # On construit le message pour l'utilisateur avec le contexte
        augmented_user_prompt = f"""
Voici des informations extraites de ma base de connaissances qui pourraient être pertinentes :
---
{context}
---
En te basant **strictement** sur ces informations et en respectant ta persona, réponds à la question suivante : {query.text}
"""
        
        # --- ÉTAPE 3: GÉNÉRATION ---
        logger.info("Envoi de la requête augmentée à Ollama...")
        
        ollama_payload = {
            "model": "qwen:0.5b", # Assurez-vous que ce modèle est téléchargé dans Ollama
            "messages": [
                {"role": "system", "content": query.system_prompt},
                {"role": "user", "content": augmented_user_prompt}
            ],
            "stream": False
        }

        response = requests.post(OLLAMA_API_URL, json=ollama_payload)
        response.raise_for_status() # Lève une exception si la requête échoue

        llm_response = response.json()
        final_answer = llm_response.get('message', {}).get('content', "Désolé, je n'ai pas pu générer de réponse.")
        
        logger.info(f"Réponse générée: {final_answer}")
        return {"response": final_answer}

    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur de communication avec Ollama: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur Ollama: {e}")
    except Exception as e:
        logger.error(f"Erreur interne dans ask_jackbot: {e}")
        raise HTTPException(status_code=500, detail=str(e))