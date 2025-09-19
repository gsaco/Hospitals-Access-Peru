# Utilities for Hospital Access Analysis in Peru
# Professional functions for data processing and visualization

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

def load_and_clean_data():
    """
    Load and preprocess all datasets with comprehensive cleaning.
    
    Returns:
        tuple: (hospitals_df, districts_gdf, pop_centers_gdf)
    """
    print("🔄 Loading datasets...")
    
    # Load hospitals data
    hospitals_df = pd.read_csv('IPRESS.csv', encoding='latin-1')
    print(f"✓ Hospitals dataset loaded: {hospitals_df.shape}")
    
    # Load districts shapefile
    districts_gdf = gpd.read_file('DISTRITOS.shp')
    print(f"✓ Districts shapefile loaded: {districts_gdf.shape}")
    
    # Load population centers shapefile
    pop_centers_gdf = gpd.read_file('CCPP_IGN100K.shp')
    print(f"✓ Population centers loaded: {pop_centers_gdf.shape}")
    
    # Standardize CRS to EPSG:4326
    if districts_gdf.crs != 'EPSG:4326':
        districts_gdf = districts_gdf.to_crs('EPSG:4326')
        print("✓ Districts CRS converted to EPSG:4326")
    
    if pop_centers_gdf.crs != 'EPSG:4326':
        pop_centers_gdf = pop_centers_gdf.to_crs('EPSG:4326')
        print("✓ Population centers CRS converted to EPSG:4326")
    
    return hospitals_df, districts_gdf, pop_centers_gdf

def filter_operational_hospitals(hospitals_df):
    """
    Filter hospitals to only operational public facilities with valid coordinates.
    
    Args:
        hospitals_df: Raw hospitals dataframe
    
    Returns:
        tuple: (public_hospitals_df, hospitals_gdf)
    """
    print("\n🔄 Filtering operational hospitals...")
    
    # Filter for operational hospitals
    operational = hospitals_df[hospitals_df['Condición'] == 'EN FUNCIONAMIENTO'].copy()
    print(f"✓ Operational hospitals: {len(operational):,}")
    
    # Filter for public institutions
    public_institutions = ['MINSA', 'GOBIERNO REGIONAL', 'ESSALUD', 'FFAA', 'PNP']
    public_hospitals = operational[operational['Institución'].isin(public_institutions)].copy()
    print(f"✓ Public hospitals: {len(public_hospitals):,}")
    
    # Clean coordinates
    valid_coords = public_hospitals.dropna(subset=['NORTE', 'ESTE'])
    valid_coords['NORTE'] = pd.to_numeric(valid_coords['NORTE'], errors='coerce')
    valid_coords['ESTE'] = pd.to_numeric(valid_coords['ESTE'], errors='coerce')
    
    # Remove invalid coordinates (zeros and out-of-bounds)
    valid_coords = valid_coords[
        (valid_coords['NORTE'] != 0) & 
        (valid_coords['ESTE'] != 0) &
        (valid_coords['NORTE'].abs() <= 90) &
        (valid_coords['ESTE'].abs() <= 180)
    ]
    print(f"✓ With valid coordinates: {len(valid_coords):,}")
    
    # Create GeoDataFrame (NORTE=longitude, ESTE=latitude based on data inspection)
    geometry = [Point(xy) for xy in zip(valid_coords['NORTE'], valid_coords['ESTE'])]
    hospitals_gdf = gpd.GeoDataFrame(valid_coords, geometry=geometry, crs='EPSG:4326')
    
    return valid_coords, hospitals_gdf

