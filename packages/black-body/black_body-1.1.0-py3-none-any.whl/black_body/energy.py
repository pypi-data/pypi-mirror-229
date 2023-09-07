"""
Different formalisms to express energy radiated by black bodies
"""
from math import exp

from .constants import c, h, k, stephan_boltzmann, wiens_displacement


def black_body(temp):
    """Amount of energy radiated by black body

    References: https://en.wikipedia.org/wiki/Black-body_radiation

    Args:
        temp (float): [K] temperature of black body

    Returns:
        (float): [W.m-2]
    """
    return stephan_boltzmann * temp ** 4


def modal_wavelength(temp):
    """Wavelength with maximum energy

    References: https://en.wikipedia.org/wiki/Black-body_radiation

    Args:
        temp (float): [K] temperature of black body

    Returns:
        (float): [m]
    """
    return wiens_displacement / temp


def spectrum(wavelength, t_body):
    """Energy of black body in specific wavelength

    References: https://en.wikipedia.org/wiki/Planck%27s_law#Black-body_radiation

    Args:
        wavelength (float): [m]
        t_body (float): [K] temperature of back body

    Returns:
        (float): [W.m-2.sr-1.m-1]
    """
    return 2 * h * c ** 2 / wavelength ** 5 / (exp(h * c / (wavelength * k * t_body)) - 1)
