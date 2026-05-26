"""Flask app factory. Validates settings at boot; wires routes; injects
chain + store into `app.extensions` so routes can pull them out.

Per spec §8.2: provider misconfig should fail at app startup. We instantiate
the embeddings client and chat model here so a missing API key raises
immediately (Flask refuses to boot).
"""
from __future__ import annotations

import logging

from flask import Flask

from rocs_copilot_backend.chains.rag_chain import build_chain
from rocs_copilot_backend.config import Settings
from rocs_copilot_backend.ingest.store import ChromaStore
from rocs_copilot_backend.providers.llm import get_chat_model, get_embeddings
from rocs_copilot_backend.routes import chat, health

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")


def create_app(settings: Settings | None = None) -> Flask:
    settings = settings or Settings()  # raises ValidationError on bad config

    app = Flask(__name__)
    app.config["SETTINGS"] = settings

    # Eager provider construction — fail fast on missing API keys per §8.2.
    embeddings = get_embeddings()
    chat_model = get_chat_model()

    store = ChromaStore(persist_dir=settings.chroma_dir, embeddings=embeddings)
    rag_chain = build_chain(
        llm=chat_model,
        store=store,
        min_score=settings.retrieval_min_score,
        top_k=settings.retrieval_top_k,
    )

    app.extensions["chroma_store"] = store
    app.extensions["rag_chain"] = rag_chain

    app.register_blueprint(health.bp)
    app.register_blueprint(chat.bp)

    # Dev-only CORS for the Vite dev server (5173). Same-origin in prod.
    @app.after_request
    def _cors(resp):
        resp.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return resp

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False, threaded=True)
