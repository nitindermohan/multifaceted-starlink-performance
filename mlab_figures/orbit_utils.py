import numpy as np
import math
import matplotlib.pyplot as plt
from functools import partial
from descartes import PolygonPatch

# We are often interested in the radius of the coverage area based on altitude and elevation.
# There are two ways to define radius: the radius of the slice depicted in the image above (A), or the geodesic distance (arc length) (B)

def slant_distance(e, h, R = 6371):
    """
    Computes the slant distance based on elevation and altitude.
    
    e: Elevation in degrees
    h: Altitude in km
    
    Returns
    
    d: slant distance in km
    """
    B = -2 * R * np.cos(np.radians(90 + e))
    C = -2 * R * h - h**2
    # Solving a geometric equation where only one is real
    d = (-B + np.sqrt(B**2 - 4*C)) / 2.0
    return d

def params(e, h, R = 6371):
    """
    With the equations above, we can solve all four parameters
    
    e: Elevation in degrees
    h: Altitude in km
    
    Returns
    
    all four parameters discussed above
    """
    r = R + h
    
    d = slant_distance(e, h, R=R)
    beta = np.degrees( np.arcsin( d * np.cos(np.radians(e))/r ) )
    alpha = 90 - e - beta
    
    return e, alpha, beta, d

def coverage_radius_A(e, h, R = 6371):
    """
    With the equations above, we can solve all four parameters
    
    e: Elevation in degrees
    h: Altitude in km
    
    Returns
    
    Radius A in km
    """
    _, _, beta, _ = params(e, h, R=R)
    radius = np.sin(np.radians(beta)) * R
    return radius

def coverage_radius_B(e, h, R = 6371):
    """
    With the equations above, we can solve all four parameters
    
    e: Elevation in degrees
    h: Altitude in km
    
    Returns
    
    Radius B in km
    """
    _, _, beta, _ = params(e, h, R=R)
    diameter = 2 * np.pi * R
    radius = (beta / 360) * diameter
    return radius
