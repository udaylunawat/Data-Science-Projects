
# Agentic Data Analysis Framework

## Overview
A conversational AI agent for automated data analysis with natural language queries. Key capabilities:
- 📊 Smart visualization selection (histograms, scatter plots, bar/line charts)
- 🔍 Automated data profiling and statistical analysis
- 🧩 Modular tool architecture (data loading, analysis, visualization, querying)
- 🤖 Gemini-2.0-flack model integration (via Google ADK)

## Architecture

```mermaid
%%{init: {'theme': 'neutral', 'themeVariables': { 'primaryColor': '#E3F2FD'}}}%%
flowchart TD
    A[User] -->|Natural Language Query & Data Files| B(Agent Core)
    B --> C{Query Type}
    C -->|Load Data| D[📂 Data Loader & CSV/Excel Support]
    C -->|Analyze| E[📈 Statistical Analysis & Summary Stats, Grouping]
    C -->|Visualize| F[📊 Visualization Engine & Auto Chart Selection]
    C -->|Query| G[🔍 Data Query & Filter/Sort/Limit]
    D --> H[Structured Data & Metadata Profile]
    E --> I[Statistical Insights:- Mean, Median, Trends]
    F --> J[Interactive Plots:- PNG/HTML Output]
    G --> K[Filtered Dataset:- Sorted Results]
    H & I & J & K --> L[📄 Final Report\nFormatted Results]
    L --> A

    style A fill:#B3E5FC,stroke:#039BE5
    style B fill:#C8E6C9,stroke:#43A047
    style C fill:#FFF3E0,stroke:#FB8C00
    style D fill:#F0F4C3,stroke:#C0CA33
    style E fill:#FFCCBC,stroke:#EF6C00
    style F fill:#E1BEE7,stroke:#8E24AA
    style G fill:#B2DFDB,stroke:#00897B
    style L fill:#BBDEFB,stroke:#1976D2
```



## Features
### Core Components
- `load_data_tool`: Intelligent data ingestion (CSV/Excel) with automatic type detection
- `analyze_data_tool`: NLP-driven statistical analysis (summary stats, group-by ops)
- `visualize_data_tool`: Context-aware visualization engine (Plotly-based)
- `query_data_tool`: Natural language data filtering/sorting

### Advanced Capabilities
- Automatic chart type selection based on data types
- Dynamic column matching from natural language queries
- Image generation with timestamped report archiving
- Base64 encoded visualizations for web integration

## Installation
```bash
# Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env  # Add your Google API key
```

## Usage Example
```python
adk web --reload
```
