# 🌫 Karnataka AQI Analyzer Dashboard  
![Karnataka AQI Analyzer Banner](./assets/karnataka_aqi_banner.png)

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)]()  
[![Dash](https://img.shields.io/badge/Dash-v2.10-blue.svg)]()  
[![TensorFlow](https://img.shields.io/badge/TensorFlow-v2.13-orange.svg)]()  
[![LightGBM](https://img.shields.io/badge/LightGBM-v3.3-green.svg)]()  
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)]()  
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Deployed%20on%20Render-brightgreen)](https://aqi-weather-karnataka-dash-app.onrender.com/)  

---

## 🚀 Live Demo: [Check out the Karnataka AQI Analyzer here](https://aqi-weather-karnataka-dash-app.onrender.com/)

Welcome to the **Karnataka AQI Analyzer**, a state-of-the-art interactive dashboard built with Dash to monitor, forecast, and analyze air quality across Karnataka cities. The app brings together live weather, pollutant data, and AI-powered AQI predictions in an elegant, responsive interface.

---

# Karnataka AQI Analyzer  

An AI-powered **Dash** dashboard that provides:  
- Real-time AQI forecasting based on pollutant input using LSTM deep learning.  
- Live weather updates fetched from WeatherAPI.  
- Air quality snapshot and trends for key cities like Bangalore and Mysuru.  
- MLflow experiment statistics for model monitoring and transparency.  

---

## Project Overview

This dashboard uses modern Python tooling to combine:  
- **Dash & Dash Bootstrap Components** for a sleek UI.  
- **TensorFlow** based LSTM models for time-series AQI prediction.  
- **LightGBM** classifier for AQI categorization.  
- **MLflow** for experiment tracking and reporting.  
- Real-time integration of external APIs for weather and AQI data.  

---

## Features  

- **Interactive pollutant input** with dropdown and manual entry.  
- **Hourly AQI forecasting** with categorized air quality levels.  
- City-wise snapshots with live weather and AQI plots.  
- Historical AQI trend analysis with annotated key events.  
- Responsive design with caching for fast updates.  
- Easy deployment on Render with Gunicorn support.  

---

## Repo Structure  

Karnataka_AQI_Analyzer/
│
├── app.py # Main Dash app setup and layout
├── cache_config.py # Cache initialization and configuration
├── mlflow_utils.py # MLflow CSV data utils for experiment metrics
├── utils.py # Data loading, preprocessing, prediction helpers
├── pages/ # Multi-page Dash app components
│ ├── about.py # About page with MLflow experiment summaries
│ ├── city_snapshot.py # City live snapshot with weather & AQI visualizations
│ ├── predictor.py # AQI predictor page with pollutant inputs and forecasts
│ └── trends.py # AQI trends with historical views and annotations
├── models/ # Pretrained TensorFlow LSTM and LightGBM models
├── assets/ # Static CSS, JavaScript, images, and favicon files
├── data/ # AQI and weather datasets & plot images
├── requirements.txt # Python package dependencies
└── README.md # Project documentation and instructions


## Getting Started  

### Prerequisites  
- Python 3.10 or later  
- Git  

### Local Setup  

1. Clone the repository:  
git clone https://github.com/yourusername/karnataka-aqi-analyzer.git
cd karnataka-aqi-analyzer

text
2. Install dependencies:  
pip install -r requirements.txt

text
3. Run the app locally:  
python app.py

text
Open your browser at `http://127.0.0.1:8050` to view the dashboard.

---

## Deploy on Render (Free Tier)  

1. Push your repo to GitHub.  
2. Log in to [Render.com](https://render.com/), create a new **Web Service**, and connect your repo.  
3. Set these commands:  
   - **Build Command:**  
pip install -r requirements.txt

text
- **Start Command:**  
gunicorn app:server --bind 0.0.0.0:$PORT --workers 2 --threads 8 --timeout 120

text
4. Render will deploy and give you a HTTPS URL such as:  
[https://aqi-weather-karnataka-dash-app.onrender.com/](https://aqi-weather-karnataka-dash-app.onrender.com/)

---

## Screenshots  

*(Include screenshots or GIFs demonstrating:)*  
- The AQI Predictor page with pollutant inputs and forecast graph.  
- City Snapshot showing live weather and AQI plots.  
- Trends page with historical AQI charts and annotations.  
- About page displaying MLflow experiment metrics summaries.

---

## Future Enhancements  

- Integrate explainability methods (e.g., SHAP) for predictions.  
- Add multi-city batch prediction capabilities.  
- Dockerize for streamlined deployment and reproducibility.  
- Implement user authentication for personalized user experience.  
- Enhance UI/UX with additional interactive visualizations.

---

## License  

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Contact & Feedback  

Built with ❤️ by **Akash Anup Kumar**  
Contributions and feedback are welcome! Feel free to open issues, submit pull requests, or connect on LinkedIn.

---

*Thank you for exploring the Karnataka AQI Analyzer. Stay informed, breathe easy.*  
