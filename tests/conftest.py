# Add project root to Python path so local package imports work
import os
import sys

test_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(test_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