def spatial_join_hospitals_districts(hospitals_gdf, districts_gdf):
    """
    Spatially join hospitals to districts and count hospitals per district.
    
    Args:
        hospitals_gdf: GeoDataFrame of hospitals
        districts_gdf: GeoDataFrame of districts
    
    Returns:
        GeoDataFrame: Districts with hospital counts
    """
    print("\n🔄 Performing spatial join...")
    
    # Method 1: Direct UBIGEO matching (faster)
    hospitals_gdf['UBIGEO_clean'] = hospitals_gdf['UBIGEO'].astype(str).str.zfill(6)
    districts_gdf['IDDIST_clean'] = districts_gdf['IDDIST'].astype(str)
    
    # Count hospitals by district code
    hospital_counts = (hospitals_gdf.groupby('UBIGEO_clean').size()
                      .reset_index(name='hospital_count'))
    
    # Merge with districts
    districts_with_counts = districts_gdf.merge(
        hospital_counts, 
        left_on='IDDIST_clean', 
        right_on='UBIGEO_clean', 
        how='left'
    ).fillna({'hospital_count': 0})
    
    assigned_count = hospital_counts['hospital_count'].sum()
    zero_districts = (districts_with_counts['hospital_count'] == 0).sum()
    
    print(f"✓ Hospitals assigned: {assigned_count:,}")
    print(f"✓ Districts with zero hospitals: {zero_districts:,}")
    
    return districts_with_counts

