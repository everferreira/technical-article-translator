/// <summary>
/// Technical Article Translator — C# CLI
///
/// Traduz artigos técnicos usando a MyMemory API (gratuita, sem chave).
/// Preserva blocos de código, termos técnicos, URLs e formatação markdown.
///
/// Uso:
///   dotnet run -- "text to translate" --target=pt --mode=technical
///
/// Compilar:
///   dotnet build
///   dotnet run -- --help
/// </summary>
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace TechnicalArticleTranslator
{
    /// <summary>
    /// Modelo para resposta da API MyMemory.
    /// </summary>
    class MyMemoryResponse
    {
        public ResponseData responseData { get; set; }
        public string responseStatus { get; set; }
    }

    class ResponseData
    {
        public string translatedText { get; set; }
        public double match { get; set; }
    }

    /// <summary>
    /// Tradutor de artigos técnicos em C#.
    /// </summary>
    public class ArticleTranslator
    {
        // ── Termos técnicos que NÃO devem ser traduzidos ──────
        private static readonly HashSet<string> TECHNICAL_TERMS = new HashSet<string>(Arrays.asList(
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
        ));

        // ── Regex patterns ─────────────────────────────────────
        private static readonly Regex CODE_BLOCK_RE = new Regex("```[\\w]*\\n.*?```", RegexOptions.DotAll);
        private static readonly Regex INLINE_CODE_RE = new Regex("`[^`]+`");
        private static readonly Regex URL_RE = new Regex("https?://\\S+");

        /// <summary>
        /// Traduz um artigo técnico preservando código, termos e formatação.
        /// </summary>
        public static string Translate(string text, string source, string target, string mode)
        {
            if (text == null || text.Trim().isEmpty())
                return "";

            if (mode.Equals("general", StringComparison.IgnoreCase))
            {
                return CallTranslationApi(text, source, target);
            }

            // Modo técnico: preservar estrutura
            var codeBlocks = new List<string>();
            text = PreserveBlocks(text, CODE_BLOCK_RE, "CODEBLOCK", codeBlocks);

            var inlineCodes = new List<string>();
            text = PreserveBlocks(text, INLINE_CODE_RE, "INLINECODE", inlineCodes);

            var urls = new List<string>();
            text = PreserveBlocks(text, URL_RE, "URL", urls);

            var termPlaceholders = ProtectTechnicalTerms(text);
            text = termPlaceholders.GetKey();

            // Traduzir
            string translated = CallTranslationApi(text, source, target);

            // Restaurar
            translated = RestoreTermPlaceholders(translated, termPlaceholders.GetValue());
            translated = RestoreBlocks(translated, "URL", urls);
            translated = RestoreBlocks(translated, "INLINECODE", inlineCodes);
            translated = RestoreBlocks(translated, "CODEBLOCK", codeBlocks);

            return translated;
        }

        /// <summary>
        /// Chama a MyMemory API para tradução.
        /// </summary>
        private static string CallTranslationApi(string text, string source, string target)
        {
            try
            {
                string encodedText = UriEncode(text);
                // MyMemory API — gratuita, sem chave para uso moderado
                string url = string.Format(
                    "https://api.mymemory.transmitted.net/get?q={0}&langpair={1}|{2}",
                    encodedText,
                    source.Equals("auto") ? "en" : source,
                    target
                );

                var client = new HttpClient();
                var request = new HttpRequest(HttpMethod.Get, url);
                request.Headers.Add("User-Agent", "TechnicalArticleTranslator/1.0");

                var response = client.Send(request);
                string body = response.Body.ReadString();

                var json = JsonSerializer.Deserialize<MyMemoryResponse>(body);
                if (json != null && json.responseData != null)
                {
                    return json.responseData.translatedText;
                }
                return text; // fallback: retorna original
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("Erro na tradução: " + ex.Message);
                return text; // fallback seguro
            }
        }

        /// <summary>
        /// Substitui matches de uma regex por placeholders.
        /// </summary>
        private static string PreserveBlocks(string text, Regex regex, string prefix, List<string> storage)
        {
            var matcher = regex.Matcher(text);
            var buffer = new StringBuilder();
            int lastEnd = 0;

            while (matcher.Find())
            {
                buffer.Append(text.Substring(lastEnd, matcher.Start() - lastEnd));
                storage.Add(matcher.Group(0));
                buffer.Append($"\u0000{prefix}{storage.Size() - 1}\u0000");
                lastEnd = matcher.End();
            }
            buffer.Append(text.Substring(lastEnd));
            return buffer.ToString();
        }

        /// <summary>
        /// Restaura placeholders para blocos originais.
        /// </summary>
        private static string RestoreBlocks(string text, string prefix, List<string> originals)
        {
            for (int i = 0; i < originals.Size(); i++)
            {
                text = text.Replace($"\u0000{prefix}{i}\u0000", originals[i]);
            }
            return text;
        }

        /// <summary>
        /// Protege termos técnicos com placeholders.
        /// </summary>
        private static KeyValuePair<string, List<KeyValuePair<string, string>>> ProtectTechnicalTerms(string text)
        {
            var placeholders = new List<KeyValuePair<string, string>>();
            int idx = 0;

            // Ordenar do maior para o menor
            var sortedTerms = TECHNICAL_TERMS.ToArray();
            Arrays.Sort(sortedTerms, (a, b) => b.Length() - a.Length());

            foreach (var term in sortedTerms)
            {
                string pattern = "\\b" + Regex.Escape(term) + "\\b";
                string placeholder = $"\u0000TECH{idx}\u0000";

                var re = new Regex(pattern);
                if (re.IsMatch(text))
                {
                    text = re.Replace(text, placeholder);
                    placeholders.Add(new KeyValuePair<string, string>(placeholder, term));
                    idx++;
                }
            }

            return new KeyValuePair<string, List<KeyValuePair<string, string>>>(text, placeholders);
        }

        /// <summary>
        /// Restaura termos técnicos dos placeholders.
        /// </summary>
        private static string RestoreTermPlaceholders(string text, List<KeyValuePair<string, string>> placeholders)
        {
            foreach (var pair in placeholders)
            {
                text = text.Replace(pair.GetKey(), pair.GetValue());
            }
            return text;
        }

        /// <summary>
        /// Encode URI para o texto.
        /// </summary>
        private static string UriEncode(string text)
        {
            return UriEncode(text); // C#/.NET Uri.EscapeDataString no real
        }
    }
}