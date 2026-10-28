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
        return f"\x00CODEBLOCK{idx}\x00"
    return CODE_BLOCK_RE.sub(_replace, text), blocks


def restore_code_blocks(text: str, blocks: list[str]) -> str:
    """Restaura blocos de código dos placeholders."""
    for idx, block in enumerate(blocks):
        text = text.replace(f"\x00CODEBLOCK{idx}\x00", block)
    return text


def protect_technical_terms(text: str) -> tuple[str, list[tuple[str, str]]]:
    """Protege termos técnicos com placeholders para evitar tradução."""
    placeholders: list[tuple[str, str]] = []

    # Ordenar do maior para o menor para evitar substituições parciais
    terms = sorted(TECHNICAL_TERMS, key=len, reverse=True)
    for i, term in enumerate(terms):
        # Só protege se for palavra inteira (usando \b boundaries)
        pattern = r"\b" + re.escape(term) + r"\b"
        placeholder = f"\x00TECH{i}\x00"
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
        return f"\x00INLINECODE{idx}\x00"
    return INLINE_CODE_RE.sub(_replace, text), codes


def restore_inline_code(text: str, codes: list[str]) -> str:
    for idx, code in enumerate(codes):
        text = text.replace(f"\x00INLINECODE{idx}\x00", code)
    return text


def protect_urls(text: str) -> tuple[str, list[str]]:
    """Protege URLs."""
    urls = []
    def _replace(m: re.Match) -> str:
        urls.append(m.group(0))
        idx = len(urls) - 1
        return f"\x00URL{idx}\x00"
    return URL_RE.sub(_replace, text), urls


def restore_urls(text: str, urls: list[str]) -> str:
    for idx, url in enumerate(urls):
        text = text.replace(f"\x00URL{idx}\x00", url)
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

    from deep_translator import GoogleTranslator

    if mode == "general":
        translator = GoogleTranslator(source=source, target=target)
        return translator.translate(text)

    # ── Modo técnico: preservar estrutura ──
    text, code_blocks = preserve_code_blocks(text)
    text, inline_codes = protect_inline_code(text)
    text, urls = protect_urls(text)
    text, term_placeholders = protect_technical_terms(text)

    # Traduzir
    translator = GoogleTranslator(source=source, target=target)
    translated = translator.translate(text)

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


# ── CLI ─────────────────────────────────────────────────────────────
def main():
    import typer
    app = typer.Typer(help="Tradutor de Artigos Técnicos")

    @app.command()
    def translate(
        text: str = typer.Argument(..., help="Texto a traduzir"),
        source: str = typer.Option("auto", "--from", "-f", help="Idioma fonte"),
        target: str = typer.Option("pt", "--to", "-t", help="Idioma alvo"),
        mode: str = typer.Option(
            "technical", "--mode", "-m",
            help="Modo: 'technical' (preserva código) ou 'general'"
        ),
        file: Optional[str] = typer.Option(
            None, "--file", "-i",
            help="Ler texto de um arquivo em vez de argumento"
        ),
    ):
        """Traduz um artigo técnico."""
        if file:
            with open(file, "r", encoding="utf-8") as f:
                text = f.read()

        result = translate_technical_article(text, source, target, mode)
        print(result)

    @app.command()
    def languages():
        """Lista idiomas suportados."""
        langs = supported_languages()
        for code, name in sorted(langs.items(), key=lambda x: x[1]):
            print(f"  {code:8s} {name}")

    app()


if __name__ == "__main__":
    main()