"""
Set of physical constants useful to compute black bodies related formalisms

.. include:: ../../doc/biblio/biblio.rst
"""

_hnu_550 = 0.2175028466158127
"""[J.µmol photon-1] Energy in mol of photon @ 550 [nm]

References: https://sun-r.gitlab.io/paper/energy_balance/pyranometer.html#conversion-to-par
"""

_par_frac = 0.45
"""[-] Fraction of PAR in global solar radiation

Theoretical fraction considering PAR in [350:720] [nm]

References: https://sun-r.gitlab.io/paper/energy_balance/pyranometer.html#conversion-to-par
"""

sun_temp = 5772
"""[K] Temperature of sun's photosphere

References: https://en.wikipedia.org/wiki/Sun
"""

sun_radius = 696342e3
"""[m] Sun radius

References: https://en.wikipedia.org/wiki/Sun
"""

sun_earth_distance = 149598023e3
"""[m] Distance between Earth and Sun (Semi-major axis)

References: https://en.wikipedia.org/wiki/Earth
"""

solar_cst = 1353.
"""[W.m-2] mean amount of solar radiations received by earth above the atmosphere

References: https://www.pveducation.org/pvcdrom/properties-of-sunlight/solar-radiation-outside-the-earths-atmosphere
"""

h = 6.62607015e-34
"""[J.Hz-1] Planck's constant

References: scipy.constant
"""

k = 1.380649e-23
"""[J.K-1] Botzmann constant

References: scipy.constant
"""

c = 299792458
"""[m.s-1] speed of light

References: scipy.constant
"""

stephan_boltzmann = 5.670367e-08
"""[W.m-2.K-4] Stefan-Boltzmann constant per surface area (σ).

References: scipy.constants.physical_constants['Stefan-Boltzmann constant']
"""

wiens_displacement = 2.897771955e-3
"""[m.K] Wien's displacement constant

References: https://en.wikipedia.org/wiki/Black-body_radiation
"""

_kelvin = 273.15
"""[°C] temperature of 0°C in K

References: https://en.wikipedia.org/wiki/Kelvin
"""


def kelvin(temp):
    """Conversion to Kelvin

    Args:
        temp (float): [°C]

    Returns:
        (float): [K]
    """
    return temp + _kelvin


def celsius(temp):
    """Conversion to Celsius

    Args:
        temp (float): [K]

    Returns:
        (float): [°C]
    """
    return temp - _kelvin


def rg_to_ppfd(rg):
    """Convert solar global radiation to PAR

    References
        - `reis2020`_ (see formula 34)
        - corrected: https://sun-r.gitlab.io/paper/energy_balance/pyranometer.html#conversion-to-par

    Args:
        rg (float): [W.m-2] global radiation intensity

    Returns:
        (float): [µmol photon.m-2.s-1] PPFD
    """
    return rg * _par_frac / _hnu_550


def ppfd_to_rg(ppfd):
    """Convert PAR to solar global radiation

    References
        - `reis2020`_ (see formula 38)
        - corrected: https://sun-r.gitlab.io/paper/energy_balance/pyranometer.html#conversion-to-par

    Args:
        ppfd (float): [µmol photon.m-2.s-1] PPFD

    Returns:
        (float): [W.m-2] global radiation intensity
    """
    return ppfd * _hnu_550 / _par_frac


def par_to_ppfd(par):
    """Convert PAR to PPFD

    References
        - `reis2020`_ (see page 233)
        - corrected: https://sun-r.gitlab.io/paper/energy_balance/pyranometer.html#conversion-to-par

    Args:
        par (float): [W.m-2] PAR (photosynthetically active radiation)

    Returns:
        (float): [µmol photon.m-2.s-1] PPFD
    """
    return par / _hnu_550


def ppfd_to_par(ppfd):
    """Convert PPFD to PAR

    References
        - `reis2020`_ (see page 233)
        - corrected: https://sun-r.gitlab.io/paper/energy_balance/pyranometer.html#conversion-to-par

    Args:
        ppfd (float): [µmol photon.m-2.s-1] PPFD

    Returns:
        (float): [W.m-2] PAR (photosynthetically active radiation)
    """
    return ppfd * _hnu_550
