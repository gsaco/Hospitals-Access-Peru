# Hospitals Access Peru - Geospatial Analysis 🏥

A comprehensive geospatial analysis of hospital accessibility in Peru using data from MINSA (hospitals) and INEI (population centers).

## 📋 Project Overview

This project provides a complete analysis of hospital accessibility in Peru through:
- **Static maps** showing hospital distribution by district
- **Department-level analysis** with summary statistics
- **Proximity analysis** for Lima and Loreto regions
- **Interactive visualizations** using Folium
- **Streamlit web application** with three analytical tabs

## 📊 Data Sources

- **Hospitals (MINSA – IPRESS)**: National registry of operational hospitals
- **Population Centers (INEI)**: Population centers dataset from CCPP_IGN100K.shp
- **Administrative Boundaries**: Districts shapefile (DISTRITOS.shp)

## 🔍 Methodology

### Hospital Filtering ("Functioning Status")
The analysis includes only **operational public hospitals** based on the following criteria:

1. **Status Filter**: Only hospitals with `Condición == "EN FUNCIONAMIENTO"` (operational status)
2. **Institution Filter**: Public institutions only:
   - MINSA (Ministry of Health)
   - GOBIERNO REGIONAL (Regional Government)
   - ESSALUD (Social Health Insurance)
   - FFAA (Armed Forces)
   - PNP (National Police)
3. **Coordinate Validation**: Hospitals must have valid latitude/longitude coordinates
4. **CRS Standardization**: All data standardized to EPSG:4326

## 📁 Files Structure

```
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── assets/                    # Generated maps and visualizations
├── data/                      # All datasets
│   ├── IPRESS.csv            # Hospitals dataset
│   ├── DISTRITOS.shp         # Districts shapefile
│   ├── CCPP_IGN100K.shp      # Population centers shapefile
│   └── ...                   # Additional shapefile components
├── src/                       # Source code
│   ├── streamlit_app.py      # Main Streamlit web application
│   └── utils.py              # Utility functions for data processing
├── code.ipynb                 # Main Jupyter notebook with complete analysis
├── run_app.py                # Streamlit application launcher
├── requirements.txt          # Python dependencies
├── LICENSE                   # MIT License
└── README.md                 # This file
```

## 🚀 Getting Started

### Prerequisites
```bash
pip install -r requirements.txt
```

### Running the Analysis

1. **Jupyter Notebook**: Open and run `code.ipynb` for the complete analysis
2. **Streamlit App**: Run the web application from the project root
   ```bash
   # Option 1: Using the launcher script (Recommended)
   python run_app.py
   
   # Option 2: Direct streamlit command from src directory
   cd src
   streamlit run streamlit_app.py
   ```
   
   The application will start at `http://localhost:8501` by default.

## 📋 Analysis Components

### 1. **Static Maps (GeoPandas)**
- Hospital count by district
- Districts with zero hospitals
- Top 10 districts with most hospitals
- Department-level choropleth maps

### 2. **Department-level Analysis**
- Summary statistics by department
- Bar charts and tables
- Identification of highest/lowest hospital coverage

### 3. **Proximity Analysis (Lima & Loreto)**
- 10km buffer analysis around population centers
- Identification of most isolated vs. most accessible areas
- Urban (Lima) vs. Amazon (Loreto) accessibility comparison

### 4. **Interactive Maps (Folium)**
- National choropleth with hospital markers
- Clustered hospital locations
- Proximity visualizations for Lima and Loreto

## 🎯 Streamlit Application Tabs

### 🗂️ Tab 1: Data Description
- Operational public hospitals overview
- Data sources and methodology
- Summary statistics and filtering rules

### 🗺️ Tab 2: Static Maps & Department Analysis  
- Hospital distribution maps
- Department-level analysis
- Summary tables and charts

### 🌍 Tab 3: Dynamic Maps
- Interactive national map
- Lima and Loreto proximity analysis
- 10km buffer visualizations

## 📈 Key Findings

- **Urban Concentration**: Higher hospital density in urban areas
- **Rural Accessibility**: Limited hospital access in remote areas
- **Geographic Challenges**: Amazon regions face particular difficulties
- **Inequality**: Significant disparities in healthcare infrastructure distribution

## 🛠️ Technical Notes

- **Project Structure**: Professional organization with separate directories for source code, data, and generated assets
- **Asset Management**: Maps and visualizations are automatically saved to the `assets/` directory
- **Coordinate System**: EPSG:4326 (WGS84) for consistency
- **Buffer Analysis**: 10km radius using approximate degree conversion
- **Spatial Operations**: GeoPandas for spatial joins and analysis
- **Visualization**: Matplotlib/Seaborn for static maps, Folium for interactive maps

## 📝 Data Quality

- All hospitals filtered for operational status ("EN FUNCIONAMIENTO")
- Only public institutions included in analysis
- Coordinate validation ensures spatial accuracy
- Missing data handled appropriately in all analyses
