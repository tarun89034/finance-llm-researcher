---
title: Financial LLM Copilot
emoji: "\U0001F4CA"
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: openrail
app_port: 7860
---

# Financial LLM Copilot

AI-powered macroeconomic analysis covering **80+ countries** across **7 regions** with **12 indicators**.

## Features

- Chat with a fine-tuned Mistral-7B model for financial analysis
- Regional economic analysis with interactive charts
- Global country rankings by any indicator
- Side-by-side country comparisons
- Data triangulated from FRED, World Bank, and OECD

## Tech Stack

- **Frontend**: Streamlit
- **LLM**: QLoRA fine-tuned Mistral-7B (GGUF format)
- **Inference**: llama-cpp-python
- **Data Sources**: FRED, World Bank, OECD APIs
- **Visualization**: Plotly
