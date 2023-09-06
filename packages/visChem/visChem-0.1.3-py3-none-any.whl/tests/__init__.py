import warnings
from numba import NumbaDeprecationWarning
warnings.filterwarnings('ignore', category=NumbaDeprecationWarning, module='umap')
