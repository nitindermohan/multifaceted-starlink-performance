import numpy as np
from pymap3d.ecef import eci2geodetic
from datetime import datetime
from functools import partial
from scipy.spatial.transform import Rotation as R
import geopandas
import cartopy.crs as ccrs
from matplotlib import colors
import matplotlib.pyplot as plt

from orbit_utils import params

def get_orbitecis(incl, raan, altitude, n, begin_time=0, Earth_R=6371, portion=1.0, retrograde=False):
    """Generates a circular orbit based on given parameters
    
    Params:
        incl: Inclination in Degrees
        raan: Right Ascension to Ascending Node in Degrees
        altitude: Altitude in km
        n: amount of points needed for a full revolution
        begin_time: time in which to begin
        portion: ratio of the portion of points to be created
    
    Returns:
        A tuple
        (
            np array of r_eci points in km,
            np array of v_eci in km/s,
            delta seconds since beginning)
    """
    
    # Calculating r_eci
    if retrograde:
        sign = 1
    else:
        sign = -1
    points = []
    for i in range(int(n*portion)):
        points.append([np.sin(sign * 2*np.pi * (i/n)), np.cos(sign * 2*np.pi * (i/n)), 0])
    points = np.array(points) * (altitude + Earth_R)  # Plus height in km
    
    m_raan = R.from_rotvec(np.array([0, 0, 1]) * raan, degrees=True).as_matrix()  # Rotation along the north-pole axis
    m_incl = R.from_rotvec(np.array([1, 0, 0]) * incl, degrees=True).as_matrix()  # Rotation along the axis towards the ascending node
    
    raan_vec = np.matmul(m_raan, np.array([1, 0, 0]))
    incl_vec = np.matmul(m_incl, np.array([0, 1, 0]))
    incl_vec = np.matmul(m_raan, incl_vec)
    normal = np.cross(raan_vec, incl_vec)
    basechange_m = np.array([raan_vec, incl_vec, normal])
    
    r_ecis = np.matmul(basechange_m.T, points.T).T
    
    # Calculating Time periods
    mu = 398600.4418 # unit: (km)^3 / s^2
    period_s = ((2*np.pi) / np.sqrt(mu)) * np.sqrt(altitude + Earth_R)**3 # Period of one revolution
    delta_array = np.arange(0, period_s, period_s/n)
    time_array = [datetime.fromtimestamp(dt + begin_time) for dt in delta_array]
    
    # Calculating v_eci in km/s
    velocity = (2 * np.pi * (altitude + Earth_R)) / period_s
    v_ecis = []
    for r_eci in r_ecis:
        v_eci_ = np.cross(-r_eci, normal)
        v_eci_ = v_eci_ / np.linalg.norm(v_eci_)
        v_eci_ *= velocity
        v_ecis.append(v_eci_)
    v_ecis = np.array(v_ecis)
    
    return r_ecis, v_ecis, time_array

def get_bounding_points(r_eci, v_eci, time, min_elevation=15):
    """
    Given a eci point, we calculate the bounding points of its coverage based
    on min_elevation in degrees.
    
    r_eci: point in ECI coordinates
    v_eci: vector tangential forward, also can be seen as velocity
    min_elevation: minimum elevation, for coverage
    
    returns upperbounding point, lowerbounding point as lat long coordinates
    """
    altitude = np.linalg.norm(r_eci) - 6371
    _, _, beta, _ = params(min_elevation, altitude, R = 6371)
    rot_m = R.from_rotvec(v_eci * np.radians(beta) / np.linalg.norm(v_eci)).as_matrix()
    
    bounding_reci1 = np.matmul(rot_m, r_eci)
    bounding_reci2 = np.matmul(np.linalg.inv(rot_m), r_eci)
    
    lat1, long1, _ = eci2geodetic(*(bounding_reci1 * 1000), time)
    lat2, long2, _ = eci2geodetic(*(bounding_reci2 * 1000), time)
    return ((lat1, long1), (lat2, long2))

def get_coords(incl, raan, altitude, n, begin_time=0, portion=1.0):
    """Generates ground track of a  circular orbit based on given parameters
    
    Params:
        incl: Inclination in Degrees
        raan: Right Ascension to Ascending Node in Degrees
        altitude: Altitude in km
        n: amount of points to be generated
        begin_time: time in which to begin
    
    Returns:
        array of lat long tuples
    """
    ps, vs, ts = get_orbitecis(incl, raan, altitude, n, begin_time, portion=portion)
    
    coords = []
    bound_coords1 = []
    bound_coords2 = []
    for point, fwd, time in zip(ps, vs, ts):
        lat, long, altitude = eci2geodetic(*(point * 1000), time)
        coords.append((lat[0], long[0]))
        bc1, bc2 = get_bounding_points(point, fwd, time)
        bound_coords1.append(bc1)
        bound_coords2.append(bc2)
    return np.array(coords), np.array(bound_coords1), np.array(bound_coords2)

# partitioning a coordinate list based on continuities
def discontin_partition(coord_list):
    latitude, longitude = coord_list[:, 0], coord_list[:, 1]
    coords_list_ = [(latitude, longitude)]
    last_long = 0
    for i, long in enumerate(longitude):
        if (np.abs(long - last_long) > 200):
            coords_list_ = [(coord_list[:i, 0], coord_list[:i, 1])]
            coords_list_.append((coord_list[i:, 0], coord_list[i:, 1]))
            break
        else:
            last_long = long
    return coords_list_

# Plotting GS points
def plot_period_groundtrack(coord_list, ax, color, label=""):
    coords_list = discontin_partition(coord_list)
    for lats, longs in coords_list:
        ax.plot(longs, lats,
                   color=color,
                   zorder = 10,
                   linewidth = 0.7, label=label)
        label = ""

def construct_polygon(bound_coords1, bound_coords2):
    """Constructing polygon based on bounding coords.
    
    We are working with the following assumptions about the coordinates:
    - they are contiguously ordered
    - they do one revolution around the longitude coordinates
    
    This is a rather quick and dirty solution but it somewhat works, so year. The resulting polygon might have some weird
    zizags
    """
    def get_longitude(c):
        return c[1]
    bound_coords1 = sorted(bound_coords1, key=get_longitude)
    bound_coords2 = sorted(bound_coords2, key=get_longitude, reverse=True)
    polygon = np.array([*bound_coords1, *bound_coords2])
    return polygon

def plot_bounds(bound_coords1, bound_coords2, ax, color):
    bound_polygon = construct_polygon(bound_coords1, bound_coords2)
    ax.fill(bound_polygon[:, 1], bound_polygon[:, 0], facecolor=color)