def create_choropleth_map(districts_with_counts, title="Hospital Distribution by District"):
    """
    Create a professional choropleth map of hospital distribution.
    
    Args:
        districts_with_counts: GeoDataFrame with hospital counts
        title: Map title
    
    Returns:
        matplotlib figure
    """
    fig, ax = plt.subplots(1, 1, figsize=(15, 12))
    
    # Create choropleth
    districts_with_counts.plot(
        column='hospital_count',
        cmap='YlOrRd',
        linewidth=0.1,
        ax=ax,
        edgecolor='white',
        legend=True,
        legend_kwds={
            'label': "Number of Hospitals",
            'orientation': "vertical",
            'shrink': 0.6
        }
    )
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Longitude', fontsize=12)
    ax.set_ylabel('Latitude', fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # Remove axis ticks for cleaner look
    ax.set_xticks([])
    ax.set_yticks([])
    
    plt.tight_layout()
    return fig

def perform_proximity_analysis(hospitals_gdf, pop_centers_gdf, department, buffer_km=10):
    """
    Perform proximity analysis for a specific department.
    
    Args:
        hospitals_gdf: GeoDataFrame of hospitals
        pop_centers_gdf: GeoDataFrame of population centers
        department: Department name to analyze
        buffer_km: Buffer radius in kilometers
    
    Returns:
        tuple: (most_isolated_center, most_concentrated_center, dept_hospitals)
    """
    print(f"\n🔄 Analyzing proximity for {department}...")
    
    # Filter data for the department
    dept_hospitals = hospitals_gdf[hospitals_gdf['Departamento'] == department.upper()].copy()
    dept_pop_centers = pop_centers_gdf[pop_centers_gdf['CCDD'] == get_department_code(department)].copy()
    
    if len(dept_hospitals) == 0:
        print(f"❌ No hospitals found for {department}")
        return None, None, None
    
    if len(dept_pop_centers) == 0:
        print(f"❌ No population centers found for {department}")
        return None, None, None
    
    print(f"✓ Department hospitals: {len(dept_hospitals):,}")
    print(f"✓ Department population centers: {len(dept_pop_centers):,}")
    
    # Convert buffer to degrees (approximate)
    buffer_degrees = buffer_km / 111.0  # 1 degree ≈ 111 km
    
    # Calculate hospital proximity for each population center
    proximity_results = []
    
    for idx, center in dept_pop_centers.iterrows():
        # Create buffer around population center
        center_buffer = center.geometry.buffer(buffer_degrees)
        
        # Count hospitals within buffer
        hospitals_in_buffer = dept_hospitals[dept_hospitals.geometry.within(center_buffer)]
        hospital_count = len(hospitals_in_buffer)
        
        proximity_results.append({
            'center_id': idx,
            'geometry': center.geometry,
            'hospitals_10km': hospital_count,
            'nome': center.get('NOME', 'Unknown'),
            'ccpp': center.get('CCPP', 'Unknown')
        })
    
    proximity_df = pd.DataFrame(proximity_results)
    proximity_gdf = gpd.GeoDataFrame(proximity_df, geometry='geometry', crs='EPSG:4326')
    
    # Find most isolated (fewest hospitals)
    most_isolated = proximity_gdf.loc[proximity_gdf['hospitals_10km'].idxmin()]
    
    # Find most concentrated (most hospitals)
    most_concentrated = proximity_gdf.loc[proximity_gdf['hospitals_10km'].idxmax()]
    
    print(f"✓ Most isolated center: {most_isolated['hospitals_10km']} hospitals in 10km")
    print(f"✓ Most concentrated center: {most_concentrated['hospitals_10km']} hospitals in 10km")
    
    return most_isolated, most_concentrated, dept_hospitals

def get_department_code(department_name):
    """Map department names to their codes"""
    dept_codes = {
        'lima': '15',
        'loreto': '16',
        'cusco': '08',
        'arequipa': '04',
        'piura': '20',
        'la libertad': '13',
        'cajamarca': '06',
        'puno': '21',
        'junin': '12',
        'ancash': '02'
    }
    return dept_codes.get(department_name.lower(), '15')  # Default to Lima

def create_proximity_folium_map(hospitals, isolated_center, concentrated_center, 
                              department, center_coords, zoom=8):
    """
    Create a professional Folium map for proximity analysis.
    
    Args:
        hospitals: GeoDataFrame of hospitals in the department
        isolated_center: Most isolated population center
        concentrated_center: Most concentrated population center
        department: Department name
        center_coords: [lat, lon] for map center
        zoom: Initial zoom level
    
    Returns:
        folium.Map object
    """
    # Create base map
    m = folium.Map(
        location=center_coords,
        zoom_start=zoom,
        tiles='OpenStreetMap'
    )
    
    # Add isolated center (red)
    if isolated_center is not None:
        folium.Marker(
            location=[isolated_center.geometry.y, isolated_center.geometry.x],
            popup=folium.Popup(
                f"<b>Most Isolated Center</b><br>"
                f"Name: {isolated_center.get('nome', 'Unknown')}<br>"
                f"Hospitals within 10km: {isolated_center['hospitals_10km']}<br>"
                f"Coordinates: ({isolated_center.geometry.y:.4f}, {isolated_center.geometry.x:.4f})",
                max_width=300
            ),
            icon=folium.Icon(color='red', icon='exclamation-sign')
        ).add_to(m)
        
        # Add 10km buffer
        folium.Circle(
            location=[isolated_center.geometry.y, isolated_center.geometry.x],
            radius=10000,  # 10 km in meters
            color='red',
            fillColor='red',
            fillOpacity=0.1,
            weight=2,
            popup=f"10km buffer - {isolated_center['hospitals_10km']} hospitals"
        ).add_to(m)
    
    # Add concentrated center (green)
    if concentrated_center is not None:
        folium.Marker(
            location=[concentrated_center.geometry.y, concentrated_center.geometry.x],
            popup=folium.Popup(
                f"<b>Most Concentrated Center</b><br>"
                f"Name: {concentrated_center.get('nome', 'Unknown')}<br>"
                f"Hospitals within 10km: {concentrated_center['hospitals_10km']}<br>"
                f"Coordinates: ({concentrated_center.geometry.y:.4f}, {concentrated_center.geometry.x:.4f})",
                max_width=300
            ),
            icon=folium.Icon(color='green', icon='plus-sign')
        ).add_to(m)
        
        # Add 10km buffer
        folium.Circle(
            location=[concentrated_center.geometry.y, concentrated_center.geometry.x],
            radius=10000,  # 10 km in meters
            color='green',
            fillColor='green',
            fillOpacity=0.1,
            weight=2,
            popup=f"10km buffer - {concentrated_center['hospitals_10km']} hospitals"
        ).add_to(m)
    
    # Add all hospitals in the department
    if hospitals is not None and len(hospitals) > 0:
        for idx, hospital in hospitals.iterrows():
            if pd.notna(hospital.geometry.y) and pd.notna(hospital.geometry.x):
                folium.CircleMarker(
                    location=[hospital.geometry.y, hospital.geometry.x],
                    radius=4,
                    popup=folium.Popup(
                        f"<b>{hospital['Nombre del establecimiento']}</b><br>"
                        f"Type: {hospital.get('Tipo', 'N/A')}<br>"
                        f"Institution: {hospital.get('Institución', 'N/A')}",
                        max_width=300
                    ),
                    color='blue',
                    fillColor='lightblue',
                    fillOpacity=0.7,
                    weight=1
                ).add_to(m)
    
    # Add legend
    legend_html = f'''
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 220px; height: 140px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <b>{department} Proximity Analysis</b><br>
    <i class="fa fa-exclamation-sign" style="color:red"></i> Most Isolated Center<br>
    <i class="fa fa-plus-sign" style="color:green"></i> Most Concentrated Center<br>
    <i class="fa fa-circle" style="color:blue"></i> Hospitals<br>
    <span style="color:red">●</span>/<span style="color:green">●</span> 10km buffers
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m

def create_national_choropleth_folium(districts_with_counts, hospitals_gdf):
    """
    Create a national Folium choropleth map with hospital markers.
    
    Args:
        districts_with_counts: GeoDataFrame with hospital counts
        hospitals_gdf: GeoDataFrame of hospitals
    
    Returns:
        folium.Map object
    """
    # Create base map centered on Peru
    peru_center = [-9.19, -75.0152]
    m = folium.Map(location=peru_center, zoom_start=6)
    
    # Add choropleth layer
    folium.Choropleth(
        geo_data=districts_with_counts,
        data=districts_with_counts,
        columns=['IDDIST_clean', 'hospital_count'],
        key_on='feature.properties.IDDIST_clean',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Number of Hospitals per District'
    ).add_to(m)
    
    # Add hospital markers with clustering
    if hospitals_gdf is not None and len(hospitals_gdf) > 0:
        marker_cluster = plugins.MarkerCluster().add_to(m)
        
        for idx, hospital in hospitals_gdf.iterrows():
            if pd.notna(hospital.geometry.y) and pd.notna(hospital.geometry.x):
                folium.Marker(
                    location=[hospital.geometry.y, hospital.geometry.x],
                    popup=folium.Popup(
                        f"<b>{hospital['Nombre del establecimiento']}</b><br>"
                        f"Department: {hospital['Departamento']}<br>"
                        f"Institution: {hospital['Institución']}<br>"
                        f"Type: {hospital.get('Tipo', 'N/A')}",
                        max_width=300
                    ),
                    icon=folium.Icon(color='red', icon='plus-sign')
                ).add_to(marker_cluster)
    
    return m

def create_summary_statistics(hospitals_df, districts_with_counts):
    """
    Create comprehensive summary statistics.
    
    Args:
        hospitals_df: DataFrame of hospitals
        districts_with_counts: GeoDataFrame with hospital counts
    
    Returns:
        dict: Summary statistics
    """
    stats = {
        'total_hospitals': len(hospitals_df),
        'total_districts': len(districts_with_counts),
        'districts_with_hospitals': len(districts_with_counts[districts_with_counts['hospital_count'] > 0]),
        'districts_without_hospitals': len(districts_with_counts[districts_with_counts['hospital_count'] == 0]),
        'avg_hospitals_per_district': districts_with_counts['hospital_count'].mean(),
        'max_hospitals_district': districts_with_counts['hospital_count'].max(),
        'departments_covered': hospitals_df['Departamento'].nunique(),
        'top_departments': hospitals_df['Departamento'].value_counts().head(5).to_dict(),
        'institutions': hospitals_df['Institución'].value_counts().to_dict()
    }
    
    return stats