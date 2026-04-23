# 🧠 FINDIT Core: ML-Service (AI Engine)

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)
![XGBoost](https://img.shields.io/badge/Model-XGBoost-orange?style=for-the-badge&logo=scikitlearn)
![FastAPI](https://img.shields.io/badge/Framework-FastAPI/Flask-009688?style=for-the-badge&logo=fastapi)
![Hugging Face](https://img.shields.io/badge/Deployed_on-Hugging_Face-yellow?style=for-the-badge&logo=huggingface)

This repository contains the Machine Learning service for **FINDIT Core**. It serves as the primary inference engine that calculates win probabilities and generates tactical strategic insights for Mobile Legends: Bang Bang (MLBB) drafts.

## 🤖 Model Intelligence

The core of this service is a **Gradient Boosting (XGBoost)** classifier trained on historical competitive draft data. It analyzes the synergy and counter-relationships between heroes across 10 pick slots and 10 ban slots.

### Key Capabilities:
* **Predictive Analytics:** Calculates real-time win probability margins for Blue and Red teams.
* **Dynamic Insight Engine:** Utilizes a randomized heuristic pool to generate unique tactical analyses in **English**.
* **Recommendation System:** Provides actionable strategic advice (e.g., "Prioritise Turtle control", "Capitalise on power spikes") based on the predicted match momentum.

## 📡 API Reference

### Predict Outcome
Returns the probability and tactical analysis for a specific draft composition.

* **Endpoint:** `POST /predict`
* **Content-Type:** `application/json`

**Request Body:**
```json
{
  "teamA": ["phoveus", "fanny", "zhuxin", "moskov", "khaleed"],
  "teamB": ["sora", "leomord", "valentina", "claude", "gloo"],
  "teamABans": ["khufra", "harley", "fredrinn", "guinevere", "zetian"],
  "teamBBans": ["marcel", "granger", "karrie", "chip", "uranus"]
}
