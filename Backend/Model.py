import cohere
import os
from dotenv import load_dotenv
from rich import print

# Load environment variables
load_dotenv()
COHERE_API_KEY = os.getenv("CO_API_KEY")

# Check API key
if not COHERE_API_KEY:
    raise ValueError("CO_API_KEY not found in .env file.")

# Initialize Cohere client
co = cohere.Client(api_key=COHERE_API_KEY)

# Pre-defined prompt for classification
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
Do not answer any query, just decide the type of query based on its intent.
Respond only using these formats:
- general (query)
- realtime (query)
- automation (query)
"""

# Supported function types (if you need this list elsewhere)
funcs = [
    "exit", "general", "search", "generate", "summarize", "translate", "classify",
    "analyze_sentiment", "extract_entities", "generate_text", "generate_image",
    "generate_code", "generate_poem", "generate_story", "generate_joke",
    "generate_recipe", "generate_song", "generate_essay", "generate_email",
    "generate_letter", "generate_report", "generate_summary", "generate_tweet",
    "generate_blog_post", "youtube search", "reminder", "language", "weather",
    "news", "stock", "calculator", "unit_converter", "currency_converter", "time",
    "date", "joke", "quote", "fact", "advice", "trivia", "riddle", "math_problem",
    "word_definition", "synonym_antonym", "spelling_check", "grammar_check"
]

# Main decision function
def FirstLayerDMM(query: str) -> list:
    try:
        full_prompt = f"{preamble}\n\nQuery: {query.strip()}"
        response = co.chat(
            model="command-r-plus",
            message=full_prompt,
            temperature=0.2  # Low temp for accuracy
        )

        # Extract and clean response
        result = response.text.strip().lower()
        result_lines = result.split('\n')
        decisions = [line.strip() for line in result_lines if line.strip()]

        print("[bold cyan]Decision(s) returned:[/bold cyan]", decisions)
        return decisions

    except Exception as e:
        print(f"[red]Error in FirstLayerDMM:[/red] {e}")
        return []

# Optional testing block
if __name__ == "__main__":
    test_query = "What is the weather in Karachi?"
    decisions = FirstLayerDMM(test_query)
    print("[bold yellow]Final Output:[/bold yellow]", decisions)
