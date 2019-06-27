# flake8: noqa
from ._version import get_versions

from .clarite import ClariteDataframeAccessor

from .ewas import SurveyDesignSpec, ewas, add_corrected_pvalues
from .utilities import make_binary, make_categorical, make_continuous, merge_variables
from .io import load_data
from .plotting import plot_manhattan

__version__ = get_versions()['version']
del get_versions
