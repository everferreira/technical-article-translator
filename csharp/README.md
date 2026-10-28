# C# Technical Article Translator

CLI em C# para tradução de artigos técnicos usando MyMemory API.

## Pré-requisitos

- **.NET SDK 21+** (ou 11+ para versões LTS)

```bash
# Verificar instalação
dotnet --version

# Se não tiver: https://dotnet.microsoft.com/download
```

## Compilar e Executar

```bash
cd csharp/src

# Executar direto
dotnet run -- "Python is a programming language" --to pt

# Com arquivo de entrada
dotnet run -- --file artigo.md --from en --to pt --mode technical

# Tradução geral (sem preservar termos técnicos)
dotnet run -- "Hello world" --to pt --mode general

# Listar opções
dotnet run -- --help
```

## Exemplo

```bash
dotnet run -- "Docker containers are lightweight virtual machines that share the host kernel" --to pt
# Saída: "Os contêineres Docker são máquinas virtuais leves que compartilham o kernel do host"
# Nota: "Docker" e "kernel" permanecem intactos
```

## Estrutura

```
csharp/
└── src/
    └── Program.cs    # CLI + lógica de tradução (monoarquivo)
```