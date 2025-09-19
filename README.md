# 🏥 Hospitals Access Peru - Professional Geospatial Analysis

<div align="center">

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

*A comprehensive, professional-grade geospatial analysis platform for healthcare infrastructure accessibility in Peru*

[🚀 **Live Demo**](#getting-started) | [📖 **Documentation**](#documentation) | [🤝 **Contributing**](#contributing) | [📊 **Screenshots**](#screenshots)

</div>

---

## 🌟 Overview

This repository provides a **world-class, professional geospatial analysis platform** for examining hospital accessibility across Peru. Built with modern data science tools and following industry best practices, it delivers actionable insights into healthcare infrastructure distribution and accessibility patterns.

### ✨ Key Features

- 🎯 **Interactive Dashboard**: Professional Streamlit web application with 4 comprehensive analysis tabs
- 🗺️ **Advanced Geospatial Visualization**: Static maps, interactive choropleth maps, and proximity analysis
- 📊 **Professional Analytics**: Statistical analysis, accessibility indices, and disparity metrics
- 🏗️ **Enterprise-Grade Architecture**: Modular design, comprehensive testing, and CI/CD integration
- 🎨 **Modern UI/UX**: Professional styling with animations, custom themes, and responsive design
- 📈 **Interactive Charts**: Plotly-powered visualizations with exportable reports
- 🔧 **Developer-Friendly**: Full testing suite, Docker support, and comprehensive documentation

## 📊 Screenshots

### Dashboard Overview
![Dashboard Overview](assets/dashboard_overview.png)

### Interactive Maps
![Interactive Maps](assets/interactive_maps.png)

### Analytics Dashboard
![Analytics](assets/analytics_dashboard.png)

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** (recommended: 3.11)
- **Git** for version control
- **Optional**: Docker for containerized deployment

### 🔧 Quick Installation

```bash
# Clone the repository
git clone https://github.com/gsaco/Hospitals-Access-Peru.git
cd Hospitals-Access-Peru

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
python run_app.py
```

The application will launch at `http://localhost:8501`

### 🐳 Docker Deployment

```bash
# Build and run with Docker
docker-compose up --build

# Or with individual containers
docker build -t hospitals-access-peru .
docker run -p 8501:8501 hospitals-access-peru
```

### 🛠️ Development Setup

```bash
# Install development dependencies
make install-dev

# Run tests
make test

# Format code
make format

# Run all checks
make check-all
```

## 📁 Professional Repository Structure

```
📦 Hospitals-Access-Peru/
├── 📁 .github/                    # GitHub workflows and templates
│   └── workflows/
│       └── ci.yml                 # CI/CD pipeline
├── 📁 analysis/                   # Jupyter notebooks
│   ├── geospatial_analysis.ipynb  # Main analysis notebook
│   └── interactive_mapping.ipynb  # Interactive mapping notebook
├── 📁 assets/                     # Generated visualizations and screenshots
├── 📁 data/                       # Datasets (MINSA, INEI, shapefiles)
│   ├── IPRESS.csv                 # Hospitals dataset
│   ├── DISTRITOS.shp              # Districts boundaries
│   └── CCPP_IGN100K.shp           # Population centers
├── 📁 docs/                       # Documentation
├── 📁 scripts/                    # Utility scripts
├── 📁 src/                        # Source code
│   ├── streamlit_app.py           # Main dashboard application
│   ├── utils.py                   # Utility functions
│   └── __init__.py                # Package initialization
├── 📁 tests/                      # Test suite
│   ├── test_analysis.py           # Analysis function tests
│   ├── test_streamlit_app.py      # Streamlit app tests
│   └── __init__.py                # Test package initialization
├── 🐳 docker-compose.yml          # Docker orchestration
├── 🐳 Dockerfile                  # Docker container configuration
├── ⚙️ Makefile                    # Development commands
├── 📋 pyproject.toml               # Project configuration
├── 📋 requirements.txt             # Python dependencies
├── 🚀 run_app.py                   # Application launcher
├── 📄 LICENSE                     # MIT License
└── 📖 README.md                   # This file
```

## 🎯 Analysis Components

### 1. 📊 Dashboard Overview
- **Real-time Metrics**: Live healthcare infrastructure statistics
- **Data Quality Indicators**: Completeness, validity, and operational status metrics
- **Interactive Charts**: Plotly-powered visualizations with drill-down capabilities
- **Professional Styling**: Modern UI with animations and responsive design

### 2. 🗺️ Static Geographic Analysis
- **Hospital Distribution Maps**: Choropleth visualization by districts
- **Department-Level Analysis**: Statistical summaries and rankings
- **Disparity Metrics**: Inequality analysis and accessibility ratios
- **Summary Statistics**: Comprehensive data overviews

### 3. 🌍 Interactive Geographic Visualization
- **National Choropleth Maps**: Interactive district-level hospital distribution
- **Regional Proximity Analysis**: Lima (urban) vs Loreto (Amazon) comparison
- **Buffer Analysis**: 10km accessibility zones around population centers
- **Custom Map Styling**: Multiple tile layers and professional legends

### 4. 📈 Advanced Healthcare Analytics
- **Accessibility Index**: Composite scoring system for healthcare access
- **Statistical Analysis**: Correlation studies and distribution patterns
- **Performance Benchmarking**: Regional comparison and ranking systems
- **Export Capabilities**: Data download in multiple formats

## 📊 Data Sources

| Source | Description | Records | Format |
|--------|-------------|---------|---------|
| **MINSA - IPRESS** | National registry of operational health establishments | ~7,000+ | CSV |
| **INEI - Population Centers** | Official population centers database | ~130,000+ | Shapefile |
| **Administrative Boundaries** | Official district boundaries of Peru | ~1,800+ | Shapefile |

## 🔍 Methodology

### Data Quality Assurance
- ✅ **Operational Status**: Only hospitals with status "EN FUNCIONAMIENTO"
- 🏛️ **Public Institutions**: MINSA, GOBIERNO REGIONAL, ESSALUD, FFAA, PNP
- 📍 **Coordinate Validation**: Valid latitude/longitude required
- 🌐 **Standardized CRS**: EPSG:4326 (WGS84) for global consistency
- 🔬 **Automated Validation**: Comprehensive data integrity checks

### Spatial Analysis
- **Buffer Analysis**: 10km radius accessibility zones
- **Spatial Joins**: Hospital-district association mapping
- **Proximity Calculations**: Distance-based accessibility metrics
- **Choropleth Mapping**: Statistical density visualization

## 🛡️ Quality Assurance

### Testing Framework
- **Unit Tests**: Comprehensive function testing with pytest
- **Integration Tests**: End-to-end workflow validation
- **Data Validation**: Automated data quality checks
- **Performance Testing**: Load and stress testing capabilities

### Code Quality
- **Type Hints**: Full type annotation coverage
- **Code Formatting**: Black and isort for consistent styling
- **Linting**: Flake8 for code quality enforcement
- **Documentation**: Comprehensive docstrings and comments

### CI/CD Pipeline
- **Automated Testing**: GitHub Actions workflow
- **Multi-Python Support**: Testing across Python 3.8-3.12
- **Security Scanning**: Dependency vulnerability checks
- **Documentation Building**: Automated docs generation

## 🚀 Advanced Features

### Professional Dashboard Enhancements
- 🎨 **Custom Themes**: Professional gradient styling and animations
- 📱 **Responsive Design**: Mobile-friendly interface
- ⚡ **Performance Optimization**: Caching and lazy loading
- 🔧 **Interactive Controls**: Advanced filtering and configuration options
- 📊 **Export Functionality**: Multi-format data export capabilities

### Analytics Capabilities
- 📈 **Statistical Analysis**: Correlation studies and trend analysis
- 🎯 **Accessibility Indices**: Composite scoring algorithms
- 📊 **Comparative Analysis**: Regional benchmarking and ranking
- 🔍 **Pattern Recognition**: Geographic clustering and dispersion analysis

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](docs/CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run the test suite (`make test`)
5. Format your code (`make format`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📖 Documentation

- 📚 [**User Guide**](docs/user_guide.md) - Complete usage instructions
- 🔧 [**Developer Guide**](docs/developer_guide.md) - Development setup and API reference
- 📊 [**Data Guide**](docs/data_guide.md) - Data sources and methodology
- 🚀 [**Deployment Guide**](docs/deployment_guide.md) - Production deployment instructions

## 🔗 Links & Resources

- 🌐 **Live Demo**: [Streamlit Cloud Deployment](https://share.streamlit.io)
- 📊 **Dataset Sources**: [MINSA](https://www.gob.pe/minsa) | [INEI](https://www.inei.gob.pe/)
- 🗺️ **Geospatial Tools**: [GeoPandas](https://geopandas.org/) | [Folium](https://folium.readthedocs.io/)
- 📈 **Visualization**: [Plotly](https://plotly.com/) | [Matplotlib](https://matplotlib.org/)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Gabriel Saco**
- GitHub: [@gsaco](https://github.com/gsaco)
- Email: [Contact via GitHub](https://github.com/gsaco)

## 🙏 Acknowledgments

- **MINSA** - For providing comprehensive healthcare establishment data
- **INEI** - For population and geographic boundary datasets
- **Open Source Community** - For the amazing tools and libraries that make this project possible

## 📈 Project Statistics

- 🏥 **7,000+** Hospitals analyzed
- 🗺️ **1,800+** Districts covered
- 📊 **25** Departments included
- 🎯 **4** Analysis modules
- ✅ **90%+** Test coverage

---

<div align="center">

**Built with ❤️ for better healthcare accessibility in Peru**

[⬆ Back to top](#-hospitals-access-peru---professional-geospatial-analysis)

</div>
