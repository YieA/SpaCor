# SpaCor: Natural Language Query Detection and Correction for Spatial Databases

**SpaCor** is a tool designed for detecting, correcting and generating natural language queries over spatial databases. It integrates query detection, repair and generation into a unified framework, and supports both command-line and web-based interaction.

🔗 **Project Repository**: [https://github.com/YieA/SpaCor](https://github.com/YieA/SpaCor)

---

## 🚀 Features

- **Query Type Prediction** using a trained LSTM model
- **Error Detection** for spatial natural language queries
- **Automatic Correction** of invalid or inconsistent query expressions
- **Query Generation** based on pre-defined templates
- **Web Interface** for ease of use

---

## 🧠 Technologies

- Python 3.8
- Flask (for web interface)
- LSTM model (for query type prediction)
- pandas, re, sklearn, torch, etc.

---

## 📁 Project Structure

```bash
├── SpaCor/
│   ├── knowledge_base/        # Datasets for training
│   ├── save_models/           # Trained LSTM model
│   ├── PredictText.py         # Query type prediction module
│   ├── QueryDetection.py      # Multi-query detection module
│   ├── QueryDectionOne.py     # Single query detection module
│   ├── QueryGeneration.py     # Query generation module
├── static/                    # Web UI styles (CSS)
├── templates/
│   ├── index.html             # Web UI template
├── app.py                     # Main application entry (Flask server)
└── README.md                  # Project documentation
```

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/YieA/SpaCor.git
cd SpaCor
```

> ⚠️ Note: Make sure you have Python 3.8+ and PyTorch installed.

---

## 💻 Usage

### ▶️ Run Web Application

```bash
python app.py
```

Then open your browser and visit:  
[http://127.0.0.1:5000](http://127.0.0.1:5000)

### 📊 Predict Query Type

```bash
python SpaCor/PredictText.py
```

### 🧪 Run Query Detection and Repair Manually

```bash
python SpaCor/QueryDetection.py
```

### 🧪 Run Query Generation Manually

```bash
python SpaCor/QueryGeneration.py
```

---

## 📄 Sample Input & Output

**Input CSV (from `knowledge_base/`):**
```spatial_relations.csv
id,name,GeoData,place_name_attr
1,Faehren,line,Ort
2,Flaechen,region,Name
3,Kinos,point,Name
4,Kneipen,point,Name
```

```places.csv
rel_id,name
1,Caputh (Havel)
1,Ketzin (Havel)
1,Strodehne (Havel)
1,Räbel (Elbe)
```

**Output:**
```csv
cat,query,relations,entities
Aggregation-count Query,Could you provide the total number of UBahnhof in Großer Kuhwall?,['UBahnhof'],['Großer Kuhwall']
Aggregation-count Query,Could you please enumerate the number of WFlaechen in Neue Wache?,['WFlaechen'],['Neue Wache']
Aggregation-count Query,I am looking for the overall number of strassen in Havel.,['strassen'],['Havel']
Aggregation-count Query,Kindly provide me with the count of Landstrassen in Rehwiese.,['Landstrassen'],['Rehwiese']
```

---

## 📚 Citation

If you use this tool in your research, please cite:

> -

---

## 📬 Contact

For questions or feedback, please reach out to: **wjyi_x@nuaa.edu.com**

---

## 📝 License

This project is licensed under the NUAA License.
