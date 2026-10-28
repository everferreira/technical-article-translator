#!/usr/bin/env python3
"""
Technical Article Translator — módulo principal de tradução.

Usa deep-translator para traduzir artigos técnicos preservando:
  - Blocos de código (``` ... ```)
  - Termos técnicos (whitelist)
  - URLs, e-mails, caminhos de arquivo
  - Formatação markdown estrutural

Modos:
  - general   → tradução direta (padrão)
  - technical → modo técnico com preservação de código e termos
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ── Whitelist de termos técnicos que NÃO devem ser traduzidos ──────────
TECHNICAL_TERMS = {
    # Linguagens / runtimes
    "Python", "Java", "JavaScript", "TypeScript", "C#", "C++", "Rust", "Go",
    "Ruby", "PHP", "Swift", "Kotlin", "Scala", "Perl", "Lua", "Elixir",
    "Node.js", "Deno", ".NET", "React", "Angular", "Vue", "Flask", "FastAPI",
    "Django", "Spring Boot", "Next.js", "Tailwind", "Bootstrap",
    # Cloud & infra
    "Azure", "AWS", "GCP", "Docker", "Kubernetes", "Terraform", "Ansible",
    "CI/CD", "GitHub Actions", "GitLab CI", "Jenkins",
    # IA & dados
    "API", "REST", "GraphQL", "JSON", "YAML", "SQL", "NoSQL", "LLM",
    "GPT", "Transformers", "TensorFlow", "PyTorch", "scikit-learn",
    "Pandas", "NumPy", "OpenAI", "LangChain",
    # Ferramentas
    "Git", "Linux", "HTTP", "HTTPS", "SSH", "CLI", "SDK", "IDE",
    "CRUD", "JWT", "OAuth", "WebSocket", "gRPC",
    # Nuvem
    "AWS Lambda", "Azure Functions", "Serverless", "Microservices",
}

# ── Preservação de blocos de código ──────────────────────────────────
CODE_BLOCK_RE = re.compile(r"```[\w]*\n.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`]+`")
URL_RE = re.compile(r"https?://\S+")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.\w+")


def preserve_code_blocks(text: str) -> tuple[str, list[str]]:
    """Substitui blocos de código por placeholders e retorna os originais."""
    blocks = []
    def _replace(m: re.Match) -> str:
        blocks.append(m.group(0))
        idx = len(blocks) - 1
        return f"__CB_{idx}__"
    return CODE_BLOCK_RE.sub(_replace, text), blocks


def restore_code_blocks(text: str, blocks: list[str]) -> str:
    """Restaura blocos de código dos placeholders."""
    for idx, block in enumerate(blocks):
        text = text.replace(f"__CB_{idx}__", block)
    return text


def protect_technical_terms(text: str) -> tuple[str, list[tuple[str, str]]]:
    """Protege termos técnicos com placeholders para evitar tradução."""
    placeholders: list[tuple[str, str]] = []

    # Ordenar do maior para o menor para evitar substituições parciais
    terms = sorted(TECHNICAL_TERMS, key=len, reverse=True)
    for i, term in enumerate(terms):
        pattern = r"\b" + re.escape(term) + r"\b"
        placeholder = f"__TECH_{i}__"
        text = re.sub(pattern, placeholder, text)
        placeholders.append((placeholder, term))

    return text, placeholders


def restore_technical_terms(text: str, placeholders: list[tuple[str, str]]) -> str:
    """Restaura termos técnicos dos placeholders."""
    for placeholder, term in placeholders:
        text = text.replace(placeholder, term)
    return text


def protect_inline_code(text: str) -> tuple[str, list[str]]:
    """Protege código inline (`code`)."""
    codes = []
    def _replace(m: re.Match) -> str:
        codes.append(m.group(0))
        idx = len(codes) - 1
        return f"__IC_{idx}__"
    return INLINE_CODE_RE.sub(_replace, text), codes


def restore_inline_code(text: str, codes: list[str]) -> str:
    for idx, code in enumerate(codes):
        text = text.replace(f"__IC_{idx}__", code)
    return text


def protect_urls(text: str) -> tuple[str, list[str]]:
    """Protege URLs."""
    urls = []
    def _replace(m: re.Match) -> str:
        urls.append(m.group(0))
        idx = len(urls) - 1
        return f"__URL_{idx}__"
    return URL_RE.sub(_replace, text), urls


def restore_urls(text: str, urls: list[str]) -> str:
    for idx, url in enumerate(urls):
        text = text.replace(f"__URL_{idx}__", url)
    return text


def translate_technical_article(
    text: str,
    source: str = "auto",
    target: str = "pt",
    mode: str = "technical",
) -> str:
    """
    Traduz um artigo técnico preservando formatação e termos.

    Args:
        text: Texto a ser traduzido.
        source: Código do idioma fonte ("auto" para detecção automática).
        target: Código do idioma alvo (ex: "pt", "en", "es", "fr").
        mode: "general" → tradução simples | "technical" → modo técnico.

    Returns:
        Texto traduzido.
    """
    if not text.strip():
        return ""

    if mode == "general":
        return _do_translate(text, source, target)

    # ── Modo técnico: preservar estrutura ──
    text, code_blocks = preserve_code_blocks(text)
    text, inline_codes = protect_inline_code(text)
    text, urls = protect_urls(text)
    text, term_placeholders = protect_technical_terms(text)

    # Traduzir com fallback
    translated = _do_translate(text, source, target)

    # Restaurar
    translated = restore_technical_terms(translated, term_placeholders)
    translated = restore_urls(translated, urls)
    translated = restore_inline_code(translated, inline_codes)
    translated = restore_code_blocks(translated, code_blocks)

    return translated


def supported_languages() -> dict[str, str]:
    """Retorna dicionário de idiomas suportados (código → nome)."""
    from deep_translator import GoogleTranslator
    # deep-translator retorna dict do Google Translate
    try:
        return GoogleTranslator().get_supported_languages(as_dict=True)
    except Exception:
        return {
            "en": "English", "pt": "Português", "es": "Español",
            "fr": "Français", "de": "Deutsch", "it": "Italiano",
            "ja": "日本語", "zh": "中文", "ru": "Русский",
            "ko": "한국어", "ar": "العربية", "hi": "हिन्दी",
        }


# ── Engine: fallback MyMemory quando Google Translate falha ────────
_MYMEMORY_CACHE: dict[str, str] = {}


def _translate_via_mymemory(text: str, source: str, target: str) -> str:
    """Fallback usando MyMemory API (gratuita, sem chave)."""
    import urllib.request
    import urllib.parse
    import json

    params = urllib.parse.urlencode({
        "q": text,
        "langpair": f"{'en' if source == 'auto' else source}|{target}",
    })
    url = f"https://api.mymemory.translated.net/get?{params}"

    req = urllib.request.Request(url, headers={"User-Agent": "TechnicalArticleTranslator/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())

    if data.get("responseStatus") != 200:
        raise RuntimeError(f"MyMemory error {data.get('responseStatus')}")

    return data["responseData"]["translatedText"]


def _do_translate(text: str, source: str, target: str) -> str:
    """Tenta Google Translate (deep-translator), fallback MyMemory."""
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source=source, target=target)
        return translator.translate(text)
    except Exception:
        logger.warning("Google Translate falhou, usando fallback MyMemory API")
        return _translate_via_mymemory(text, source, target)


# ── CLI ─────────────────────────────────────────────────────────────
def main():
    import argparse

    parser = argparse.ArgumentParser(
        prog="translate-article",
        description="Tradutor de Artigos Técnicos — preserva código, termos e formatação.",
    )
    parser.add_argument("text", nargs="?", default=None, help="Texto a traduzir")
    parser.add_argument("--from", "-f", dest="source", default="auto",
                        help="Idioma fonte (ex: en, pt, auto)")
    parser.add_argument("--to", "-t", dest="target", default="pt",
                        help="Idioma alvo (ex: pt, en, es)")
    parser.add_argument("--mode", "-m", default="technical",
                        choices=["technical", "general"],
                        help="Modo: technical (preserva código) ou general")
    parser.add_argument("--file", "-i", default=None,
                        help="Ler texto de um arquivo")
    parser.add_argument("--languages", "-l", action="store_true",
                        help="Listar idiomas suportados")

    args = parser.parse_args()

    if args.languages:
        langs = supported_languages()
        for code, name in sorted(langs.items(), key=lambda x: x[1]):
            print(f"  {code:8s} {name}")
        return

    text = args.text
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()

    if not text:
        parser.print_help()
        return

    result = translate_technical_article(text, args.source, args.target, args.mode)
    print(result)


if __name__ == "__main__":
    main()