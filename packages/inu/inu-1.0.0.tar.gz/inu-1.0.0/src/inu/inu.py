"""
Copyright 2022 David Woodburn

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
--------------------------------------------------------------------------------

Functions
---------
This library provides forward mechanization of inertial measurement unit sensor
values (accelerometer and gyroscope readings) to get position, velocity, and
attitude as well as inverse mechanization to get sensor values from position,
velocity, and attitude. It also includes tools to calculate velocity from
geodetic position over time, to estimate attitude from velocity, and to estimate
wind velocity from ground-track velocity and yaw angle.

Accuracy
--------
The mechanization algorithms in this library make no simplifying assumptions.
The Earth is defined as an ellipsoid. Any deviations of the truth from this
simple shape can be captured by more complex gravity models. The algorithms use
a single frequency update structure which is much simpler than the common
two-frequency update structure and just as, if not more, accurate.

Duality
-------
The forward and inverse mechanization functions are perfect duals of each other.
This means that if you started with a profile of position, velocity, and
attitude and passed these into the inverse mechanization algorithm to get sensor
values and then passed those sensor values into the forward mechanization
algorithm, you would get back the original position, velocity, and attitude
profiles. The only error will be due to finite-precision rounding.
"""

__author__ = "David Woodburn"
__license__ = "MIT"
__date__ = "2023-09-06"
__maintainer__ = "David Woodburn"
__email__ = "david.woodburn@icloud.com"
__status__ = "Development"

import numpy as np
import r3f

# -----------------
# Support Functions
# -----------------

def progress(k, K):
    """
    Output a simple progress bar with percent complete to the terminal. When `k`
    equals `K - 1`, the progress bar will complete and start a new line.

    Parameters
    ----------
    k : int
        Index which should grow monotonically from 0 to K - 1.
    K : int
        Final index value of `k` plus 1.
    """

    M = 60 - 2 # length of progress bar, without percentage
    if k + 1 == K:
        print("\r[" + "="*M + "] 100%", flush=True)
    elif k % int(K/M) == 0:
        bar_len = int(M*(k + 1)/K)
        print("\r[" + "="*bar_len + " "*(M - bar_len) +
            "] %3d%%" % (int(100*(k + 1)/K)), end="", flush=True)


def sma(x, N):
    N_pre = int(np.ceil(N/2))
    N_post = int(np.floor(N/2))
    x_pre = x[0]*np.ones(N_pre)
    x_post = x[-1]*np.ones(N_post)
    x_ext = np.concatenate((x_pre, x, x_post))
    X = np.cumsum(x_ext)
    y = (X[N:] - X[:-N])/N
    return y


def lpf(x, fp, T):
    """
    Discrete, first-order, low-pass, infinite impulse response (IIR) filter,
    using the bilinear transform, applied twice, once forwards and then once
    backwards, effectively making it a second-order filter with no phase shift.
    This function uses frequency pre-warping.

    Parameters
    ----------
    x : (K,) np.ndarray
        Input to the filter as a time-history profile of K samples.
    fp : float
        Positive pole frequency in hertz.
    T : float
        Sampling period in seconds.

    Returns
    -------
    y : (K,) np.ndarray
        Output from the filter as a time-history profile of K samples.
    """

    # Define coefficients.
    Tpi = np.pi*T
    fp = np.tan(Tpi*fp)/Tpi # pre-warped pole frequency
    k = 1.0/(Tpi*fp + 1)
    N1 = Tpi*fp*k
    N0 = Tpi*fp*k
    D0 = Tpi*fp*k - k
    EOld = 0.0

    # Forward filter the whole array.
    K = len(x)
    y = np.zeros(K)
    for k in range(K):
        E = x[k] - D0*EOld
        y[k] = N1*E + N0*EOld
        EOld = E

    # Backward filter the whole array.
    for k in range(K-1, -1, -1):
        E = y[k] - D0*EOld
        y[k] = N1*E + N0*EOld
        EOld = E

    return y


