# Agent Browser

A command-line interface (CLI) tool for AI-driven browser automation. Built on top of [browser-use](https://github.com/browser-use/browser-use), this tool allows you to command an AI agent to perform complex browser interactions, scraping, and testing using natural language.

## Features

- **Natural Language Control:** Command the browser to navigate, click, fill forms, and extract information using simple text prompts.
- **Multiple LLM Support:** Easily toggle between powerful models like Google Gemini and Groq.
- **Smart Rate Limiting:** Built-in delay mechanism and fallback handling to gracefully circumvent free-tier API rate limits.
- **CLI Workflows:** Execute fast actions directly from your terminal.

## Installation

This project requires **Python 3.11+**. We recommend using `uv` or a standard virtual environment (`venv`) to install dependencies.

1. **Clone the repository and set up a virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -e .
   ```

3. **Environment Setup**
   Copy `.env.example` to `.env` and fill in your API credentials:
   ```bash
   cp .env.example .env
   ```
   *Note: Either `GOOGLE_API_KEY` or `GROQ_API_KEY` is required depending on your chosen LLM provider.*

## Usage

You can run the agent by giving it a specific task. To see available options, simply run:

```bash
agentbrowser run --help
```

### Examples

**Information Extraction (Fast & Simple):**
```bash
agentbrowser run "Cari jadwal libur nasional Indonesia 2026 di Google dan rangkum"
```

**Running with a Specific LLM Provider:**
```bash
agentbrowser run "Cari sejarah singkat berdirinya kota Jakarta melalui Wikipedia" --llm gemini
```

**Enabling Vision Mode (For complex sites):**
*Note: Vision requires standard screen rendering capability and may consume more tokens.*
```bash
agentbrowser run "Buka kalkulator BMI online, isi berat badan 70kg dan tinggi 175cm, bagikan hasilnya" --vision
```

## Logs & Outputs

- Execution traces and application logs are automatically written to the `logs/` directory.
- Any graphical outputs (like screenshots from Vision mode) or data exports are saved to the `outputs/` directory.

## Best Practices (Free-Tier APIs)

When using free accounts for LLMs (like the Gemini 15 RPM Free Tier):
- Limit your tasks to websites with simple structures (Wikipedia, News platforms, Google Search).
- Avoid massive single-page applications or heavy E-commerce sites like Tokopedia, as they can exhaust your token quota almost instantly due to their giant DOM sizes.

## License

MIT License
