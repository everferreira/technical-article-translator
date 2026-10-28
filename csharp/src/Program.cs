using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text.RegularExpressions;
using System.Text.Json;
using System.Text.URI;
using System.Threading.Tasks;

/// <summary>
/// Tradutor de Artigos Técnicos — CLI em C#
///
/// Traduz artigos técnicos usando a MyMemory API (gratuita, sem chave).
/// Preserva blocos de código, termos técnicos, URLs e formatação markdown.
///
/// Uso:
///   dotnet run -- "text to translate" --target=pt
///   dotnet run -- --file artigo.txt --from en --to pt
///   dotnet run -- --languages
/// </summary>
public class Program
{
    public static void Main(string[] args)
    {
        var cli = new CliParser(args);
        
        if (cli.HasFlag("--languages") || cli.HasFlag("-l"))
        {
            PrintLanguages();
            return;
        }

        if (cli.HasFlag("--help") || cli.HasFlag("-h"))
        {
            PrintHelp();
            return;
        }

        string text;
        if (cli.HasFlag("--file") || cli.HasFlag("-i"))
        {
            string filePath = cli.GetValue("--file") ?? cli.GetValue("-i");
            text = File.ReadAllText(filePath);
        }
        else
        {
            text = cli.GetPositional(0);
        }

        if (text == null || text.Trim().IsEmpty())
        {
            Console.Error.WriteLine("Erro: informe um texto ou use --file");
            PrintHelp();
            return;
        }

        string source = cli.GetValue("--from") ?? cli.GetValue("-f") ?? "auto";
        string target = cli.GetValue("--to") ?? cli.GetValue("-t") ?? "pt";
        string mode   = cli.GetValue("--mode") ?? cli.GetValue("-m") ?? "technical";

        try
        {
            string result = ArticleTranslator.Translate(text, source, target, mode);
            Console.WriteLine(result);
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine("Erro: " + ex.Message);
        }
    }

    private static void PrintLanguages()
    {
        Console.WriteLine("Idiomas suportados (MyMemory API):");
        Console.WriteLine("  en  English");
        Console.WriteLine("  pt  Português");
        Console.WriteLine("  es  Español");
        Console.WriteLine("  fr  Français");
        Console.WriteLine("  de  Deutsch");
        Console.WriteLine("  it  Italiano");
        Console.WriteLine("  ja  日本語");
        Console.WriteLine("  zh  中文");
        Console.WriteLine("  ru  Русский");
        Console.WriteLine("  ko  한국어");
        Console.WriteLine("  ar  العربية");
        Console.WriteLine("  hi  हिन्दी");
    }

    private static void PrintHelp()
    {
        Console.WriteLine("Uso: dotnet run -- [texto] [opcoes]");
        Console.WriteLine();
        Console.WriteLine("Argumentos:");
        Console.WriteLine("  texto              Texto a traduzir (ou use --file)");
        Console.WriteLine();
        Console.WriteLine("Opcoes:");
        Console.WriteLine("  --from, -f  CODE   Idioma fonte (padrao: auto)");
        Console.WriteLine("  --to, -t    CODE   Idioma alvo  (padrao: pt)");
        Console.WriteLine("  --mode, -m  MODE   Modo: technical|general (padrao: technical)");
        Console.WriteLine("  --file, -i  PATH   Ler texto de arquivo");
        Console.WriteLine("  --languages, -l    Listar idiomas disponiveis");
        Console.WriteLine("  --help, -h         Mostrar esta ajuda");
        Console.WriteLine();
        Console.WriteLine("Exemplos:");
        Console.WriteLine("  dotnet run -- \"Python is a programming language\"");
        Console.WriteLine("  dotnet run -- --file artigo.txt --from en --to pt");
    }
}

/// <summary>
/// Parser simples de CLI (sem dependencias externas).
/// </summary>
class CliParser
{
    private readonly string[] args;
    private readonly Dictionary<string, string> flags = new Dictionary<string, string>();
    private readonly List<string> positional = new List<string>();

    public CliParser(string[] args)
    {
        this.args = args;
        for (int i = 0; i < args.Length; i++)
        {
            string arg = args[i];
            if (arg.StartsWith("--"))
            {
                string key = arg;
                string value = null;
                if (i + 1 < args.Length && !args[i + 1].StartsWith("-"))
                {
                    value = args[++i];
                }
                flags[key] = value;
            }
            else if (arg.StartsWith("-") && arg.Length > 1 && arg[1] != '-')
            {
                // Flag curta: pode ter valor no proximo argumento
                string key = arg;
                string value = null;
                if (i + 1 < args.Length && !args[i + 1].StartsWith("-"))
                {
                    value = args[++i];
                }
                flags[key] = value;
            }
            else
            {
                positional.Add(arg);
            }
        }
    }

    public bool HasFlag(string name) => flags.ContainsKey(name);
    public string GetValue(string name) => flags[name];
    public string GetPositional(int index) => index < positional.Length ? positional[index] : null;
}

