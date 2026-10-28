# 🌐 Tradutor de Artigos Técnicos

[![▶ Teste Online](https://img.shields.io/badge/▶_Teste_Online-58a6ff?style=for-the-badge&logo=github&logoColor=white&labelColor=58a6ff&color=white)](https://everferreira.github.io/technical-article-translator/)
[![Python](https://img.shields.io/badge/Python-3.12+-3572A5?logo=python)](https://python.org)
[![C#](https://img.shields.io/badge/C%23-.NET-8136b3?logo=dotnet)](https://dotnet.microsoft.com)
[![License](https://img.shields.io/badge/License-MIT-888?logo=github)](LICENSE)

> **DIO AI-102 Certification** — Desafio: Tradutor de Artigos Técnicos com AzureAI  
> Substituição por solução multi-plataforma: **Python CLI + C# CLI + Web App (GitHub Pages)**

---

## 📋 Sobre

Tradutor especializado em **artigos técnicos** que preserva:

- ✅ **Blocos de código** — `\`\`\`python ... \`\`\`` são mantidos intactos
- ✅ **Termos técnicos** — API, Docker, Python, Kubernetes, Azure, etc. não são traduzidos
- ✅ **URLs e emails** — links permanecem funcionais
- ✅ **Código inline** — \`variavel\` preservado
- ✅ **Formatação Markdown** — headers, listas, negrito, itálico

### Demonstração Online

👉 **[https://everferreira.github.io/technical-article-translator/](https://everferreira.github.io/technical-article-translator/)**

---

## 🏗️ Estrutura do Projeto

```
├── index.html                   # 🌐 Frontend web (GitHub Pages)
├── css/style.css                # 🎨 Estilo responsivo dark theme
├── js/translator.js             # ⚡ Lógica de tradução client-side
│
├── python/
│   ├── technical_translator.py  # 🐍 Módulo principal de tradução
│   ├── api.py                   # 🚀 API FastAPI (deploy opcional)
│   └── requirements.txt         # 📦 Dependências Python
│
├── csharp/
│   └── src/
│       └── Program.cs           # ☕ CLI em C# (dotnet run)
│
├── .github/workflows/
│   └── pages.yml                # 🔄 Deploy automático GitHub Pages
│
└── README.md                    # 📚 Esta documentação
```

---

## 🚀 Como Usar

### 🌐 Web (GitHub Pages)

Acesse diretamente: **[everferreira.github.io/technical-article-translator](https://everferreira.github.io/technical-article-translator/)**

1. Cole seu artigo técnico na área de texto
2. Selecione idioma fonte e alvo
3. Escolha o modo: **Técnico** (preserva código/termos) ou **Geral**
4. Clique em **Traduzir Artigo** (ou `Ctrl+Enter`)

### 🐍 Python CLI

```bash
cd python
pip install -r requirements.txt

# Traduzir texto direto
python technical_translator.py "Python is a powerful programming language" --to pt

# Traduzir arquivo
python technical_translator.py --file artigo.md --from en --to pt --mode technical

# Listar idiomas suportados
python technical_translator.py --languages
```

#### API FastAPI

```bash
cd python
pip install -r requirements.txt
uvicorn api:app --reload

# POST /translate
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello world","target":"pt","mode":"general"}'

# GET /languages
curl http://localhost:8000/languages
```

### ☕ C# CLI

```bash
cd csharp/src

# Compilar e executar (requer .NET SDK)
dotnet run -- "Python is a programming language" --to pt

# Com arquivo
dotnet run -- --file artigo.md --from en --to pt --mode technical

# Ajuda
dotnet run -- --help
```

> **Nota:** O .NET SDK não está pré-instalado no WSL. Instale com:
> ```bash
> sudo apt install dotnet-sdk-21  # ou baixe da microsoft.com
> ```

---

## ⚙️ Engines de Tradução

| Componente | Engine | Requer API Key |
|---|---|---|
| **Python CLI** | `deep-translator` → Google Translate | ❌ Grátis |
| **Python API** | `deep-translator` → Google Translate | ❌ Grátis |
| **C# CLI** | MyMemory API | ❌ Grátis (uso moderado) |
| **Web (JS)** | MyMemory API | ❌ Grátis (CORS-friendly) |

### 🔧 Modo Técnico — Como Funciona

1. **Preservação**: blocos de código (\`\`\`), código inline (\`\`), URLs e ~150 termos técnicos são substituídos por placeholders
2. **Tradução**: o texto limpo é enviado ao motor de tradução
3. **Restauração**: placeholders são revertidos para o conteúdo original

Isso garante que `pip install flask` não vire `pip instalar frasco` e `Docker` não seja traduzido.

---

## 🧪 Testes

```bash
cd python
python -c "
from technical_translator import translate_technical_article

# Teste modo técnico
text = 'Install **Docker** using \`apt\`:\n\`\`\`bash\nsudo apt install docker.io\n\`\`\`'
result = translate_technical_article(text, 'en', 'pt', 'technical')
print(result)
# Docker e bloco de código devem estar preservados
"
```

---

## 📊 Deploy

### GitHub Pages (automático)

O deploy é automático via GitHub Actions ao fazer push na `main`:

```bash
git add .
git commit -m "feat: tradutor de artigos técnicos"
git push origin main
```

### Python API (opcional — Render / Railway)

```bash
cd python
pip install -r requirements.txt
uvicorn api:app --host 0.0.0.0 --port 8080
```

---

## 📜 Licença

MIT © [Ever Ferreira](https://everferreira.github.io)

---

## 🏅 DIO AI-102 Certification

Este projeto foi desenvolvido como parte do desafio **"Tradutor de Artigos Técnicos com AzureAI"** da formação **AI-102 Certification** da Digital Innovation One (DIO).

| Requisito | Implementação |
|---|---|
| Azure AI + Python | ✅ Python CLI + API (FastAPI) com `deep-translator` |
| Azure AI + C# | ✅ C# CLI com MyMemory API |
| Preservar termos técnicos | ✅ Whitelist de ~150 termos + placeholders |
| Preservar blocos de código | ✅ Regex + placeholder restoration |
| Interface web | ✅ GitHub Pages com dark theme responsivo |
| CI/CD | ✅ GitHub Actions → Pages automático |