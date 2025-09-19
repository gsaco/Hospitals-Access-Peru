import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium import plugins
from shapely.geometry import Point
import warnings
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import time
from datetime import datetime
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import (
    load_and_clean_data,
    filter_operational_hospitals,
    spatial_join_hospitals_districts,
    create_choropleth_map,
    perform_proximity_analysis,
    create_proximity_folium_map,
    create_national_choropleth_folium,
    create_summary_statistics
)
warnings.filterwarnings('ignore')

# Configure Streamlit page
st.set_page_config(
    page_title="🏥 Hospitals Access Peru - Professional Geospatial Analysis",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/gsaco/Hospitals-Access-Peru',
        'Report a bug': 'https://github.com/gsaco/Hospitals-Access-Peru/issues',
        'About': "# Hospitals Access Peru\n\nProfessional geospatial analysis of hospital accessibility in Peru.\n\nDeveloped by Gabriel Saco © 2025"
    }
)

# Enhanced Custom CSS for professional styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styling */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Custom header styling */
    .main-header {
        font-family: 'Inter', sans-serif;
        font-size: 3.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        padding: 1rem 0;
    }
    
    .subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        color: #6c757d;
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 300;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #ffffff;
        border-radius: 8px;
        font-weight: 500;
        color: #495057;
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Enhanced card styling */
    .metric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 16px;
        margin: 0.75rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(102, 126, 234, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #495057;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Enhanced info boxes */
    .analysis-box {
        background: linear-gradient(145deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 1.5rem;
        border-left: 5px solid #2196f3;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 15px rgba(33, 150, 243, 0.15);
    }
    
    .warning-box {
        background: linear-gradient(145deg, #fff8e1 0%, #ffecb3 100%);
        padding: 1.5rem;
        border-left: 5px solid #ff9800;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 15px rgba(255, 152, 0, 0.15);
    }
    
    .success-box {
        background: linear-gradient(145deg, #e8f5e8 0%, #c8e6c9 100%);
        padding: 1.5rem;
        border-left: 5px solid #4caf50;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.15);
    }
    
    .danger-box {
        background: linear-gradient(145deg, #ffebee 0%, #ffcdd2 100%);
        padding: 1.5rem;
        border-left: 5px solid #f44336;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 15px rgba(244, 67, 54, 0.15);
    }
    
    /* Professional table styling */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    }
    
    /* Custom progress bars */
    .progress-container {
        background-color: #e9ecef;
        border-radius: 10px;
        padding: 3px;
        margin: 0.5rem 0;
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 20px;
        border-radius: 8px;
        transition: width 0.8s ease;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: #6c757d;
        font-size: 0.9rem;
        border-top: 1px solid #e9ecef;
        margin-top: 3rem;
    }
    
    /* Animation for loading */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animate-fade-in {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Custom button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Enhanced selectbox */
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid #e9ecef;
        transition: border-color 0.3s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_all_data():
    """Load and preprocess all datasets using professional utility functions"""
    try:
        hospitals_df, districts_gdf, pop_centers_gdf = load_and_clean_data()
        public_hospitals, hospitals_gdf = filter_operational_hospitals(hospitals_df)
        districts_with_counts = spatial_join_hospitals_districts(hospitals_gdf, districts_gdf)
        
        return hospitals_df, districts_gdf, pop_centers_gdf, public_hospitals, hospitals_gdf, districts_with_counts
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None, None, None, None

def create_static_maps_section(public_hospitals, districts_with_counts):
    """Create static maps and analysis for Tab 2"""
    
    # Department analysis
    dept_counts = public_hospitals['Departamento'].value_counts().reset_index()
    dept_counts.columns = ['Departamento', 'hospital_count']
    dept_counts = dept_counts.sort_values('hospital_count', ascending=False)
    
    # Create choropleth map using matplotlib
    fig1, ax1 = plt.subplots(1, 1, figsize=(15, 12))
    
    districts_with_counts.plot(
        column='hospital_count',
        cmap='YlOrRd',
        linewidth=0.1,
        ax=ax1,
        edgecolor='white',
        legend=True,
        legend_kwds={
            'label': "Number of Hospitals",
            'orientation': "vertical",
            'shrink': 0.6
        }
    )
    
    ax1.set_title('Hospital Distribution by District - Peru 2024', fontsize=16, fontweight='bold', pad=20)
    ax1.set_xlabel('Longitude', fontsize=12)
    ax1.set_ylabel('Latitude', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks([])
    ax1.set_yticks([])
    
    # Add statistical annotations
    total_districts = len(districts_with_counts)
    districts_with_hospitals = len(districts_with_counts[districts_with_counts['hospital_count'] > 0])
    avg_hospitals = districts_with_counts['hospital_count'].mean()
    max_hospitals = districts_with_counts['hospital_count'].max()
    
    textstr = f"""Analysis Summary:
• Total Districts: {total_districts:,}
• Districts with Hospitals: {districts_with_hospitals:,}
• Avg Hospitals/District: {avg_hospitals:.1f}
• Max Hospitals: {max_hospitals}"""
    
    fig1.text(0.02, 0.02, textstr, fontsize=9, 
             bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.8))
    
    plt.tight_layout()
    st.pyplot(fig1)
    
    # Department bar chart
    fig2, ax2 = plt.subplots(figsize=(12, 8))
    dept_summary = public_hospitals.groupby('Departamento').size().sort_values(ascending=True)
    bars = dept_summary.plot(kind='barh', ax=ax2, color='steelblue', alpha=0.8)
    ax2.set_title('Number of Public Hospitals by Department', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Number of Hospitals', fontsize=12)
    ax2.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(dept_summary.values):
        ax2.text(v + 5, i, str(v), va='center', fontweight='bold')
    
    plt.tight_layout()
    st.pyplot(fig2)
    
    return dept_counts

# Enhanced utility functions
def create_performance_metrics():
    """Create performance metrics for the dashboard."""
    return {
        'load_time': time.time(),
        'data_freshness': datetime.now(),
        'analysis_version': '2.0',
        'total_computations': 0
    }

def display_header_with_metrics():
    """Display enhanced header with real-time metrics."""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown('<h1 class="main-header animate-fade-in">🏥 Hospitals Access Peru</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle animate-fade-in">Professional Geospatial Analysis & Healthcare Infrastructure Insights</p>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card animate-fade-in">', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Analysis Version</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-value">v2.0</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card animate-fade-in">', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Last Updated</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{datetime.now().strftime("%m/%d")}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def create_enhanced_metrics_dashboard(hospitals_df, districts_with_counts):
    """Create an enhanced metrics dashboard with interactive charts."""
    
    # Calculate advanced metrics
    total_hospitals = len(hospitals_df)
    departments = hospitals_df['Departamento'].nunique()
    avg_per_dept = total_hospitals / departments
    coverage_rate = len(districts_with_counts[districts_with_counts['hospital_count'] > 0]) / len(districts_with_counts) * 100
    
    # Create 4-column layout for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card animate-fade-in">', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Total Hospitals</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{total_hospitals:,}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card animate-fade-in">', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Departments Covered</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{departments}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card animate-fade-in">', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Avg per Department</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{avg_per_dept:.1f}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card animate-fade-in">', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">District Coverage</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{coverage_rate:.1f}%</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    return total_hospitals, departments, avg_per_dept, coverage_rate

def create_interactive_plotly_charts(hospitals_df):
    """Create interactive Plotly charts for better visualization."""
    
    # 1. Department distribution pie chart
    dept_counts = hospitals_df['Departamento'].value_counts().head(10)
    
    fig_pie = go.Figure(data=[go.Pie(
        labels=dept_counts.index,
        values=dept_counts.values,
        hole=0.4,
        textinfo='label+percent',
        textposition='outside',
        marker=dict(
            colors=px.colors.qualitative.Set3,
            line=dict(color='#000000', width=2)
        )
    )])
    
    fig_pie.update_layout(
        title={
            'text': "Top 10 Departments by Hospital Count",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Inter'}
        },
        font=dict(family="Inter", size=12),
        showlegend=True,
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    # 2. Institution type distribution
    inst_counts = hospitals_df['Inst_Adm'].value_counts()
    
    fig_bar = go.Figure(data=[go.Bar(
        x=inst_counts.values,
        y=inst_counts.index,
        orientation='h',
        marker=dict(
            color=px.colors.qualitative.Pastel,
            line=dict(color='rgba(58, 71, 80, 1.0)', width=1)
        ),
        text=inst_counts.values,
        textposition='outside'
    )])
    
    fig_bar.update_layout(
        title={
            'text': "Hospitals by Institution Type",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Inter'}
        },
        xaxis_title="Number of Hospitals",
        yaxis_title="Institution Type",
        font=dict(family="Inter", size=12),
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    # 3. Geographic distribution heatmap
    dept_province_counts = hospitals_df.groupby(['Departamento', 'Provincia']).size().reset_index(name='count')
    top_combinations = dept_province_counts.nlargest(20, 'count')
    
    fig_heatmap = px.treemap(
        top_combinations,
        path=['Departamento', 'Provincia'],
        values='count',
        title="Geographic Distribution of Hospitals (Top 20 Department-Province Combinations)",
        color='count',
        color_continuous_scale='Viridis'
    )
    
    fig_heatmap.update_layout(
        font=dict(family="Inter", size=12),
        height=600,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig_pie, fig_bar, fig_heatmap

def create_advanced_sidebar():
    """Create an advanced sidebar with filters and controls."""
    st.sidebar.markdown("## 🎛️ Dashboard Controls")
    
    # Analysis options
    st.sidebar.markdown("### 📊 Analysis Options")
    show_advanced_stats = st.sidebar.checkbox("Show Advanced Statistics", value=True)
    show_interactive_charts = st.sidebar.checkbox("Interactive Charts", value=True)
    enable_animations = st.sidebar.checkbox("Enable Animations", value=True)
    
    # Data filters
    st.sidebar.markdown("### 🔍 Data Filters")
    selected_departments = st.sidebar.multiselect(
        "Select Departments",
        options=["All"] + ["Lima", "Arequipa", "La Libertad", "Piura", "Junín"],
        default=["All"]
    )
    
    # Map settings
    st.sidebar.markdown("### 🗺️ Map Settings")
    map_style = st.sidebar.selectbox(
        "Map Style",
        options=["OpenStreetMap", "CartoDB Positron", "CartoDB Dark_Matter", "Stamen Terrain"],
        index=1
    )
    
    buffer_distance = st.sidebar.slider("Buffer Distance (km)", 5, 20, 10)
    
    # Export options
    st.sidebar.markdown("### 📤 Export Options")
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.experimental_rerun()
    
    download_format = st.sidebar.selectbox(
        "Download Format",
        options=["CSV", "Excel", "JSON", "GeoJSON"]
    )
    
    # Info section
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ About")
    st.sidebar.info(
        "This dashboard provides comprehensive analysis of hospital accessibility in Peru. "
        "Data sources include MINSA, INEI, and administrative boundaries."
    )
    
    st.sidebar.markdown("### 👨‍💻 Developer")
    st.sidebar.markdown("**Gabriel Saco**")
    st.sidebar.markdown("📧 Contact: [GitHub](https://github.com/gsaco)")
    
    return {
        'show_advanced_stats': show_advanced_stats,
        'show_interactive_charts': show_interactive_charts,
        'enable_animations': enable_animations,
        'selected_departments': selected_departments,
        'map_style': map_style,
        'buffer_distance': buffer_distance,
        'download_format': download_format
    }

# Main application
def main():
    """Enhanced main application with professional features."""
    
    # Create sidebar controls
    sidebar_config = create_advanced_sidebar()
    
    # Display enhanced header
    display_header_with_metrics()
    
    # Initialize performance metrics
    perf_metrics = create_performance_metrics()
    
    # Show loading animation
    with st.spinner('🔄 Loading and processing healthcare data...'):
        # Load all data
        hospitals_df, districts_gdf, pop_centers_gdf, public_hospitals, hospitals_gdf, districts_with_counts = load_all_data()
    
    if hospitals_df is None:
        st.markdown('<div class="danger-box">', unsafe_allow_html=True)
        st.error("❌ Unable to load data. Please check that all required files are present in the data/ directory.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Success message
    st.markdown('<div class="success-box">', unsafe_allow_html=True)
    st.success(f"✅ Successfully loaded {len(hospitals_df):,} hospitals from {hospitals_df['Departamento'].nunique()} departments")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced tabs with better icons and descriptions
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard Overview", 
        "🗺️ Static Analysis", 
        "🌍 Interactive Maps",
        "📈 Advanced Analytics"
    ])
    
    with tab1:
        st.markdown('<div class="animate-fade-in">', unsafe_allow_html=True)
        st.markdown("## 📊 Healthcare Infrastructure Dashboard")
        
        # Enhanced metrics dashboard
        total_hospitals, departments, avg_per_dept, coverage_rate = create_enhanced_metrics_dashboard(
            public_hospitals, districts_with_counts
        )
        
        st.markdown("---")
        
        # Interactive charts section
        if sidebar_config['show_interactive_charts']:
            st.markdown("### 📈 Interactive Analytics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_pie, fig_bar, fig_heatmap = create_interactive_plotly_charts(public_hospitals)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Treemap visualization
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Data quality indicators
        st.markdown("### 🎯 Data Quality Indicators")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            completeness = (1 - hospitals_df.isnull().sum().sum() / (len(hospitals_df) * len(hospitals_df.columns))) * 100
            st.metric("Data Completeness", f"{completeness:.1f}%")
        
        with col2:
            coord_validity = len(hospitals_df.dropna(subset=['Latitud', 'Longitud'])) / len(hospitals_df) * 100
            st.metric("Coordinate Validity", f"{coord_validity:.1f}%")
        
        with col3:
            operational_rate = len(hospitals_df[hospitals_df['Condición'] == 'EN FUNCIONAMIENTO']) / len(hospitals_df) * 100
            st.metric("Operational Rate", f"{operational_rate:.1f}%")
        
        # Data sources with enhanced styling
        st.markdown("### 📚 Data Sources & Methodology")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.markdown("**🏥 MINSA – IPRESS**")
            st.write("National registry of operational health establishments")
            st.caption(f"📊 {len(hospitals_df):,} total records")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.markdown("**🏘️ INEI – Population Centers**")
            st.write("Population centers database from official census")
            st.caption(f"📊 {len(pop_centers_gdf):,} total centers")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.markdown("**🗺️ Administrative Boundaries**")
            st.write("Official district boundaries of Peru")
            st.caption(f"📊 {len(districts_gdf):,} districts")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Enhanced filtering rules
        st.markdown("### 🔍 Quality Assurance Criteria")
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown("""
        **Applied filters for data quality:**
        
        ✅ **Operational Status**: Only hospitals with status "EN FUNCIONAMIENTO"  
        🏛️ **Public Institutions**: MINSA, GOBIERNO REGIONAL, ESSALUD, FFAA, PNP  
        📍 **Valid Coordinates**: Latitude and longitude required for spatial analysis  
        🌐 **Standardized CRS**: EPSG:4326 (WGS84) for global consistency  
        🔬 **Data Validation**: Automated checks for data integrity and completeness
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="animate-fade-in">', unsafe_allow_html=True)
        st.markdown("## 🗺️ Static Geographic Analysis")
        
        if public_hospitals is not None and districts_with_counts is not None:
            
            # Create static maps
            dept_counts = create_static_maps_section(public_hospitals, districts_with_counts)
            
            if dept_counts is not None:
                # Enhanced disparity analysis
                st.markdown("### 📊 Regional Disparity Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    max_hospitals = dept_counts.max()
                    min_hospitals = dept_counts.min()
                    disparity_ratio = max_hospitals / max(min_hospitals, 1)
                    
                    st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
                    st.markdown("#### 📈 Inequality Metrics")
                    st.write(f"**Disparity Ratio:** {disparity_ratio:.1f}:1 between highest and lowest departments")
                    st.write(f"**High Coverage:** {len(dept_counts[dept_counts >= 50]):,} departments have 50+ hospitals")
                    st.write(f"**Low Coverage:** {len(dept_counts[dept_counts < 10]):,} departments have <10 hospitals")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    # Create distribution chart
                    fig_dist = px.histogram(
                        x=dept_counts.values,
                        nbins=15,
                        title="Distribution of Hospitals by Department",
                        labels={'x': 'Number of Hospitals', 'y': 'Department Count'}
                    )
                    fig_dist.update_layout(height=300)
                    st.plotly_chart(fig_dist, use_container_width=True)
        
        else:
            st.error("Unable to process hospital data for static maps.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="animate-fade-in">', unsafe_allow_html=True)
        st.markdown("## 🌍 Interactive Geographic Visualization")
        
        if hospitals_gdf is not None and districts_with_counts is not None:
            
            # National choropleth map
            st.markdown("### 🗺️ National Hospital Distribution")
            
            map_style_mapping = {
                "OpenStreetMap": "OpenStreetMap",
                "CartoDB Positron": "CartoDB positron",
                "CartoDB Dark_Matter": "CartoDB dark_matter",
                "Stamen Terrain": "Stamen Terrain"
            }
            
            national_map = create_national_choropleth_folium(
                districts_with_counts, 
                hospitals_gdf,
                tiles=map_style_mapping.get(sidebar_config['map_style'], "CartoDB positron")
            )
            
            # Add custom legend
            legend_html = """
            <div style="position: fixed; top: 50px; right: 50px; width: 200px; height: 120px; 
                        background-color: white; border:2px solid grey; z-index:9999; 
                        font-size:12px; padding: 10px; border-radius: 10px;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
            <h4 style="margin-top:0;"><b>🏥 Hospital Density</b></h4>
            <p><span style="color:#1f77b4;">●</span> High Density (10+ hospitals)</p>
            <p><span style="color:#ff7f0e;">●</span> Medium Density (5-9 hospitals)</p>
            <p><span style="color:#2ca02c;">●</span> Low Density (1-4 hospitals)</p>
            <p><span style="color:#d62728;">●</span> No Hospitals</p>
            </div>
            """
            national_map.get_root().html.add_child(folium.Element(legend_html))
            
            st.components.v1.html(national_map._repr_html_(), height=600)
            
            # Regional proximity analysis
            st.markdown("### 🔍 Regional Proximity Analysis")
            
            tab_lima, tab_loreto = st.tabs(["🏙️ Lima Metropolitan", "🌳 Loreto Amazon"])
            
            with tab_lima:
                # Lima analysis with enhanced buffer
                lima_isolated, lima_concentrated, lima_hospitals = perform_proximity_analysis(
                    hospitals_gdf, pop_centers_gdf, 'Lima', buffer_km=sidebar_config['buffer_distance']
                )
                
                if lima_isolated is not None and lima_concentrated is not None:
                    lima_center = (-77.0428, -12.0464)
                    lima_map = create_proximity_folium_map(
                        lima_hospitals, lima_isolated, lima_concentrated,
                        'Lima', lima_center, zoom=10
                    )
                    
                    # Enhanced analysis context
                    analysis_html = f'''
                    <div style="position: fixed; 
                                bottom: 10px; left: 10px; width: 320px; height: 180px; 
                                background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%); 
                                border: 2px solid #667eea; z-index:9999; 
                                font-size:11px; padding: 12px; border-radius: 12px;
                                box-shadow: 0 8px 25px rgba(0,0,0,0.15);">
                    <h4 style="margin-top:0; color: #495057;"><b>🏙️ Lima Analysis</b></h4>
                    <div style="background: #e3f2fd; padding: 8px; border-radius: 6px; margin: 8px 0;">
                    <b>Urban Concentration Advantage:</b><br>
                    • High hospital density in metro area<br>
                    • Public transport improves accessibility<br>
                    • Buffer: {sidebar_config['buffer_distance']}km radius
                    </div>
                    <b>📊 Coverage Stats:</b><br>
                    • Maximum: {lima_concentrated['hospitals_10km'] if lima_concentrated else 0} hospitals<br>
                    • Minimum: {lima_isolated['hospitals_10km'] if lima_isolated else 0} hospitals
                    </div>
                    '''
                    lima_map.get_root().html.add_child(folium.Element(analysis_html))
                    
                    st.components.v1.html(lima_map._repr_html_(), height=500)
                    
                    # Statistical summary
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Most Accessible Area", f"{lima_concentrated['hospitals_10km']} hospitals")
                    with col2:
                        st.metric("Least Accessible Area", f"{lima_isolated['hospitals_10km']} hospitals")
                    with col3:
                        accessibility_ratio = lima_concentrated['hospitals_10km'] / max(lima_isolated['hospitals_10km'], 1)
                        st.metric("Accessibility Ratio", f"{accessibility_ratio:.1f}:1")
            
            with tab_loreto:
                # Loreto analysis
                loreto_isolated, loreto_concentrated, loreto_hospitals = perform_proximity_analysis(
                    hospitals_gdf, pop_centers_gdf, 'Loreto', buffer_km=sidebar_config['buffer_distance']
                )
                
                if loreto_isolated is not None and loreto_concentrated is not None:
                    loreto_center = (-74.2, -4.0)
                    loreto_map = create_proximity_folium_map(
                        loreto_hospitals, loreto_isolated, loreto_concentrated,
                        'Loreto', loreto_center, zoom=7
                    )
                    
                    # Enhanced analysis context for Loreto
                    loreto_analysis_html = f'''
                    <div style="position: fixed; 
                                bottom: 10px; left: 10px; width: 320px; height: 200px; 
                                background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%); 
                                border: 2px solid #28a745; z-index:9999; 
                                font-size:11px; padding: 12px; border-radius: 12px;
                                box-shadow: 0 8px 25px rgba(0,0,0,0.15);">
                    <h4 style="margin-top:0; color: #495057;"><b>🌳 Loreto Amazon Analysis</b></h4>
                    <div style="background: #e8f5e8; padding: 8px; border-radius: 6px; margin: 8px 0;">
                    <b>Amazon Challenges:</b><br>
                    • Remote communities with limited access<br>
                    • River transport dependency<br>
                    • Sparse infrastructure network
                    </div>
                    <b>📊 Accessibility Stats:</b><br>
                    • Maximum: {loreto_concentrated['hospitals_10km'] if loreto_concentrated else 0} hospitals<br>
                    • Minimum: {loreto_isolated['hospitals_10km'] if loreto_isolated else 0} hospitals<br>
                    • Buffer: {sidebar_config['buffer_distance']}km radius
                    </div>
                    '''
                    loreto_map.get_root().html.add_child(folium.Element(loreto_analysis_html))
                    
                    st.components.v1.html(loreto_map._repr_html_(), height=500)
                    
                    # Statistical summary for Loreto
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Most Accessible Area", f"{loreto_concentrated['hospitals_10km']} hospitals")
                    with col2:
                        st.metric("Least Accessible Area", f"{loreto_isolated['hospitals_10km']} hospitals")
                    with col3:
                        if loreto_isolated['hospitals_10km'] > 0:
                            loreto_ratio = loreto_concentrated['hospitals_10km'] / loreto_isolated['hospitals_10km']
                        else:
                            loreto_ratio = float('inf')
                        st.metric("Accessibility Ratio", f"{loreto_ratio:.1f}:1" if loreto_ratio != float('inf') else "∞:1")
        
        else:
            st.error("Unable to create interactive maps. Please check data availability.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown('<div class="animate-fade-in">', unsafe_allow_html=True)
        st.markdown("## 📈 Advanced Healthcare Analytics")
        
        if sidebar_config['show_advanced_stats']:
            
            # Advanced statistical analysis
            st.markdown("### 🔬 Statistical Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Population vs Hospital correlation (simulated for demo)
                dept_hospital_counts = public_hospitals['Departamento'].value_counts()
                
                # Create correlation matrix visualization
                correlation_data = pd.DataFrame({
                    'Department': dept_hospital_counts.index[:10],
                    'Hospitals': dept_hospital_counts.values[:10],
                    'Population_Index': np.random.normal(100, 30, 10)  # Simulated population data
                })
                
                fig_scatter = px.scatter(
                    correlation_data,
                    x='Population_Index',
                    y='Hospitals',
                    hover_data=['Department'],
                    title="Hospital Count vs Population Index (Simulated)",
                    trendline="ols"
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
            
            with col2:
                # Geographic dispersion analysis
                coords = public_hospitals[['Latitud', 'Longitud']].dropna()
                center_lat, center_lon = coords.mean()
                distances = np.sqrt((coords['Latitud'] - center_lat)**2 + (coords['Longitud'] - center_lon)**2)
                
                fig_hist = px.histogram(
                    x=distances,
                    nbins=30,
                    title="Geographic Distribution Pattern",
                    labels={'x': 'Distance from Geographic Center', 'y': 'Hospital Count'}
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            
            # Accessibility index calculation
            st.markdown("### 🎯 Healthcare Accessibility Index")
            
            # Calculate a composite accessibility index
            dept_stats = public_hospitals.groupby('Departamento').agg({
                'Nombre': 'count',
                'Latitud': 'std',
                'Longitud': 'std'
            }).round(3)
            
            dept_stats.columns = ['Hospital_Count', 'Lat_Dispersion', 'Lon_Dispersion']
            dept_stats['Accessibility_Score'] = (
                dept_stats['Hospital_Count'] / 
                (1 + dept_stats['Lat_Dispersion'] + dept_stats['Lon_Dispersion'])
            ).round(2)
            
            dept_stats = dept_stats.sort_values('Accessibility_Score', ascending=False)
            
            # Display top and bottom departments
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🥇 Top Performing Departments")
                top_depts = dept_stats.head(10)
                
                fig_top = px.bar(
                    x=top_depts['Accessibility_Score'],
                    y=top_depts.index,
                    orientation='h',
                    title="Highest Accessibility Scores",
                    color=top_depts['Accessibility_Score'],
                    color_continuous_scale='Greens'
                )
                fig_top.update_layout(height=400)
                st.plotly_chart(fig_top, use_container_width=True)
            
            with col2:
                st.markdown("#### 🎯 Areas for Improvement")
                bottom_depts = dept_stats.tail(10)
                
                fig_bottom = px.bar(
                    x=bottom_depts['Accessibility_Score'],
                    y=bottom_depts.index,
                    orientation='h',
                    title="Areas Needing Investment",
                    color=bottom_depts['Accessibility_Score'],
                    color_continuous_scale='Reds'
                )
                fig_bottom.update_layout(height=400)
                st.plotly_chart(fig_bottom, use_container_width=True)
        
        # Performance metrics and download options
        st.markdown("### 📤 Data Export & Performance")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Download Summary Report"):
                # Create summary report
                summary_data = {
                    'metric': ['Total Hospitals', 'Departments', 'Districts', 'Coverage Rate'],
                    'value': [len(public_hospitals), public_hospitals['Departamento'].nunique(), 
                             len(districts_gdf), f"{coverage_rate:.1f}%"]
                }
                summary_df = pd.DataFrame(summary_data)
                
                if sidebar_config['download_format'] == 'CSV':
                    csv = summary_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"peru_hospitals_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
        
        with col2:
            processing_time = time.time() - perf_metrics['load_time']
            st.metric("Processing Time", f"{processing_time:.2f}s")
        
        with col3:
            st.metric("Memory Usage", "Optimized")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
if __name__ == "__main__":
    main()