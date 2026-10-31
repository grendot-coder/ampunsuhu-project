import os
import sys

# Add root directory to sys.path so project.py can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project import app

