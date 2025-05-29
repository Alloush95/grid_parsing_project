
# 📊 Grid Parser Project 🧩  
**Spatial Numerical Relationships for UI Layout Analysis**

This project automates the parsing and evaluation of graphical user interfaces (GUIs) from web pages using a **grid-based approach**. By leveraging **computer vision (OpenCV)**, **optical character recognition (OCR with Tesseract)**, and **deep learning object detection (YOLOv8)**, it extracts structured spatial relationships between UI components.

Designed for research in **UI usability, accessibility analysis, and automated interface parsing**, the project follows a **modular, step-by-step pipeline** aligned with academic methodologies.

---

## 📁 Project Structure

```
grid_parser_project/
│
├── main.py                           # Run the entire end-to-end pipeline
├── config.py                         # Paths, URLs, and runtime settings
│
├── step1_data_collection.py          # Step 1: Screenshot capture & UI element annotation
├── step2_grid_parsing.py             # Step 2: Grid-based layout mapping (spatial grammar)
├── step3_computer_vision.py          # Step 3: CV preprocessing, OCR, YOLO annotation generation
├── step4_metrics_evaluation.py       # Step 4: Compute parsing metrics (hit rate, density, entropy)
├── step5_prototype_development.py    # Step 5: Prototype testing on new e-commerce sites
├── step6_ai_integration.py           # Step 6: Simulated UI interactions (clicks, inputs)
├── step7_generalization.py           # Step 7: Generalization test on media/blog sites
├── step8_final_analysis.py           # Step 8: Final statistical analysis & visualization
│
└── utils/
    ├── driver_setup.py               # Selenium browser automation setup (undetected_chromedriver)
    └── helpers.py                    # Cookie dismissal logic, UI categorization, misc utilities
```

---

## 🚀 How to Run

### 1. 🔧 Setup Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

---

### 2. 📦 Install Required Packages

```bash
pip install -r requirements.txt
```

---

## 🆘 Troubleshooting & Support

- If encountering **network issues during installation**:
```bash
pip install -r requirements.txt --timeout=100
```
Or install critical packages manually:
```bash
pip install selenium undetected-chromedriver pandas numpy opencv-python pytesseract ultralytics seaborn scikit-learn matplotlib
```

- For faster downloads, use:
```bash
pip install -r requirements.txt -i https://pypi.org/simple --timeout=100
```

---

### 3. 🧠 Install Tesseract OCR (for text extraction)

- 📥 Download: [Tesseract OCR GitHub Releases](https://github.com/tesseract-ocr/tesseract)
- Update your Tesseract path in `config.py`:
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

---

### 4. ▶️ Run the Full Parsing Pipeline

```bash
python main.py
```

- You can also run **individual steps manually** (e.g., `step5_prototype_development.py`).

---

## 🧰 Dependencies

```
selenium
undetected-chromedriver
webdriver-manager
pandas
numpy
opencv-python
pytesseract
ultralytics (YOLOv8)
seaborn
scikit-learn
matplotlib
```

---

## 🏁 Expected Outputs

- 📸 **Screenshots** with grid overlays & OCR annotations.
- 📄 **JSON & CSV files**: UI component metadata (positions, roles, grid mappings).
- 📊 **Layout Metrics**: Hit Rate, Density, Entropy, Compression Ratios.
- 📈 **Visual Reports**: Correlation heatmaps, parsing score comparisons, grid consistency plots.
- 📝 **Interaction Logs**: Simulated user actions on buttons and input fields.

All outputs are organized under `ui_data/`, `screenshots/`, `plots/`, and `logs/` directories.

---

## 📚 Academic Context

This project was developed for the **Bachelor of Science in Computer Science Thesis**  
**Title**: *A Grid-Based Approach to Parsing 2D Screens for Web Interfaces*  
Focus: **Enhancing UI Component Detection via Spatial Numerical Relationships**
---

---

## 🎓 Educational Contributions

This project was developed as part of a Bachelor’s thesis in Computer Science at Kristianstad University. It supports key academic learning outcomes by:

- **Applying Scientific Methods:** Combines computer vision, OCR, and deep learning to model GUI layouts using grid-based spatial analysis.
- **Demonstrating Critical Thinking:** Builds on a literature review of 45 studies to address the lack of spatial reasoning in existing UI parsers.
- **Solving Problems Independently:** Designs and implements a modular pipeline—from data collection to evaluation—without relying on external frameworks.
- **Communicating Effectively:** Explains parsing logic, evaluation metrics, and interaction testing through written documentation and visual reporting.
- **Contributing to Society:** Enables use cases in accessibility auditing and AI-driven UX evaluation through structured layout analysis.
- **Fostering Lifelong Learning:** Outlines future directions such as semantic role inference, adaptive grids, and runtime profiling to inspire ongoing development.

---

## 👥 Authors

This project was developed by **Sam El Saati** and **Mohamad Alloush**  
as part of a Bachelor’s thesis in Computer Science at **Kristianstad University**, May 2025.