def somigliana(lat, lon, hae):
    """
    Calculate the scalar component of local acceleration of gravity using the
    Somigliana equation.

    Parameters
    ----------
    lat : float or (K,) np.ndarray
        Geodetic latitude in radians.
    lon : float or (K,) np.ndarray
        Longitude in radians. This parameter is unused.
    hae : float or (K,) np.ndarray
        Height above ellipsoid in meters.

    Returns
    -------
    gamma : float or (K,) np.ndarray
        Acceleration of gravity in meters per second squared.
    """

    # gravity coefficients
    A_E = 6378137.0             # Earth's semi-major axis [m] (p. 109)
    E2 = 6.694379990141317e-3   # Earth's eccentricity squared [ND] (derived)
    ge = 9.7803253359           # Somigliana coefficient ge [m/s^2]
    k = 1.93185265241e-3        # Somigliana coefficient k [ND]
    f = 3.35281066475e-3        # Somigliana coefficient f [ND]
    m = 3.44978650684e-3        # Somigliana coefficient m [ND]

    # Get local acceleration of gravity for height equal to zero.
    slat = np.sin(lat)
    klat = np.sqrt(1 - E2*slat**2)
    g0 = ge*(1 + k*slat**2)/klat

    # Calculate gamma for the given height.
    gh = g0*(1 + (3/A_E**2)*hae**2 - 2/A_E*(1 + f + m - 2*f*slat**2)*hae)

    return gh


def vne_to_rpy(vne_t, grav_t, T, alpha=0.0, wind=None, axis=1):
    """
    Estimate the attitude angles in radians based on velocity.

    Parameters
    ----------
    vne_t : (3, K) or (K, 3) np.ndarray
        Matrix of vectors of velocity of the navigation frame relative to the
        ECEF frame (meters per second).
    grav_t : float or (K,) np.ndarray
        Local acceleration of gravity magnitude in meters per second squared.
    T : float
        Sampling period in seconds.
    alpha : float, default 0.0
        Angle of attack in radians.
    wind : (2,) or (2, K) np.ndarray, default None
        Horizontal velocity vector of wind in meters per second.
    axis : int, default 1
        The axis along which time varies.

    Returns
    -------
    rpy_t : (3, K) or (K, 3) np.ndarray
        Matrix of vectors of attitude angles roll, pitch, and yaw, all in
        radians. These angles are applied in the context of a North, East, Down
        navigation frame to produce the body frame in a zyx sequence of passive
        rotations.
    """

    # Check the inputs.
    if axis not in (0, 1):
        raise ValueError('axis must be 0 or 1')

    # Transpose.
    if axis == 0:
        vne_t = vne_t.T

    # Filter the velocity.
    vN = lpf(vne_t[0, :], fp=0.1, T=T)
    vE = lpf(vne_t[1, :], fp=0.1, T=T)
    vD = lpf(vne_t[2, :], fp=0.1, T=T)

    # Get the horizontal velocity.
    vH = np.sqrt(vN**2 + vE**2)

    # Estimate the yaw.
    if wind is None:
        yaw = np.arctan2(vE, vN)*(vH > 1e-6)
    else:
        yaw = np.arctan2(vE - wind[1], vN - wind[0])*(vH > 1e-6)

    # Estimate the pitch.
    pit = np.arctan(-vD/vH)*(vH > 1e-6) + alpha

    # Estimate the roll.
    aN = np.gradient(vN)/T # x-axis acceleration
    aE = np.gradient(vE)/T # y-axis acceleration
    #aN = ctrl.corrode(aN, 100)
    #aE = ctrl.corrode(aE, 100)
    ac = (vN*aE - vE*aN)/(vH + 1e-4) # cross product vH with axy
    rol = np.arctan(ac/grav_t)*(vH > 1e-6)

    # Assemble.
    if axis == 0:
        rpy_t = np.column_stack((rol, pit, yaw))
    else:
        rpy_t = np.row_stack((rol, pit, yaw))

    return rpy_t


