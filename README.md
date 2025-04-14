# Natural Language Query Detection and Correction Tool for Spatial Databases

This repository contains the source code for the master's thesis **"SpaCor: A Tool for High-Quality Spatial NLQ Corpus Construction"**. The project focuses on **building** a natural language query corpus for spatial databases and developing an automated tool for **detecting** and **correcting** incorrect queries.

## 🌟 Features

- Construction of a domain-specific query corpus
- Automatic classification of spatial queries (e.g., range, nearest neighbor, spatial join, etc.)
- Detection of mismatches between query expressions and database entities
- Automatic correction of natural language queries

## 🛠 Technologies Used

- Python 3.x
- pandas
- Regular Expressions
- Custom rule-based detection and correction logic

## 📁 Project Structure

```bash
├── SpaCor
│   ├── knowledge_base/    # Datasets for training
│   ├── save_models/       # LSTM training model
│   ├── PredictText.py     # Module for type predict
│   ├── QueryDetection.py  # Module for query detection
│   ├── QueryDectionOne.py # Module for one query detection
│   ├── QueryGeneration.py # Module for query generation    
├── static/                # Web page style
├── templates
│   ├── index.html         # Web page
├── app.py                 # Executable file 
└── README.md              # Project documentation

