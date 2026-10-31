<div align="center">

# 🔍 GitHub Profile Screening Tool

**Analyze GitHub profiles against configurable criteria and make data-driven eligibility decisions.**

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![GitHub API](https://img.shields.io/badge/GitHub%20API-v3%20%2B%20GraphQL-181717?logo=github&logoColor=white)](https://docs.github.com/en/rest)
---

*Built by **Chouaib**, **Rayan**, **Mehdi**, and **Mohamed**

</div>

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the App](#running-the-app)
- [Usage Guide](#-usage-guide)
  - [Input Methods](#input-methods)
  - [Configurable Criteria](#configurable-criteria)
  - [Understanding Results](#understanding-results)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
  - [Data Fetching Layer](#1-data-fetching-layer-srcfetcherpy)
  - [Evaluation Engine](#2-evaluation-engine-srcevaluatorpy)
  - [Pipeline Orchestrator](#3-pipeline-orchestrator-srcpipelinepy)
- [GitHub API & Authentication](#-github-api--authentication)
- [Configuration Reference](#-configuration-reference)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [Team](#-team)

---

## 🌟 Overview

The **GitHub Profile Screening Tool** is a web application that analyzes GitHub developer profiles against user-defined criteria to determine eligibility for programs, hiring, hackathons, or any scenario where you need to evaluate developer activity at scale.

Instead of manually reviewing each GitHub profile, this tool:

1. **Fetches** comprehensive profile data from the GitHub REST & GraphQL APIs
2. **Evaluates** each profile against your chosen thresholds (repos, followers, commits, languages, etc.)
3. **Scores** candidates on a 0–20 scale with clear accept / review / reject decisions
4. **Presents** results in an interactive dashboard with per-profile drill-down

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **🎯 Configurable Criteria** | Set minimum thresholds for repos, followers, account age, commits, topics, and external contributions |
| **🌐 Language Filtering** | Require specific programming languages (Python, Rust, Go, JavaScript, etc.) |
| **📊 Scoring System** | 0–20 score based on how well a profile meets each criterion, with levels from "Bad" to "Perfect" |
| **📁 Bulk Input** | Analyze multiple profiles at once via text input, CSV, or Excel files |
| **🔗 Flexible Input** | Accepts raw usernames, full GitHub URLs, or mixed input |
| **🧹 Deduplication** | Automatically deduplicates entries (case-insensitive) |
| **⚡ Smart Decisions** | Three-tier output: **ACCEPTED**, **NEED REVIEW** (close to thresholds), or **REJECTED** |
| **🔑 Token Support** | Works without a token (basic mode) or with a `GITHUB_TOKEN` for commit/contribution data |
| **📈 Detailed Review** | Per-criterion breakdown showing profile values, required minimums, and percentage reached |

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Streamlit UI (app.py)                  │
│         Sidebar criteria  ·  Input area  ·  Results      │
└──────────────────────┬───────────────────────────────────┘
                       │
              ┌────────▼────────┐
              │   Pipeline      │    Orchestration: input parsing,
              │  (pipeline.py)  │    URL extraction, dedup, error
              └──┬──────────┬───┘    handling per user
                 │          │
        ┌────────▼──┐  ┌────▼───────┐
        │  Fetcher   │  │ Evaluator  │
        │(fetcher.py)│  │(evaluator. │
        │            │  │    py)     │
        │ REST API   │  │ Scoring &  │
        │ GraphQL    │  │ Decisions  │
        └────────────┘  └────────────┘
              │
     ┌────────▼────────┐
     │   GitHub API     │
     │  REST + GraphQL  │
     └─────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.12** or higher
- **pip** (Python package manager)
- A **GitHub Personal Access Token** *(optional but recommended as it's required for commit and contribution data)*

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/hebboulchouaib/github-tool-chouaib.git
   cd github-tool-chouaib
   ```

2. **Create a virtual environment** *(recommended)*

   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Linux / macOS
   # .venv\Scripts\activate          # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set your GitHub token** *(optional)*

   ```bash
   export GITHUB_TOKEN="ghp_your_token_here"
   ```

   > **Without a token:** the tool still works but is limited to 60 API requests/hour and cannot fetch commit counts or external contribution data. Those fields will show as "unknown" in the evaluation.

### Running the App

```bash
streamlit run app.py
```

The application opens in your browser at `http://localhost:8501`.

---

## 📖 Usage Guide

### Input Methods

The tool supports **three ways** to provide GitHub profiles:

| Method | How |
|--------|-----|
| **Text Input** | Type or paste usernames and/or GitHub URLs, separated by spaces, commas, semicolons, or newlines |
| **CSV File** | Upload a `.csv` file — the tool auto-detects columns named `username`, `link`, `url`, or `github` |
| **Excel File** | Upload a `.xlsx` file — same column auto-detection as CSV |

**Examples of accepted input:**
```
octocat
https://github.com/torvalds
github.com/gvanrossum
```

### Configurable Criteria

All criteria are set via sidebar sliders. **Setting a criterion to 0 means it is ignored** (any value is accepted).

| Criterion | Description | Slider Max |
|-----------|-------------|------------|
| **Minimum public repos** | Total public repositories on the profile | 100 |
| **Minimum followers** | Number of followers | 500 |
| **Minimum account age** | How old the GitHub account is (in years) | 20 |
| **Minimum total commits** | Lifetime commit contributions *(requires token)* | 2,000 |
| **Minimum topics** | Number of unique topics across repositories | 20 |
| **Minimum external repos** | Repos contributed to that the user doesn't own *(requires token)* | 50 |
| **Required languages** | Programming languages that must appear in the profile | Multi-select |

### Understanding Results

After analysis, results appear in an interactive table:

| Column | Meaning |
|--------|---------|
| **Username** | The GitHub login |
| **Score** | 0–20 numeric score (average of how well each criterion is met) |
| **Level** | Human-readable level: Bad · Below Average · Average · Above Average · Good · Perfect |
| **Decision** | **ACCEPTED** · **NEED REVIEW** · **REJECTED** |

**Click any row** to see the detailed per-criterion breakdown:

- **Profile value** — what the user actually has
- **Minimum** — the threshold you set
- **Reached** — percentage of the threshold met (capped at 100%)
- **Result** — accepted / close / rejected / unknown

#### Decision Logic

| Condition | Decision |
|-----------|----------|
| All criteria met | ✅ **ACCEPTED** |
| Some criteria within 80% of threshold, or commit/contribution data unavailable | 🟡 **NEED REVIEW** |
| Any criterion below 80% of threshold, or missing required language | ❌ **REJECTED** |

> **Score formula:** average of all "reached" percentages (each capped at 100%), scaled to 20. Languages affect the decision but not the numeric score.

---

## 📂 Project Structure

```
github-tool-chouaib/
├── app.py                  # Streamlit web interface (entry point)
├── src/
│   ├── fetcher.py          # GitHub API data-fetching layer
│   ├── evaluator.py        # Scoring & decision engine
│   └── pipeline.py         # Orchestration: input → fetch → evaluate → results
├── tests/
│   └── github/
│       └── test_client.py  # Unit tests (mocked HTTP)
├── data/
│   └── sample_users.csv    # Example input file
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

### Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `app.py` | Streamlit UI: sidebar criteria, input area, results table, detailed review panel |
| `src/fetcher.py` | Talks to GitHub REST & GraphQL APIs, returns a `ProfileData` frozen dataclass |
| `src/evaluator.py` | Compares `ProfileData` against criteria, computes scores and decisions |
| `src/pipeline.py` | Parses raw input (URLs, usernames, files), deduplicates, orchestrates fetch + evaluate per user |

---

## ⚙ How It Works

### 1. Data Fetching Layer (`src/fetcher.py`)

Fetches and aggregates data from **two GitHub API surfaces**:

**REST API** (no token required):
- `GET /users/{username}` → name, creation date, followers, public repo count
- `GET /users/{username}/repos?type=owner` → paginated list of owned repos (forks excluded), aggregated by primary language and topics

**GraphQL API** (requires token):
- `contributionsCollection` → total commit contributions, queried one year at a time from account creation to today
- `repositoriesContributedTo` → count of external repos (not owned by the user) with commit or PR contributions

The resulting `ProfileData` dataclass:

```python
@dataclass(frozen=True)
class ProfileData:
    username: str
    name: str | None
    created_at: datetime
    followers: int
    public_repos: int
    repos_analyzed: int                      # non-fork owned repos
    languages: dict[str, int]                # language → repo count
    topics: dict[str, int]                   # topic → repo count
    total_commits: int | None                # None if no token
    external_repos_contributed_to: int | None # None if no token
```

**Error handling:** custom exceptions (`UserNotFoundError`, `RateLimitError`, `GitHubError`) ensure failures are cleanly reported per-profile without affecting other users in the batch.

### 2. Evaluation Engine (`src/evaluator.py`)

Takes a `ProfileData` and a set of requirements, then:

1. **Checks** each criterion: `accepted` (≥ threshold), `close` (≥ 80% of threshold), `rejected` (< 80%), or `unknown` (data unavailable)
2. **Scores** by averaging the "percentage reached" across all active criteria, scaled to 0–20
3. **Assigns a level**: Bad (0–4) → Below Average (5–9) → Average (10) → Above Average (11–14) → Good (15–19) → Perfect (20)
4. **Decides**: ACCEPTED / NEED REVIEW / REJECTED based on the score and language requirements

### 3. Pipeline Orchestrator (`src/pipeline.py`)

Handles the end-to-end flow:

1. **Parses input** — extracts usernames from raw text, GitHub URLs, CSV, or Excel
2. **Deduplicates** — case-insensitive, preserves first occurrence
3. **Processes each user** — fetch → evaluate, catching errors per-profile
4. **Returns structured results** — ready for the Streamlit UI to display

---

## 🔑 GitHub API & Authentication

| Mode | Rate Limit | Available Data |
|------|-----------|----------------|
| **No token** | 60 requests/hour | Profile info, repos, languages, topics |
| **With token** | 5,000 requests/hour | All of the above **+** lifetime commits, external contributions |

### Creating a GitHub Token

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **Generate new token (classic)**
3. Select scope: **`public_repo`** (read-only access to public repos is sufficient)
4. Copy the token and set it:

```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

---

## ⚙ Configuration Reference

All configuration is done at runtime through the **Streamlit sidebar**. There are no config files to edit.

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| Minimum public repos | Slider (0–100) | 0 | 0 = any value accepted |
| Minimum followers | Slider (0–500) | 0 | |
| Minimum account age (years) | Slider (0–20) | 0 | |
| Minimum total commits | Slider (0–2000) | 0 | Requires `GITHUB_TOKEN` |
| Minimum topics | Slider (0–20) | 0 | |
| Minimum external repos | Slider (0–50) | 0 | Requires `GITHUB_TOKEN` |
| Required languages | Multi-select | None | Case-insensitive matching |

> ⚠️ **At least one criterion must be set** (non-zero slider or at least one language selected) for the analysis to run.

---

## 🧪 Testing

The project includes unit tests using **pytest** with mocked HTTP calls (no real API requests):

```bash
# Install test dependencies
pip install pytest pytest-asyncio respx

# Run tests
PYTHONPATH=src pytest tests/ -v
```

**Test coverage includes:**
- Language and topic aggregation across multiple repos
- Fork exclusion
- Null-language handling
- Pagination across multiple pages
- 404 → `UserNotFoundError`
- Rate limit → `RateLimitError` with reset time
- No-token mode (GraphQL fields are `None`)
- Commit summation across yearly windows

---

## 👥 Team

| Member                | Role                                   |
| --------------------- | -------------------------------------- |
| **Chouaib**           | Data Fetching Layer & API Integration  |
| **Rayan**             | Evaluation Engine & Scoring Logic      |
| **Mehdi**             | Pipeline Orchestration & Input Parsing |
| **Mohamed (Kiotaka)** | Streamlit UI & User Experience         |

---