def est_wind(vN_t, vE_t, yaw_t):
    """
    Estimate the time-varying wind by comparing the ground travel velocity to
    the yaw (heading) angle.

    Parameters
    ----------
    vN_t : (K,) np.ndarray
        North velocity of the navigation frame relative to the ECEF frame
        (meters per second).
    vE_t : (K,) np.ndarray
        East velocity of the navigation frame relative to the ECEF frame
        (meters per second).
    yaw_t : (K,) np.ndarray
        Yaw angle clockwise from north in radians.

    Returns
    -------
    wN_t : (K,) np.ndarray
        North component of wind vector in meters per second.
    wE_t : (K,) np.ndarray
        East component of wind vector in meters per second.
    """

    # Get the horizontal speed.
    sH_t = np.sqrt(vN_t**2 + vE_t**2)

    # Get the estimated wind.
    wN_t = vN_t - sH_t*np.cos(yaw_t)
    wE_t = vE_t - sH_t*np.sin(yaw_t)

    return wN_t, wE_t

# -------------
# Mechanization
# -------------

def llh_to_vne(lat, lon, hae, T, axis=1):
    """
    Convert geodetic position over time to velocity of the navigation frame
    relative to the earth frame over time. Geodetic position is quadratically
    extrapolated by one sample.

    Parameters
    ----------
    lat : (K,) np.ndarray
        Array of latitudes in radians.
    lon : (K,) np.ndarray
        Array of longitudes in radians.
    hae : (K,) np.ndarray
        Array of heights above ellipsoid in meters.
    T : float
        Sampling period in seconds.
    axis : int, default 1
        The axis along which time varies.

    Returns
    -------
    vne : (3, K) or (K, 3) np.ndarray
        Matrix of velocity vectors.
    """

    # Check the inputs.
    if axis not in (0, 1):
        raise ValueError('axis must be 0 or 1')

    # Extended derivatives
    lat_ext = 3*lat[-1] - 3*lat[-2] + lat[-3]
    lon_ext = 3*lon[-1] - 3*lon[-2] + lon[-3]
    hae_ext = 3*hae[-1] - 3*hae[-2] + hae[-3]
    Dlat = np.diff(np.append(lat, lat_ext))/T
    Dlon = np.diff(np.append(lon, lon_ext))/T
    Dhae = np.diff(np.append(hae, hae_ext))/T

    # Rotation rate of navigation frame relative to earth frame,
    # referenced in the navigation frame
    wnne_x = np.cos(lat)*Dlon
    wnne_y = -Dlat

    # Velocity of the navigation frame relative to the earth frame,
    # referenced in the navigation frame
    klat = np.sqrt(1 - r3f.E2*np.sin(lat)**2)
    Rm = (r3f.A_E/klat**3)*(1 - r3f.E2)
    Rt = r3f.A_E/klat
    vN = -wnne_y*(Rm + hae)
    vE =  wnne_x*(Rt + hae)
    vD = -Dhae
    if axis == 0:
        vne = np.column_stack((vN, vE, vD))
    else:
        vne = np.row_stack((vN, vE, vD))

    return vne