/// <summary>
/// Tradutor de artigos técnicos com preservação de código e termos.
/// </summary>
class ArticleTranslator
{
    // ── Termos técnicos que NÃO devem ser traduzidos ──
    private static readonly HashSet<string> TechnicalTerms = new HashSet<string>
    {
        "Python", "Java", "JavaScript", "TypeScript", "C#", "C++", "Rust", "Go",
        "Ruby", "PHP", "Swift", "Kotlin", "Scala", "Perl", "Lua", "Elixir",
        "Node.js", "Deno", ".NET", "React", "Angular", "Vue", "Flask", "FastAPI",
        "Django", "Spring Boot", "Next.js", "Tailwind", "Bootstrap",
        "Azure", "AWS", "GCP", "Docker", "Kubernetes", "Terraform", "Ansible",
        "CI/CD", "GitHub Actions", "GitLab CI", "Jenkins",
        "API", "REST", "GraphQL", "JSON", "YAML", "SQL", "NoSQL", "LLM",
        "GPT", "Transformers", "TensorFlow", "PyTorch", "scikit-learn",
        "Pandas", "NumPy", "OpenAI", "LangChain",
        "Git", "Linux", "HTTP", "HTTPS", "SSH", "CLI", "SDK", "IDE",
        "CRUD", "JWT", "OAuth", "WebSocket", "gRPC",
        "AWS Lambda", "Azure Functions", "Serverless", "Microservices"
    };

    private static readonly Regex CodeBlockRe = new Regex("```[\\w]*\\n.*?```", RegexOption.DotAll);
    private static readonly Regex InlineCodeRe = new Regex("`[^`]+`");
    private static readonly Regex UrlRe = new Regex("https?://\\S+");

    /// <summary>
    /// Traduz um artigo técnico preservando código, termos e formatação.
    /// </summary>
    public static string Translate(string text, string source, string target, string mode)
    {
        if (text == null || text.Trim().IsEmpty()) return "";

        if (mode.ToLower() == "general")
        {
            return CallTranslationApi(text, source, target);
        }

        // Modo técnico: preservar estrutura
        var codeBlocks = new List<string>();
        text = PreserveMatches(text, CodeBlockRe, "CODEBLOCK", codeBlocks);

        var inlineCodes = new List<string>();
        text = PreserveMatches(text, InlineCodeRe, "INLINECODE", inlineCodes);

        var urls = new List<string>();
        text = PreserveMatches(text, UrlRe, "URL", urls);

        // Proteger termos técnicos
        var termMap = new Dictionary<int, string>();
        text = ProtectTechnicalTerms(text, termMap);

        // Traduzir
        string translated = CallTranslationApi(text, source, target);

        // Restaurar tudo na ordem inversa
        translated = RestoreTermMap(translated, termMap);
        translated = RestorePlaceholders(translated, "URL", urls);
        translated = RestorePlaceholders(translated, "INLINECODE", inlineCodes);
        translated = RestorePlaceholders(translated, "CODEBLOCK", codeBlocks);

        return translated;
    }

    private static string PreserveMatches(string text, Regex regex, string prefix, List<string> storage)
    {
        var matcher = regex.FindAll(text);
        int offset = 0;
        var result = new StringBuilder(text);

        foreach (var match in matcher)
        {
            int idx = storage.Length;
            storage.Add(match.Text);
            string placeholder = $"\0{prefix}{idx}\0";
            
            int pos = match.Start + offset;
            result = result.Replace(pos, match.Length, placeholder);
            offset += placeholder.Length - match.Length;
        }

        return result.ToString();
    }

    private static string RestorePlaceholders(string text, string prefix, List<string> originals)
    {
        for (int i = 0; i < originals.Length; i++)
        {
            text = text.Replace($"\0{prefix}{i}\0", originals[i]);
        }
        return text;
    }

    private static string ProtectTechnicalTerms(string text, Dictionary<int, string> map)
    {
        int idx = 0;
        var sorted = TechnicalTerms.ToArray();
        Arrays.Sort(sorted, (a, b) => b.Length - a.Length);

        foreach (var term in sorted)
        {
            string escaped = Regex.Escape(term);
            string pattern = $"\\b{escaped}\\b";
            var re = new Regex(pattern);
            
            var matcher = re.Find(text);
            if (matcher != null)
            {
                string placeholder = $"\0TECH{idx}\0";
                map[idx] = term;
                text = text.Replace(matcher.Text, placeholder);
                idx++;
            }
        }

        return text;
    }

    private static string RestoreTermMap(string text, Dictionary<int, string> map)
    {
        foreach (var entry in map)
        {
            text = text.Replace($"\0TECH{entry.Key}\0", entry.Value);
        }
        return text;
    }

    private static string CallTranslationApi(string text, string source, string target)
    {
        try
        {
            string encoded = UriEncoder.Encode(text);
            string langPair = source == "auto" ? "en" : source;
            string url = $"https://api.mymemory.transmitted.net/get?q={encoded}&langpair={langPair}|{target}";

            var client = HttpClient.NewHttpClient();
            var request = HttpRequest.NewBuilder()
                .Uri(URI.Create(url))
                .Header("User-Agent", "TechnicalArticleTranslator/1.0")
                .GET()
                .Build();

            var response = client.Send(request);
            string body = response.Body.ReadString();

            var json = Json.Deserialize<MyMemoryResponse>(body);
            return json?.ResponseData?.TranslatedText ?? text;
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine("API error: " + ex.Message);
            return text;
        }
    }
}

class MyMemoryResponse
{
    public ResponseData ResponseData { get; set; }
}

class ResponseData
{
    public string TranslatedText { get; set; }
    public double Match { get; set; }
}