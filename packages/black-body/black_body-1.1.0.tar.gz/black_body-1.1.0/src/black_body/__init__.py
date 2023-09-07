"""
Set of formalisms around black bodies
"""
# {# pkglts, src
# FYEO
# #}
# {# pkglts, version, after src
from . import version

__version__ = version.__version__
# #}

from .constants import celsius, kelvin, rg_to_ppfd, par_to_ppfd, ppfd_to_rg, ppfd_to_par
from .energy import black_body