def inv_mech(llh_t, vne_t, rpy_t, T, axis=1, grav_model=somigliana,
        show_progress=True):
    """
    Compute the inverse mechanization of pose to get inertial measurement unit
    sensor values.

    Parameters
    ----------
    llh_t : (3, K) or (K, 3) np.ndarray
        Matrix of geodetic positions in terms of latitude (radians), longitude
        (radians), and height above ellipsoid (meters).
    vne_t : (3, K) or (K, 3) np.ndarray
        Matrix of vectors of velocity of the navigation frame relative to the
        ECEF frame (meters per second).
    rpy_t : (3, K) or (K, 3) np.ndarray
        Matrix of vectors of attitude angles roll, pitch, and yaw, all in
        radians. These angles are applied in the context of a North, East, Down
        navigation frame to produce the body frame in a zyx sequence of passive
        rotations.
    T : float
        Sampling period in seconds.
    axis : int, default 1
        The axis along which time varies.
    show_progress : bool, default True
        Flag to show the progress bar.

    Returns
    -------
    fbbi_t : (3, K) or (K, 3) np.ndarray
        Matrix of specific force vectors (meters per second squared) of the body
        frame relative to the inertial frame, referenced in the body frame.
    wbbi_t : (3, K) or (K, 3) np.ndarray
        Matrix of rotation rate vectors (radians per second) of the body frame
        relative to the inertial frame, referenced in the body frame.
    """

    # Check the inputs.
    if axis not in (0, 1):
        raise ValueError('axis must be 0 or 1')
    if not isinstance(show_progress, bool):
        raise TypeError('show_progress must be a boolean.')

    # Transpose.
    if axis == 0:
        llh_t = llh_t.T
        vne_t = ven_t.T
        rpy_t = rpy_t.T

    # Extrapolate inputs by one sample.
    llh_ext = 3*llh_t[:, -1] - 3*llh_t[:, -2] + llh_t[:, -3]
    vne_ext = 3*vne_t[:, -1] - 3*vne_t[:, -2] + vne_t[:, -3]
    rpy_ext = 3*rpy_t[:, -1] - 3*rpy_t[:, -2] + rpy_t[:, -3]
    llh_t = np.column_stack((llh_t, llh_ext))
    vne_t = np.column_stack((vne_t, vne_ext))
    rpy_t = np.column_stack((rpy_t, rpy_ext))

    # storage
    K = llh_t.shape[1]
    fbbi_t = np.zeros((3, K - 1))
    wbbi_t = np.zeros((3, K - 1))

    # time loop
    for k in range(K - 1):
        # inputs
        llh = llh_t[:, k]
        llh_p = llh_t[:, k + 1]
        vne = vne_t[:, k]
        vne_p = vne_t[:, k + 1]
        rpy = rpy_t[:, k]
        rpy_p = rpy_t[:, k + 1]

        # position and velocity
        Dllh = (llh_p - llh)/T
        Dvne = (vne_p - vne)/T

        # rotation matrix
        Cnb = r3f.rpy_to_dcm(rpy[0], rpy[1], rpy[2]).T
        Cnb_p = r3f.rpy_to_dcm(rpy_p[0], rpy_p[1], rpy_p[2]).T
        wbbn = r3f.inverse_rodrigues_rotation(Cnb.T @ Cnb_p)/T

        # rotation rates
        wnne = np.array([
            np.cos(llh[0])*Dllh[1],
            -Dllh[0],
            -np.sin(llh[0])*Dllh[1]])
        wnei = np.array([
            r3f.W_EI*np.cos(llh[0]),
            0.0,
            -r3f.W_EI*np.sin(llh[0])])
        wbbi = wbbn + Cnb.T @ (wnne + wnei)

        # specific force
        grav = np.array([0, 0, grav_model(*llh)])
        fbbi = Cnb.T @ (Dvne + np.cross(2*wnei + wnne, vne) - grav)

        # results storage
        fbbi_t[:, k] = fbbi
        wbbi_t[:, k] = wbbi

        # progress bar
        if show_progress:
            progress(k, K - 1)

    # Transpose back.
    if axis == 0:
        fbbi_t = fbbi_t.T
        wbbi_t = wbbi_t.T

    return fbbi_t, wbbi_t


