#!/usr/bin/env python3
"""
Technical Article Translator — API REST (FastAPI)

Endpoints:
  POST /translate   → Traduzir texto
  GET  /languages   → Listar idiomas suportados
  GET  /health      → Health check

Uso:
  uvicorn api:app --host 0.0.0.0 --port 8000
  uvicorn api:app --reload  (dev)
"""

import logging
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from technical_translator import translate_technical_article, supported_languages

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Technical Article Translator API",
    description="Traduz artigos técnicos preservando código, termos e formatação.",
    version="1.0.0",
)

# CORS — permite acesso do GitHub Pages e desenvolvimento local
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://everferreira.github.io",
        "http://localhost:5500",
        "http://localhost:8000",
        "null",  # para file:// no desenvolvimento
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Models ──────────────────────────────────────────────────────────

class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Texto a traduzir")
    source: str = Field("auto", description="Idioma fonte (ex: 'en', 'auto')")
    target: str = Field("pt", description="Idioma alvo (ex: 'pt', 'en')")
    mode: str = Field("technical", description="Modo: 'technical' ou 'general'")

class TranslateResponse(BaseModel):
    translated_text: str
    source: str
    target: str
    mode: str
    character_count: int

class LanguageItem(BaseModel):
    code: str
    name: str

class LanguagesResponse(BaseModel):
    languages: list[LanguageItem]
    count: int

# ── Endpoints ───────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "technical-article-translator"}


@app.post("/translate", response_model=TranslateResponse)
def translate(req: TranslateRequest):
    """
    Traduz um artigo técnico.

    Preserva blocos de código (```…```), código inline (`…`),
    URLs, e termos técnicos (API, Docker, Python, etc.).
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Texto vazio")

    try:
        result = translate_technical_article(
            text=req.text,
            source=req.source,
            target=req.target,
            mode=req.mode,
        )
        return TranslateResponse(
            translated_text=result,
            source=req.source,
            target=req.target,
            mode=req.mode,
            character_count=len(req.text),
        )
    except Exception as e:
        logger.exception("Erro na tradução")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/languages", response_model=LanguagesResponse)
def list_languages():
    """Lista os idiomas suportados pelo Google Translate."""
    try:
        langs = supported_languages()
        items = [LanguageItem(code=k, name=v) for k, v in langs.items()]
        return LanguagesResponse(languages=sorted(items, key=lambda x: x.name), count=len(items))
    except Exception as e:
        logger.exception("Erro ao listar idiomas")
        raise HTTPException(status_code=500, detail=str(e))