from .analysis import *
from .clustering import *
from .data_io import *
from .image_processing import *
from .integrate import *
from .interpolate import *
from .linear_algebra import *
from .metrics import *
from .modeling import *
from .numerics import *
from .optimize import *
from .preprocessing import *
from .statistics import *
from .test import *
from .text_analysis import *
from .validation import *
from .visualization import *
from .install_utilities import install_polyglot_func as install_polyglot


def check_dependencies():
    dependencies = [
        'Flask',
        'matplotlib',
        'networkx',
        'nltk',
        'numpy',
        'pandas',
        'Pillow',
        'scikit-learn',
        'scikit-image',
        'scipy',
        'seaborn',
        'statsmodels',
        'tensorflow',
        'GitPython'
    ]

    failed_dependencies = []
    
    for item in dependencies:
        try:
            __import__(item)
        except ImportError:
            failed_dependencies.append(item)

    if failed_dependencies:
        raise ImportError(f"Missing dependencies: {', '.join(failed_dependencies)}. Please install them.")

# Call this function upon import
check_dependencies()
