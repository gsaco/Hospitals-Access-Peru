#!/usr/bin/env python3
"""
Hospital Access in Peru - Streamlit Application Launcher
Run this script from the project root to start the Streamlit app.
"""

import sys
import os
import subprocess

def main():
    # Get the directory containing this script (project root)
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Add src directory to Python path
    src_dir = os.path.join(project_root, 'src')
    sys.path.insert(0, src_dir)
    
    # Change to src directory and run streamlit
    os.chdir(src_dir)
    
    # Run streamlit app
    subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py'] + sys.argv[1:])

if __name__ == "__main__":
    main()