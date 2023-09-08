# Run `pytest` in the terminal.

import time
import numpy as np
import r3f
import inu
import matplotlib.pyplot as plt


def gen_path(T, axis=1):
    # Define time.
    K = round(360.0/T) + 1
    t = np.arange(K)*T

    # Define a figure eight in the local, curvilinear frame.
    R = 1000.0
    theta = np.linspace(0, 2*np.pi, K)
    xc = (R/4)*np.sin(2*theta)
    yc = R*(np.cos(theta) - 1)
    zc = 50.0*(np.cos(theta) - 1)

    # Convert to geodetic coordinates.
    lat, lon, hae = r3f.curvilinear_to_geodetic(xc, yc, zc,
        0.6939, 1.4694, 226.0)
    llh_t = np.row_stack((lat, lon, hae))

    if axis == 0:
        llh_t = llh_t.T

    return t, llh_t


def test_mech():
    # ------------------------------------
    # Test with time varying alone axis 1.
    # ------------------------------------

    # Build path.
    T = 0.01
    t, llh = gen_path(T)
    vne = inu.llh_to_vne(llh, T)
    grav = inu.somigliana(llh)
    rpy = inu.vne_to_rpy(vne, grav[2, :], T)

    # Inverse and forward mechanize.
    hfbbi, hwbbi = inu.inv_mech(llh, vne, rpy, T)
    tllh, tvne, trpy = inu.mech(hfbbi, hwbbi,
        llh[:, 0], vne[:, 0], rpy[:, 0], T)

    assert np.allclose(llh, tllh)
    assert np.allclose(vne, tvne)
    assert np.allclose(rpy, trpy)

    # ------------------------------------
    # Test with time varying alone axis 0.
    # ------------------------------------

    # Build path.
    T = 0.01
    t, llh = gen_path(T, axis=0)
    vne = inu.llh_to_vne(llh, T)
    grav = inu.somigliana(llh)
    rpy = inu.vne_to_rpy(vne, grav[:, 2], T)

    # Inverse and forward mechanize.
    hfbbi, hwbbi = inu.inv_mech(llh, vne, rpy, T)
    tllh, tvne, trpy = inu.mech(hfbbi, hwbbi,
        llh[0, :], vne[0, :], rpy[0, :], T)

    assert np.allclose(llh, tllh)
    assert np.allclose(vne, tvne)
    assert np.allclose(rpy, trpy)
