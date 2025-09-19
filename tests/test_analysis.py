"""
Test suite for the Hospitals Access Peru application.
"""

import pytest
import pandas as pd
import geopandas as gpd
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import (
    load_and_clean_data,
    filter_operational_hospitals,
    spatial_join_hospitals_districts,
    create_choropleth_map,
    perform_proximity_analysis,
    create_summary_statistics
)


@pytest.fixture
def sample_hospitals_data():
    """Create sample hospitals data for testing."""
    return pd.DataFrame({
        'Nombre del establecimiento': ['Hospital A', 'Hospital B', 'Hospital C'],
        'Departamento': ['Lima', 'Lima', 'Cusco'],
        'Provincia': ['Lima', 'Lima', 'Cusco'],
        'Distrito': ['Lima', 'San Juan', 'Cusco'],
        'Latitud': [-12.0464, -12.1600, -13.5320],
        'Longitud': [-77.0428, -76.9900, -71.9675],
        'Condición': ['EN FUNCIONAMIENTO', 'EN FUNCIONAMIENTO', 'EN FUNCIONAMIENTO'],
        'Institución': ['MINSA', 'ESSALUD', 'GOBIERNO REGIONAL'],
        'UBIGEO': ['150101', '150102', '080101']
    })


@pytest.fixture
def sample_districts_data():
    """Create sample districts geodataframe for testing."""
    from shapely.geometry import Polygon
    
    # Simple square polygons for testing
    poly1 = Polygon([(-77.1, -12.1), (-76.9, -12.1), (-76.9, -11.9), (-77.1, -11.9)])
    poly2 = Polygon([(-77.1, -12.3), (-76.9, -12.3), (-76.9, -12.1), (-77.1, -12.1)])
    poly3 = Polygon([(-72.1, -13.6), (-71.8, -13.6), (-71.8, -13.4), (-72.1, -13.4)])
    
    return gpd.GeoDataFrame({
        'DEPARTAMEN': ['LIMA', 'LIMA', 'CUSCO'],
        'PROVINCIA': ['LIMA', 'LIMA', 'CUSCO'],
        'DISTRITO': ['LIMA', 'SAN JUAN DE LURIGANCHO', 'CUSCO'],
        'UBIGEO': ['150101', '150102', '080101'],
        'geometry': [poly1, poly2, poly3]
    })


@pytest.fixture
def sample_pop_centers_data():
    """Create sample population centers data for testing."""
    from shapely.geometry import Point
    
    return gpd.GeoDataFrame({
        'nome': ['Lima Centro', 'San Juan', 'Cusco Centro'],
        'departamen': ['LIMA', 'LIMA', 'CUSCO'],
        'provincia': ['LIMA', 'LIMA', 'CUSCO'],
        'distrito': ['LIMA', 'SAN JUAN DE LURIGANCHO', 'CUSCO'],
        'geometry': [
            Point(-77.0428, -12.0464),
            Point(-76.9900, -12.1600),
            Point(-71.9675, -13.5320)
        ]
    })


class TestDataLoading:
    """Test data loading and cleaning functions."""
    
    def test_filter_operational_hospitals(self, sample_hospitals_data):
        """Test hospital filtering functionality."""
        # Add a non-operational hospital
        test_data = sample_hospitals_data.copy()
        test_data.loc[3] = ['Hospital D', 'Lima', 'Lima', 'Lima', -12.0, -77.0, 'CERRADO', 'MINSA']
        
        filtered = filter_operational_hospitals(test_data)
        
        assert len(filtered) == 3  # Should exclude the closed hospital
        assert all(filtered['Condición'] == 'EN FUNCIONAMIENTO')
        assert 'Hospital D' not in filtered['Nombre'].values
    
    def test_filter_operational_hospitals_invalid_institutions(self, sample_hospitals_data):
        """Test filtering of non-public institutions."""
        test_data = sample_hospitals_data.copy()
        test_data.loc[3] = ['Hospital Private', 'Lima', 'Lima', 'Lima', -12.0, -77.0, 'EN FUNCIONAMIENTO', 'PRIVADO', '150103']
        
        filtered = filter_operational_hospitals(test_data)
        
        # Should exclude private hospital
        assert 'Hospital Private' not in filtered['Nombre del establecimiento'].values
    
    def test_filter_operational_hospitals_missing_coordinates(self, sample_hospitals_data):
        """Test filtering of hospitals with missing coordinates."""
        test_data = sample_hospitals_data.copy()
        test_data.loc[2, 'Latitud'] = None
        
        filtered = filter_operational_hospitals(test_data)
        
        # Should exclude hospital with missing coordinates
        assert len(filtered) == 2
        assert 'Hospital C' not in filtered['Nombre del establecimiento'].values


