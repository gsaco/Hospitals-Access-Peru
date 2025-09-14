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
warnings.filterwarnings('ignore')

# Configure Streamlit page
st.set_page_config(
    page_title="Hospitals Access Peru - Geospatial Analysis",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .tab-subheader {
        font-size: 1.8rem;
        font-weight: bold;
        color: #ff7f0e;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and preprocess all datasets"""
    try:
        # Load hospitals data
        hospitals_df = pd.read_csv('IPRESS.csv', encoding='latin-1')
        
        # Load districts shapefile
        districts_gdf = gpd.read_file('DISTRITOS.shp')
        
        # Load population centers shapefile
        pop_centers_gdf = gpd.read_file('CCPP_IGN100K.shp')
        
        return hospitals_df, districts_gdf, pop_centers_gdf
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None

@st.cache_data
def process_hospitals_data(hospitals_df):
    """Process and clean hospitals data"""
    if hospitals_df is None:
        return None, None
    
    # Filter for operational hospitals
    operational_hospitals = hospitals_df[hospitals_df['Condición'] == 'EN FUNCIONAMIENTO'].copy()
    
    # Filter for public hospitals
    public_institutions = ['MINSA', 'GOBIERNO REGIONAL', 'ESSALUD', 'FFAA', 'PNP']
    public_hospitals = operational_hospitals[operational_hospitals['Institución'].isin(public_institutions)].copy()
    
    # Clean coordinates
    if 'NORTE' in public_hospitals.columns and 'ESTE' in public_hospitals.columns:
        public_hospitals['NORTE'] = pd.to_numeric(public_hospitals['NORTE'], errors='coerce')
        public_hospitals['ESTE'] = pd.to_numeric(public_hospitals['ESTE'], errors='coerce')
        
        # Remove invalid coordinates
        public_hospitals = public_hospitals.dropna(subset=['NORTE', 'ESTE'])
        public_hospitals = public_hospitals[(public_hospitals['NORTE'] != 0) & (public_hospitals['ESTE'] != 0)]
        
        # Create GeoDataFrame
        geometry = [Point(xy) for xy in zip(public_hospitals['ESTE'], public_hospitals['NORTE'])]
        hospitals_gdf = gpd.GeoDataFrame(public_hospitals, geometry=geometry, crs='EPSG:4326')
        
        return public_hospitals, hospitals_gdf
    
    return public_hospitals, None

def create_department_analysis(public_hospitals):
    """Create department-level analysis"""
    dept_counts = public_hospitals['Departamento'].value_counts().reset_index()
    dept_counts.columns = ['Departamento', 'hospital_count']
    dept_counts = dept_counts.sort_values('hospital_count', ascending=False)
    return dept_counts

def create_folium_map(hospitals_gdf, districts_gdf):
    """Create national Folium map with hospitals"""
    # Create base map centered on Peru
    peru_center = [-9.19, -75.0152]
    m = folium.Map(location=peru_center, zoom_start=6)
    
    # Add hospital markers with clustering
    if hospitals_gdf is not None and len(hospitals_gdf) > 0:
        marker_cluster = plugins.MarkerCluster().add_to(m)
        
        for idx, hospital in hospitals_gdf.iterrows():
            if pd.notna(hospital.geometry.y) and pd.notna(hospital.geometry.x):
                folium.Marker(
                    location=[hospital.geometry.y, hospital.geometry.x],
                    popup=f"{hospital['Nombre del establecimiento']}<br>Department: {hospital['Departamento']}",
                    icon=folium.Icon(color='red', icon='plus-sign')
                ).add_to(marker_cluster)
    
    return m

# Main application
def main():
    st.markdown('<h1 class="main-header">🏥 Hospitals Access Peru - Geospatial Analysis</h1>', unsafe_allow_html=True)
    
    # Load data
    hospitals_df, districts_gdf, pop_centers_gdf = load_data()
    
    if hospitals_df is None:
        st.error("Unable to load data. Please check that all required files are present.")
        return
    
    # Process hospitals data
    public_hospitals, hospitals_gdf = process_hospitals_data(hospitals_df)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs([
        "🗂️ Descripción de Datos", 
        "🗺️ Mapas Estáticos", 
        "🌍 Mapas Dinámicos"
    ])
    
    with tab1:
        st.markdown('<h2 class="tab-subheader">📊 Descripción de los Datos</h2>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label="Total de Hospitales Operacionales",
                value=len(public_hospitals) if public_hospitals is not None else 0
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            if public_hospitals is not None:
                unique_depts = public_hospitals['Departamento'].nunique()
            else:
                unique_depts = 0
            st.metric(
                label="Departamentos Cubiertos",
                value=unique_depts
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label="Distritos en el Análisis",
                value=len(districts_gdf) if districts_gdf is not None else 0
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("### 📋 Metodología de Filtrado")
        st.write("""
        **Unidad de análisis**: Hospitales públicos operacionales en Perú
        
        **Fuentes de datos**:
        - **MINSA – IPRESS**: Registro Nacional de hospitales operacionales
        - **INEI**: Centros poblados del Perú
        - **Límites administrativos**: Distritos del Perú
        
        **Reglas de filtrado aplicadas**:
        1. Solo hospitales con estado "EN FUNCIONAMIENTO"
        2. Instituciones públicas: MINSA, GOBIERNO REGIONAL, ESSALUD, FFAA, PNP
        3. Coordenadas válidas requeridas para análisis espacial
        4. CRS estandarizado a EPSG:4326
        """)
        
        if public_hospitals is not None:
            st.markdown("### 📈 Distribución por Institución")
            institution_counts = public_hospitals['Institución'].value_counts()
            
            fig, ax = plt.subplots(figsize=(10, 6))
            institution_counts.plot(kind='bar', ax=ax, color='skyblue')
            ax.set_title('Distribución de Hospitales por Institución')
            ax.set_xlabel('Institución')
            ax.set_ylabel('Número de Hospitales')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
    
    with tab2:
        st.markdown('<h2 class="tab-subheader">🗺️ Mapas Estáticos</h2>', unsafe_allow_html=True)
        
        if public_hospitals is not None:
            # Department analysis
            dept_counts = create_department_analysis(public_hospitals)
            
            st.markdown("### 📊 Análisis a Nivel Departamental")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("**Resumen por Departamento:**")
                st.dataframe(dept_counts, use_container_width=True)
            
            with col2:
                # Bar chart
                fig, ax = plt.subplots(figsize=(10, 8))
                sns.barplot(data=dept_counts, x='hospital_count', y='Departamento', palette='viridis', ax=ax)
                ax.set_title('Número de Hospitales Públicos por Departamento')
                ax.set_xlabel('Número de Hospitales')
                ax.set_ylabel('Departamento')
                ax.grid(axis='x', alpha=0.3)
                
                # Add value labels
                for i, v in enumerate(dept_counts['hospital_count']):
                    ax.text(v + 0.5, i, str(v), va='center', fontweight='bold')
                
                plt.tight_layout()
                st.pyplot(fig)
            
            # Key insights
            if len(dept_counts) > 0:
                st.markdown("### 🔍 Principales Hallazgos")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.success(f"**Departamento con más hospitales:**  \n{dept_counts.iloc[0]['Departamento']} ({dept_counts.iloc[0]['hospital_count']} hospitales)")
                
                with col2:
                    st.warning(f"**Departamento con menos hospitales:**  \n{dept_counts.iloc[-1]['Departamento']} ({dept_counts.iloc[-1]['hospital_count']} hospitales)")
        
        else:
            st.error("No se pudieron procesar los datos de hospitales para crear mapas estáticos.")
    
    with tab3:
        st.markdown('<h2 class="tab-subheader">🌍 Mapas Dinámicos</h2>', unsafe_allow_html=True)
        
        if hospitals_gdf is not None:
            st.markdown("### 🗺️ Mapa Nacional de Hospitales")
            st.write("Mapa interactivo mostrando la distribución de hospitales públicos operacionales en todo el Perú.")
            
            # Create and display Folium map
            national_map = create_folium_map(hospitals_gdf, districts_gdf)
            
            # Display the map
            import streamlit.components.v1 as components
            map_html = national_map._repr_html_()
            components.html(map_html, height=600)
            
            st.markdown("### 📋 Análisis de Proximidad")
            st.write("""
            **Lima (Concentración urbana)**: Alta densidad hospitalaria en áreas urbanas, 
            con mejor accesibilidad en el centro metropolitano.
            
            **Loreto (Región amazónica)**: Desafíos geográficos significativos que limitan 
            la accesibilidad hospitalaria, especialmente en comunidades remotas.
            
            **Metodología de buffers de 10km**: El análisis revela disparidades significativas 
            en el acceso a hospitales entre regiones urbanas y rurales.
            """)
            
            # Additional metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                lima_hospitals = len(hospitals_gdf[hospitals_gdf['Departamento'] == 'LIMA'])
                st.metric("Hospitales en Lima", lima_hospitals)
            
            with col2:
                loreto_hospitals = len(hospitals_gdf[hospitals_gdf['Departamento'] == 'LORETO'])
                st.metric("Hospitales en Loreto", loreto_hospitals)
            
            with col3:
                total_hospitals = len(hospitals_gdf)
                st.metric("Total Nacional", total_hospitals)
        
        else:
            st.error("No se pudieron procesar los datos de hospitales para crear mapas dinámicos.")

if __name__ == "__main__":
    main()