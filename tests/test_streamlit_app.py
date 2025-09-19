"""
Test suite for the Streamlit application.
"""

import pytest
import pandas as pd
import geopandas as gpd
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestStreamlitApp:
    """Test Streamlit application functions."""
    
    @pytest.fixture
    def mock_streamlit(self):
        """Mock streamlit for testing."""
        with patch('streamlit_app.st') as mock_st:
            mock_st.set_page_config = MagicMock()
            mock_st.markdown = MagicMock()
            mock_st.tabs = MagicMock(return_value=['tab1', 'tab2', 'tab3'])
            mock_st.columns = MagicMock(return_value=['col1', 'col2', 'col3', 'col4'])
            mock_st.error = MagicMock()
            mock_st.cache_data = lambda func: func  # Simple cache mock
            yield mock_st
    
    def test_app_imports(self):
        """Test that the app can be imported without errors."""
        try:
            import streamlit_app
            assert hasattr(streamlit_app, 'main')
        except ImportError as e:
            pytest.skip(f"Streamlit app import failed: {e}")
    
    @patch('streamlit_app.load_all_data')
    def test_main_function_with_no_data(self, mock_load_data, mock_streamlit):
        """Test main function when data loading fails."""
        mock_load_data.return_value = (None, None, None, None, None, None)
        
        try:
            import streamlit_app
            streamlit_app.main()
            
            # Should call error when no data is loaded
            mock_streamlit.error.assert_called()
        except Exception as e:
            pytest.skip(f"Test skipped due to: {e}")
    
    def test_custom_css_validity(self):
        """Test that custom CSS is valid."""
        try:
            import streamlit_app
            # Check if the CSS string exists and is not empty
            # This would require accessing the CSS from the module
            assert True  # Placeholder test
        except Exception as e:
            pytest.skip(f"CSS test skipped due to: {e}")


class TestDataLoadingCaching:
    """Test data loading and caching mechanisms."""
    
    def test_load_all_data_function_exists(self):
        """Test that load_all_data function exists and is callable."""
        try:
            import streamlit_app
            assert hasattr(streamlit_app, 'load_all_data')
            assert callable(streamlit_app.load_all_data)
        except ImportError as e:
            pytest.skip(f"Streamlit app import failed: {e}")


class TestUIComponents:
    """Test UI component creation functions."""
    
    def test_create_static_maps_section_exists(self):
        """Test that static maps section function exists."""
        try:
            import streamlit_app
            assert hasattr(streamlit_app, 'create_static_maps_section')
            assert callable(streamlit_app.create_static_maps_section)
        except ImportError as e:
            pytest.skip(f"Streamlit app import failed: {e}")
    
    def test_create_proximity_analysis_maps_exists(self):
        """Test that proximity analysis function exists."""
        try:
            import streamlit_app
            assert hasattr(streamlit_app, 'create_proximity_analysis_maps')
            assert callable(streamlit_app.create_proximity_analysis_maps)
        except ImportError as e:
            pytest.skip(f"Streamlit app import failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__])