def mech(fbbi_t, wbbi_t, llh0, vne0, rpy0, T, axis=1, grav_model=somigliana,
        show_progress=True):
    """
    Compute the forward mechanization of inertial measurement unit sensor values
    to get pose.

    Parameters
    ----------
    fbbi_t : (3, K) or (K, 3) np.ndarray
        Matrix of specific force vectors (meters per second squared) of the body
        frame relative to the inertial frame, referenced in the body frame.
    wbbi_t : (3, K) or (K, 3) np.ndarray
        Matrix of rotation rate vectors (radians per second) of the body frame
        relative to the inertial frame, referenced in the body frame.
    llh0 : (3,) np.ndarray
        Initial geodetic position of latitude (radians), longitude (radians),
        and height above ellipsoid (meters).
    vne0 : (3,) np.ndarray
        Initial velocity vector (meters per second) in North, East, and Down
        (NED) directions.
    rpy0 : (3,) np.ndarray
        Initial roll, pitch, and yaw angles in radians. These angles are applied
        in the context of a North, East, Down (NED) navigation frame to produce
        the body frame in a zyx sequence of passive rotations.
    T : float
        Sampling period in seconds.
    axis : int, default 1
        The axis along which time varies.
    grav_model : function, default somigliana
        The gravity model function to use. This should take latitude (radians),
        longitude (radians), and height above ellipsoid (meters) and return
        local acceleration of gravity (meters per second squared).
    show_progress : bool, default True
        Flag to show the progress bar.

    Returns
    -------
    llh_t : (3, K) or (K, 3) np.ndarray
        Matrix of geodetic positions in terms of latitude (radians), longitude
        (radians), and height above ellipsoid (meters).
    vne_t : (3, K) or (K, 3) np.ndarray
        Matrix of vectors of velocity of the navigation frame relative to the
        ECEF frame (meters per second).
    rpy_t : (3, K) or (K, 3) np.ndarray
        Matrix of vectors of attitude angles roll, pitch, and yaw, all in
        radians. These angles are applied in the context of a North, East, Down
        navigation frame to produce the body frame in a zyx sequence of passive
        rotations.
    """

    # Check the inputs.
    if axis not in (0, 1):
        raise ValueError('axis must be 0 or 1')
    if not isinstance(show_progress, bool):
        raise TypeError('show_progress must be a boolean.')

    # Initialize states.
    llh = llh0.copy()
    vne = vne0.copy()
    rpy = rpy0.copy()

    # Transpose.
    if axis == 0:
        llh_t = llh_t.T
        vne_t = ven_t.T
        rpy_t = rpy_t.T

    # storage
    K = fbbi_t.shape[1]
    llh_t = np.zeros((3, K))
    vne_t = np.zeros((3, K))
    rpy_t = np.zeros((3, K))

    # Initialize rotation matrix.
    Cnb = r3f.rpy_to_dcm(rpy[0], rpy[1], rpy[2]).T

    # time loop
    for k in range(K):
        # inputs
        fbbi = fbbi_t[:, k]
        wbbi = wbbi_t[:, k]

        # rotation rates
        wnei = np.array([
            r3f.W_EI*np.cos(llh[0]),
            0.0,
            -r3f.W_EI*np.sin(llh[0])])
        klat = np.sqrt(1 - r3f.E2*np.sin(llh[0])**2)
        Rt = r3f.A_E/klat
        Rm = (Rt/klat**2)*(1 - r3f.E2)
        wnne = np.array([
            vne[1]/(Rt + llh[2]),
            -vne[0]/(Rm + llh[2]),
            -vne[1]*np.tan(llh[0])/(Rt + llh[2])])

        # derivatives
        Dllh = np.array([-wnne[1], wnne[0]/np.cos(llh[0]), -vne[2]])
        grav = np.array([0, 0, grav_model(*llh)])
        Dvne = Cnb @ fbbi - np.cross(2*wnei + wnne, vne) + grav
        wbbn = wbbi - Cnb.T @ (wnne + wnei)

        # results storage
        llh_t[:, k] = llh
        vne_t[:, k] = vne
        rpy_t[:, k] = r3f.dcm_to_rpy(Cnb.T)

        # integration
        llh += Dllh * T
        vne += Dvne * T
        Cnb = Cnb @ r3f.rodrigues_rotation(wbbn * T)
        Cnb = r3f.orthonormalize_dcm(Cnb)

        # progress bar
        if show_progress:
            progress(k, K)

    # Transpose back.
    if axis == 0:
        llh_t = llh_t.T
        vne_t = vne_t.T
        rpy_t = rpy_t.T

    return llh_t, vne_t, rpy_t