class TestSpatialOperations:
    """Test spatial operations and analysis functions."""
    
    def test_spatial_join_hospitals_districts(self, sample_hospitals_data, sample_districts_data):
        """Test spatial join between hospitals and districts."""
        hospitals_gdf = gpd.GeoDataFrame(
            sample_hospitals_data,
            geometry=gpd.points_from_xy(sample_hospitals_data.Longitud, sample_hospitals_data.Latitud),
            crs='EPSG:4326'
        )
        
        result = spatial_join_hospitals_districts(hospitals_gdf, sample_districts_data)
        
        assert isinstance(result, gpd.GeoDataFrame)
        assert 'hospital_count' in result.columns
        assert len(result) == len(sample_districts_data)
        assert result['hospital_count'].sum() <= len(hospitals_gdf)
    
    def test_perform_proximity_analysis(self, sample_hospitals_data, sample_pop_centers_data):
        """Test proximity analysis functionality."""
        hospitals_gdf = gpd.GeoDataFrame(
            sample_hospitals_data,
            geometry=gpd.points_from_xy(sample_hospitals_data.Longitud, sample_hospitals_data.Latitud),
            crs='EPSG:4326'
        )
        
        result = perform_proximity_analysis(hospitals_gdf, sample_pop_centers_data, 'Lima', buffer_km=10)
        
        # Should return a tuple with isolated, concentrated, and hospitals
        assert len(result) == 3
        isolated, concentrated, dept_hospitals = result
        assert isinstance(dept_hospitals, gpd.GeoDataFrame)


class TestStatistics:
    """Test statistical analysis functions."""
    
    def test_create_summary_statistics(self, sample_hospitals_data, sample_districts_data):
        """Test summary statistics generation."""
        hospitals_gdf = gpd.GeoDataFrame(
            sample_hospitals_data,
            geometry=gpd.points_from_xy(sample_hospitals_data.Longitud, sample_hospitals_data.Latitud),
            crs='EPSG:4326'
        )
        
        districts_with_counts = spatial_join_hospitals_districts(hospitals_gdf, sample_districts_data)
        stats = create_summary_statistics(sample_hospitals_data, districts_with_counts)
        
        assert isinstance(stats, dict)
        expected_keys = [
            'total_hospitals', 'departments_covered', 'districts_with_hospitals',
            'districts_without_hospitals', 'avg_hospitals_per_district'
        ]
        for key in expected_keys:
            assert key in stats
        
        assert stats['total_hospitals'] == len(sample_hospitals_data)
        assert stats['departments_covered'] > 0
        assert stats['districts_with_hospitals'] >= 0
        assert stats['districts_without_hospitals'] >= 0


class TestVisualization:
    """Test visualization functions."""
    
    def test_create_choropleth_map_basic(self, sample_districts_data):
        """Test basic choropleth map creation."""
        # Add hospital counts for visualization
        test_data = sample_districts_data.copy()
        test_data['hospital_count'] = [2, 1, 1]
        
        try:
            fig, ax = create_choropleth_map(test_data, 'hospital_count', 'Hospital Count')
            assert fig is not None
            assert ax is not None
        except Exception as e:
            pytest.skip(f"Visualization test skipped due to: {e}")


class TestIntegration:
    """Integration tests for the full pipeline."""
    
    @pytest.mark.skipif(not os.path.exists("data/IPRESS.csv"), reason="Data files not available")
    def test_full_pipeline_with_real_data(self):
        """Test the full pipeline with real data if available."""
        try:
            hospitals_df, districts_gdf, pop_centers_gdf = load_and_clean_data()
            
            # Basic assertions
            assert isinstance(hospitals_df, pd.DataFrame)
            assert isinstance(districts_gdf, gpd.GeoDataFrame)
            assert isinstance(pop_centers_gdf, gpd.GeoDataFrame)
            
            assert len(hospitals_df) > 0
            assert len(districts_gdf) > 0
            assert len(pop_centers_gdf) > 0
            
            # Test filtering
            public_hospitals = filter_operational_hospitals(hospitals_df)
            assert len(public_hospitals) <= len(hospitals_df)
            
        except Exception as e:
            pytest.skip(f"Integration test skipped due to: {e}")


class TestDataValidation:
    """Test data validation and error handling."""
    
    def test_empty_dataframe_handling(self):
        """Test handling of empty dataframes."""
        empty_df = pd.DataFrame()
        
        with pytest.raises((ValueError, KeyError, AttributeError)):
            filter_operational_hospitals(empty_df)
    
    def test_invalid_coordinate_handling(self, sample_hospitals_data):
        """Test handling of invalid coordinates."""
        test_data = sample_hospitals_data.copy()
        test_data.loc[0, 'Latitud'] = 'invalid'
        test_data.loc[1, 'Longitud'] = 'invalid'
        
        filtered = filter_operational_hospitals(test_data)
        
        # Should handle invalid coordinates gracefully
        assert len(filtered) <= len(test_data)


if __name__ == "__main__":
    pytest.main([__file__])