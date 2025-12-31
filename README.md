# Cognitive Personal Assistant (CPA)

## Overview
The Cognitive Personal Assistant (CPA) is a long-term memory and interaction intelligence system designed to help users recall information, receive intelligent reminders, and get communication guidance based on past experiences and interactions — with the human always in control.

The system builds structured memory from chats, experiences, and interactions, and uses that memory to provide decision support and guidance.

---

## Core Principles (Non-Negotiable)

- **Human-in-the-loop always**
- **Memory > raw text**
- **Meaning > wording**
- **Probabilistic, not absolute**
- **Privacy-first** (encrypted, user-owned)
- **Modular & replaceable components**
- **Language-agnostic core**
- **Scalable** from prototype to production

---

## Architecture (High-Level)

The system is organized into six major modules:

- **Module A**: Input & Capture Layer
- **Module B**: Language & Understanding Layer
- **Module C**: Interaction Intelligence Layer
- **Module D**: Memory Layer
- **Module E**: Guidance & Assistance Layer
- **Module F**: Infrastructure, Ethics & Evaluation

Each module is developed, evaluated, and frozen independently to avoid scope drift.

---

## Development Rules (Anti-Drift)

We strictly follow this loop:

> Define → Identify failure cases → Design safeguards → Lock scope → Implement → Evaluate → Freeze → Move forward

❌ **No jumping ahead**
❌ **No feature creep**

---

## Setup (Local Development)

### 1. Activate the conda environment
```bash
conda activate cognitive_assistant
```

### 2. Install dependencies
```bash
pip install .
```

### 3. Run the application
```bash
uvicorn app.main:app --reload
```

### 4. Health check
Open in browser: http://127.0.0.1:8000/health

**Expected response:**
```bash
{
  "status": "ok"
}
```