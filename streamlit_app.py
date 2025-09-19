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
    .analysis-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-left: 4px solid #1f77b4;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-left: 4px solid #ffc107;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-left: 4px solid #28a745;
        border-radius: 5px;
        margin: 1rem 0;
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

def create_proximity_analysis_maps(hospitals_gdf, pop_centers_gdf):
    """Create proximity analysis for Lima and Loreto"""
    
    # Lima analysis
    lima_isolated, lima_concentrated, lima_hospitals = perform_proximity_analysis(
        hospitals_gdf, pop_centers_gdf, 'Lima', buffer_km=10
    )
    
    # Loreto analysis
    loreto_isolated, loreto_concentrated, loreto_hospitals = perform_proximity_analysis(
        hospitals_gdf, pop_centers_gdf, 'Loreto', buffer_km=10
    )
    
    return (lima_isolated, lima_concentrated, lima_hospitals, 
            loreto_isolated, loreto_concentrated, loreto_hospitals)

# Main application
def main():
    st.markdown('<h1 class="main-header">🏥 Hospitals Access Peru - Geospatial Analysis</h1>', unsafe_allow_html=True)
    
    # Load all data
    hospitals_df, districts_gdf, pop_centers_gdf, public_hospitals, hospitals_gdf, districts_with_counts = load_all_data()
    
    if hospitals_df is None:
        st.error("Unable to load data. Please check that all required files are present.")
        return
    
    # Create tabs with icons as shown in the homework
    tab1, tab2, tab3 = st.tabs([
        "🗂️ Descripción de Datos", 
        "🗺️ Mapas Estáticos", 
        "🌍 Mapas Dinámicos"
    ])
    
    with tab1:
        st.markdown('<h2 class="tab-subheader">📊 Descripción de los Datos</h2>', unsafe_allow_html=True)
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label="Total de Hospitales Operacionales",
                value=f"{len(public_hospitals):,}" if public_hospitals is not None else 0
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
                value=f"{len(districts_gdf):,}" if districts_gdf is not None else 0
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            if districts_with_counts is not None:
                zero_districts = len(districts_with_counts[districts_with_counts['hospital_count'] == 0])
            else:
                zero_districts = 0
            st.metric(
                label="Distritos Sin Hospitales",
                value=f"{zero_districts:,}",
                delta=f"-{(zero_districts/len(districts_with_counts)*100):.1f}%" if districts_with_counts is not None else None
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Unit of analysis section
        st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
        st.markdown("### 📋 Unidad de Análisis")
        st.write("**Hospitales públicos operacionales en Perú**")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Data sources section
        st.markdown("### 📊 Fuentes de Datos")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.markdown("**MINSA – IPRESS**")
            st.write("Registro Nacional de establecimientos de salud operacionales")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.markdown("**INEI – Centros Poblados**")
            st.write("Base de datos de centros poblados del Perú")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.markdown("**Límites Administrativos**")
            st.write("Distritos oficiales del Perú")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Filtering rules section
        st.markdown("### 🔍 Reglas de Filtrado")
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown("""
        **Criterios aplicados para garantizar calidad de datos:**
        
        1. ✅ **Estado Operacional**: Solo hospitales con estado "EN FUNCIONAMIENTO"
        2. 🏛️ **Instituciones Públicas**: MINSA, GOBIERNO REGIONAL, ESSALUD, FFAA, PNP
        3. 📍 **Coordenadas Válidas**: Latitud y longitud requeridas para análisis espacial
        4. 🌐 **CRS Estandarizado**: EPSG:4326 (WGS84) para consistencia global
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if public_hospitals is not None:
            # Institution distribution
            st.markdown("### 📈 Distribución por Institución")
            
            institution_counts = public_hospitals['Institución'].value_counts()
            
            # Create interactive plotly chart
            fig = px.pie(
                values=institution_counts.values,
                names=institution_counts.index,
                title="Distribución de Hospitales por Institución",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # Summary table
            st.markdown("### 📋 Resumen Estadístico")
            
            col1, col2 = st.columns(2)
            
            with col1:
                summary_stats = create_summary_statistics(public_hospitals, districts_with_counts)
                
                metrics_df = pd.DataFrame({
                    'Métrica': [
                        'Total de Hospitales',
                        'Departamentos Cubiertos', 
                        'Distritos con Hospitales',
                        'Distritos sin Hospitales',
                        'Promedio por Distrito'
                    ],
                    'Valor': [
                        f"{summary_stats['total_hospitals']:,}",
                        f"{summary_stats['departments_covered']:,}",
                        f"{summary_stats['districts_with_hospitals']:,}",
                        f"{summary_stats['districts_without_hospitals']:,}",
                        f"{summary_stats['avg_hospitals_per_district']:.1f}"
                    ]
                })
                
                st.dataframe(metrics_df, use_container_width=True)
            
            with col2:
                # Top departments
                dept_counts = public_hospitals['Departamento'].value_counts().head(10)
                st.markdown("**Top 10 Departamentos:**")
                for dept, count in dept_counts.items():
                    st.write(f"• {dept}: {count:,} hospitales")
    
    with tab2:
        st.markdown('<h2 class="tab-subheader">🗺️ Mapas Estáticos & Análisis Departamental</h2>', unsafe_allow_html=True)
        
        if public_hospitals is not None and districts_with_counts is not None:
            
            # Create static maps
            dept_counts = create_static_maps_section(public_hospitals, districts_with_counts)
            
            st.markdown("### 📊 Análisis a Nivel Departamental")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("**Resumen por Departamento:**")
                st.dataframe(dept_counts, use_container_width=True)
            
            with col2:
                # Interactive department chart
                fig = px.bar(
                    dept_counts.head(15), 
                    x='hospital_count', 
                    y='Departamento',
                    orientation='h',
                    title='Top 15 Departamentos por Número de Hospitales',
                    color='hospital_count',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True)
            
            # Key insights
            if len(dept_counts) > 0:
                st.markdown("### 🔍 Principales Hallazgos")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.markdown(f"**🏆 Departamento con más hospitales:**")
                    st.markdown(f"**{dept_counts.iloc[0]['Departamento']}** con **{dept_counts.iloc[0]['hospital_count']:,} hospitales**")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                    st.markdown(f"**⚠️ Departamento con menos hospitales:**")
                    st.markdown(f"**{dept_counts.iloc[-1]['Departamento']}** con **{dept_counts.iloc[-1]['hospital_count']:,} hospitales**")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                # Disparity analysis
                max_hospitals = dept_counts.iloc[0]['hospital_count']
                min_hospitals = dept_counts.iloc[-1]['hospital_count']
                disparity_ratio = max_hospitals / max(min_hospitals, 1)
                
                st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
                st.markdown(f"### 📊 Análisis de Disparidad")
                st.write(f"**Ratio de disparidad:** {disparity_ratio:.1f}:1 entre el departamento con más y menos hospitales")
                st.write(f"**Distribución:** {len(dept_counts[dept_counts['hospital_count'] >= 50]):,} departamentos tienen 50+ hospitales")
                st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            st.error("No se pudieron procesar los datos de hospitales para crear mapas estáticos.")
    
    with tab3:
        st.markdown('<h2 class="tab-subheader">🌍 Mapas Dinámicos</h2>', unsafe_allow_html=True)
        
        if hospitals_gdf is not None and districts_with_counts is not None:
            
            # National choropleth map
            st.markdown("### 🗺️ Mapa Nacional de Hospitales")
            st.write("Mapa interactivo con coropletas a nivel distrital y marcadores de hospitales agrupados.")
            
            national_map = create_national_choropleth_folium(districts_with_counts, hospitals_gdf)
            
            # Add title
            title_html = '''
            <h3 style="position: fixed; 
                       top: 10px; left: 50px; width: 400px; height: 60px; 
                       background-color: white; border:2px solid grey; z-index:9999; 
                       font-size:16px; text-align: center; padding: 10px">
            <b>🏥 Distribución Nacional de Hospitales - Perú 2024</b><br>
            <small>Coropletas distritales con marcadores agrupados</small>
            </h3>
            '''
            national_map.get_root().html.add_child(folium.Element(title_html))
            
            # Display the map
            import streamlit.components.v1 as components
            map_html = national_map._repr_html_()
            components.html(map_html, height=600)
            
            # Proximity analysis section
            st.markdown("### 📍 Análisis de Proximidad - Lima & Loreto")
            
            # Perform proximity analysis
            (lima_isolated, lima_concentrated, lima_hospitals, 
             loreto_isolated, loreto_concentrated, loreto_hospitals) = create_proximity_analysis_maps(
                hospitals_gdf, pop_centers_gdf
            )
            
            # Display proximity maps
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🏙️ Lima (Concentración Urbana)")
                
                if lima_isolated is not None and lima_concentrated is not None:
                    lima_center = [-12.0464, -77.0428]
                    lima_map = create_proximity_folium_map(
                        lima_hospitals, lima_isolated, lima_concentrated,
                        'Lima', lima_center, zoom=10
                    )
                    
                    # Add analysis context
                    analysis_html = f'''
                    <div style="position: fixed; 
                                bottom: 10px; left: 10px; width: 280px; height: 160px; 
                                background-color: white; border:2px solid grey; z-index:9999; 
                                font-size:11px; padding: 8px">
                    <b>🏙️ Análisis Lima</b><br><br>
                    <b>Concentración urbana:</b><br>
                    • Alta densidad hospitalaria<br>
                    • Transporte público mejora acceso<br>
                    • Máximo: {lima_concentrated['hospitals_10km']} hospitales<br>
                    • Mínimo: {lima_isolated['hospitals_10km']} hospitales<br>
                    <br><b>Desafío:</b> Periferia urbana
                    </div>
                    '''
                    lima_map.get_root().html.add_child(folium.Element(analysis_html))
                    
                    map_html = lima_map._repr_html_()
                    components.html(map_html, height=400)
                    
                    # Lima metrics
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.markdown(f"**Hospitales en Lima:** {len(lima_hospitals):,}")
                    st.markdown(f"**Acceso máximo:** {lima_concentrated['hospitals_10km']} hospitales en 10km")
                    st.markdown(f"**Acceso mínimo:** {lima_isolated['hospitals_10km']} hospitales en 10km")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                else:
                    st.warning("No se pudo completar el análisis de Lima")
            
            with col2:
                st.markdown("#### 🌳 Loreto (Desafíos Amazónicos)")
                
                if loreto_isolated is not None and loreto_concentrated is not None:
                    loreto_center = [-4.2312, -73.2516]
                    loreto_map = create_proximity_folium_map(
                        loreto_hospitals, loreto_isolated, loreto_concentrated,
                        'Loreto', loreto_center, zoom=8
                    )
                    
                    # Add analysis context
                    analysis_html = f'''
                    <div style="position: fixed; 
                                bottom: 10px; left: 10px; width: 280px; height: 180px; 
                                background-color: white; border:2px solid grey; z-index:9999; 
                                font-size:11px; padding: 8px">
                    <b>🌳 Análisis Loreto</b><br><br>
                    <b>Desafíos geográficos:</b><br>
                    • Selva densa limita acceso<br>
                    • Ríos como transporte principal<br>
                    • Inundaciones estacionales<br>
                    • Máximo: {loreto_concentrated['hospitals_10km']} hospitales<br>
                    • Mínimo: {loreto_isolated['hospitals_10km']} hospitales<br>
                    <br><b>Necesidades:</b> Telemedicina, unidades móviles
                    </div>
                    '''
                    loreto_map.get_root().html.add_child(folium.Element(analysis_html))
                    
                    map_html = loreto_map._repr_html_()
                    components.html(map_html, height=400)
                    
                    # Loreto metrics
                    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                    st.markdown(f"**Hospitales en Loreto:** {len(loreto_hospitals):,}")
                    st.markdown(f"**Acceso máximo:** {loreto_concentrated['hospitals_10km']} hospitales en 10km")
                    st.markdown(f"**Acceso mínimo:** {loreto_isolated['hospitals_10km']} hospitales en 10km")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                else:
                    st.warning("No se pudo completar el análisis de Loreto")
            
            # Comparative analysis
            if (lima_hospitals is not None and loreto_hospitals is not None and
                lima_concentrated is not None and loreto_concentrated is not None):
                
                st.markdown("### 🔄 Análisis Comparativo")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    disparity_ratio = len(lima_hospitals) / max(len(loreto_hospitals), 1)
                    st.metric(
                        "Ratio Urbano/Amazónico",
                        f"{disparity_ratio:.1f}:1",
                        delta=f"Lima tiene {disparity_ratio:.1f}x más hospitales"
                    )
                
                with col2:
                    access_disparity = lima_concentrated['hospitals_10km'] / max(loreto_concentrated['hospitals_10km'], 1)
                    st.metric(
                        "Disparidad de Acceso Máximo",
                        f"{access_disparity:.1f}:1",
                        delta=f"Lima: {lima_concentrated['hospitals_10km']} vs Loreto: {loreto_concentrated['hospitals_10km']}"
                    )
                
                with col3:
                    total_hospitals = len(lima_hospitals) + len(loreto_hospitals)
                    lima_percentage = (len(lima_hospitals) / total_hospitals) * 100
                    st.metric(
                        "% de Hospitales en Lima",
                        f"{lima_percentage:.1f}%",
                        delta=f"de {total_hospitals:,} hospitales totales"
                    )
            
            # Written analysis section
            st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
            st.markdown("### 📝 Análisis Escrito")
            st.markdown("""
            **Lima (Concentración urbana y accesibilidad):**
            - La concentración urbana permite alta densidad hospitalaria en el área metropolitana
            - Las redes de transporte público facilitan el acceso desde diferentes distritos
            - Los desafíos se concentran en las zonas periféricas en expansión
            - La planificación urbana debe considerar el crecimiento hacia los márgenes
            
            **Loreto (Dispersión geográfica y desafíos de accesibilidad en la Amazonía):**
            - La densa cobertura forestal y los ríos como vías principales limitan el acceso terrestre
            - Las comunidades remotas enfrentan barreras geográficas significativas
            - Las inundaciones estacionales afectan la conectividad y el acceso a servicios
            - Se requieren estrategias especializadas: telemedicina, unidades móviles fluviales, y centros de atención en comunidades clave
            
            **Metodología de buffers de 10km:**
            El análisis revela disparidades significativas en el acceso a hospitales entre regiones urbanas y rurales, 
            destacando la necesidad de políticas diferenciadas según el contexto geográfico y demográfico.
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            st.error("No se pudieron procesar los datos de hospitales para crear mapas dinámicos.")

if __name__ == "__main__":
    main()