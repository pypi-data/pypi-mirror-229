"""
--------------------------------------------------------------------------------
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

Cleared for public release: 88ABW-2023-0793
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

Vectorization
-------------
When possible, the functions are vectorized in order to handle processing
batches of values. A set of scalars is a 1D array. A set of vectors is a 2D
array, with each vector in a column. So, a (3, 7) array is a set of seven
vectors, each with 3 elements. If an input matrix does not have 3 rows, it will
be assumed that the rows of the matrix are vectors.
--------------------------------------------------------------------------------
"""

__author__ = "David Woodburn"
__license__ = "MIT"
__date__ = "2023-09-08"
__maintainer__ = "David Woodburn"
__email__ = "david.woodburn@icloud.com"
__status__ = "Development"

import numpy as np

# WGS84 constants (IS-GPS-200M and NIMA TR8350.2)
A_E = 6378137.0             # Earth's semi-major axis [m] (p. 109)
E2 = 6.694379990141317e-3   # Earth's eccentricity squared [ND] (derived)
W_EI = 7.2921151467e-5      # sidereal Earth rate [rad/s] (p. 106)

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


def somigliana(llh_t):
    """
    Calculate the local acceleration of gravity vector in the navigation frame
    using the Somigliana equation. The navigation frame here has the North,
    East, Down (NED) orientation.

    Parameters
    ----------
    llh_t : (3,) or (3, K) or (K, 3) np.ndarray
        Geodetic position vector of latitude (radians), longitude (radians), and
        height above ellipsoid (meters) or matrix of such vectors.

    Returns
    -------
    gamma : (3,) or (3, K) or (K, 3) np.ndarray
        Acceleration of gravity in meters per second squared.
    """

    # Check input.
    if isinstance(llh_t, list):
        llh_t = np.array(llh_t)
    trs = (llh_t.ndim == 2 and llh_t.shape[0] != 3)

    # gravity coefficients
    ge = 9.7803253359
    k = 1.93185265241e-3
    f = 3.35281066475e-3
    m = 3.44978650684e-3

    # Transpose the input.
    if trs:
        llh_t = llh_t.T

    # Get local acceleration of gravity for height equal to zero.
    slat = np.sin(llh_t[0])
    klat = np.sqrt(1 - E2*slat**2)
    grav_z0 = ge*(1 + k*slat**2)/klat

    # Calculate gamma for the given height.
    grav_z = grav_z0*(1 + (3/A_E**2)*llh_t[2]**2
        - 2/A_E*(1 + f + m - 2*f*slat**2)*llh_t[2])

    # Form vector.
    if isinstance(grav_z, np.ndarray):
        K = len(grav_z)
        grav = np.zeros((3, K))
        grav[2, :] = grav_z
        if trs:
            grav = grav.T
    else:
        grav = np.array([0.0, 0.0, grav_z])

    return grav


def rpy_to_dcm(rpy):
    """
    Convert roll, pitch, and yaw Euler angles to a direction cosine matrix that
    represents a zyx sequence of right-handed rotations.

    Parameters
    ----------
    rpy : (3,) list or np.ndarray
        Roll, pitch, and yaw Euler angle in radians.

    Returns
    -------
    C : (3, 3) np.ndarray
        Rotation matrix.
    """

    # Get the cosine and sine functions.
    r, p, y = rpy
    cr = np.cos(r)
    sr = np.sin(r)
    cp = np.cos(p)
    sp = np.sin(p)
    cy = np.cos(y)
    sy = np.sin(y)

    # Build the 3x3 matrix.
    C = np.array([
        [            cp*cy,             cp*sy,   -sp],
        [-cr*sy + sr*sp*cy,  cr*cy + sr*sp*sy, sr*cp],
        [ sr*sy + cr*sp*cy, -sr*cy + cr*sp*sy, cr*cp]])

    return C


def dcm_to_rpy(C):
    """
    Convert a direction cosine matrix (DCM) to roll, pitch, and yaw Euler
    angles. This DCM represents the zyx sequence of right-handed rotations.

    Parameters
    ----------
    C : (3, 3) list or np.ndarray
        Rotation matrix.

    Returns
    -------
    rpy : (3,) np.ndarray
        Roll, pitch, and yaw Euler angle in radians.
    """

    # Parse out the elements of the DCM that are needed.
    c11 = C[0, 0]
    c33 = C[2, 2]
    c12 = C[0, 1]
    c13 = C[0, 2]
    c23 = C[1, 2]

    # Get roll.
    rpy = np.zeros(3)
    rpy[0] = np.arctan2(c23, c33)

    # Get pitch.
    sp = -c13
    pa = np.arcsin(sp)
    nm = np.sqrt(c11**2 + c12**2 + c23**2 + c33**2)
    pb = np.arccos(nm/np.sqrt(2))
    rpy[1] = (1.0 - np.abs(sp))*pa + sp*pb

    # Get yaw.
    rpy[2] = np.arctan2(c12, c11)

    return rpy


def orthonormalize_dcm(C):
    """
    Orthonormalize the rotation matrix using the Modified Gram-Schmidt
    algorithm. This function modifies the matrix in-place. Note that this
    algorithm only moves the matrix towards orthonormality; it does not
    guarantee that after one function call the returned matrix will be
    orthonormal. However, with a 1e-15 tolerance, orthonormality can be
    acheived typically within at most 2 function calls.

    Parameters
    ----------
    C : (3, 3) np.ndarray
        Square matrix.
    """

    # Orthonormalize a single matrix.
    C[:, 0] /= np.sqrt(C[0, 0]**2 + C[1, 0]**2 + C[2, 0]**2)
    C[:, 1] -= C[:, 0].dot(C[:, 1])*C[:, 0]
    C[:, 1] /= np.sqrt(C[0, 1]**2 + C[1, 1]**2 + C[2, 1]**2)
    C[:, 2] -= C[:, 0].dot(C[:, 2])*C[:, 0]
    C[:, 2] -= C[:, 1].dot(C[:, 2])*C[:, 1]
    C[:, 2] /= np.sqrt(C[0, 2]**2 + C[1, 2]**2 + C[2, 2]**2)


def rodrigues_rotation(theta):
    """
    Convert an active rotation vector to its passive equivalent rotation matrix.
    The rotation vector should not have a norm greater than pi. If it does,
    scale the vector by `-(2 pi - n)/n`, where `n` is the norm of the rotation
    vector.

    Parameters
    ----------
    theta : (3,) list or np.ndarray
        Three-element vector of angles in radians.

    Returns
    -------
    Delta : (3, 3) np.ndarray
        Three-by-three matrix.
    """

    # Get the vector norm.
    x2 = theta[0]*theta[0]
    y2 = theta[1]*theta[1]
    z2 = theta[2]*theta[2]
    nm2 = x2 + y2 + z2
    nm = np.sqrt(nm2)

    # Get the sine and cosine factors.
    if nm < 0.04e-6:
        s = 1.0
    else:
        s = np.sin(nm)/nm
    if nm < 0.2e-3:
        c = 0.5
    else:
        c = (1 - np.cos(nm))/nm2

    # Get the rotation matrix.
    Delta = np.array([
        [1.0 - c*(y2 + z2),
            c*theta[0]*theta[1] - s*theta[2],
            c*theta[0]*theta[2] + s*theta[1]],
        [c*theta[0]*theta[1] + s*theta[2],
            1.0 - c*(x2 + z2),
            c*theta[1]*theta[2] - s*theta[0]],
        [c*theta[0]*theta[2] - s*theta[1],
            c*theta[1]*theta[2] + s*theta[0],
            1.0 - c*(x2 + y2)]])

    return Delta


def inverse_rodrigues_rotation(Delta):
    """
    Convert a passive rotation matrix to its equivalent active rotation vector.
    The rotation vector will not have a norm greater than pi.

    Parameters
    ----------
    Delta : (3, 3) np.ndarray
        Three-by-three matrix.

    Returns
    -------
    theta : (3,) np.ndarray
        Three-element vector of angles in radians.
    """

    # Get the trace of the matrix.
    q = Delta[0, 0] + Delta[1, 1] + Delta[2, 2]
    q = q if q <= 3 else 3 # limit

    # Get the scaling factor of the vector.
    ang = np.arccos((q-1)/2)
    s = ang/np.sqrt(3 + 2*q - q**2) if (q <= 2.9995) \
            else (q**2 - 11*q + 54)/60

    # Build the vector.
    theta = s*np.array([
        Delta[2, 1] - Delta[1, 2],
        Delta[0, 2] - Delta[2, 0],
        Delta[1, 0] - Delta[0, 1]])

    return theta


def est_wind(vne_t, yaw_t):
    """
    Estimate the time-varying wind by comparing the ground travel velocity to
    the yaw (heading) angle.

    Parameters
    ----------
    vne_t : (3,) or (3, K) or (K, 3) np.ndarray
        North, East, and Down velocity vector of the navigation frame relative
        to the ECEF frame (meters per second).
    yaw_t : (K,) np.ndarray
        Yaw angle clockwise from north in radians.

    Returns
    -------
    wind_t : (2,) or (2, K) or (K, 2) np.ndarray
        North and East components of wind vector in meters per second.
    """

    # Check input.
    if isinstance(vne_t, list):
        vne_t = np.array(vne_t)
    if isinstance(yaw_t, list):
        yaw_t = np.array(yaw_t)
    trs = (vne_t.ndim == 2 and vne_t.shape[0] != 3)

    # Transpose input.
    if trs:
        vne_t = vne_t.T

    # Get the horizontal speed.
    sH_t = np.sqrt(vne_t[0]**2 + vne_t[1]**2)

    # Get the estimated wind.
    wind_t = np.array([
        vne_t[0] - sH_t*np.cos(yaw_t),
        vne_t[1] - sH_t*np.sin(yaw_t)])

    # Transpose.
    if trs:
        wind_t = wind_t.T

    return wind_t

# -------------
# Mechanization
# -------------

def llh_to_vne(llh_t, T):
    """
    Convert geodetic position over time to velocity of the navigation frame
    relative to the earth frame over time. Geodetic position is quadratically
    extrapolated by one sample.

    Parameters
    ----------
    llh_t : (3, K) or (K, 3) np.ndarray
        Matrix of geodetic position vectors of latitude (radians), longitude
        (radians), and height above ellipsoid (meters).
    T : float
        Sampling period in seconds.

    Returns
    -------
    vne : (3, K) or (K, 3) np.ndarray
        Matrix of velocity vectors.
    """

    # Check input.
    if isinstance(llh_t, list):
        llh_t = np.array(llh_t)
    trs = (llh_t.ndim == 2 and llh_t.shape[0] != 3)

    # Transpose the input.
    if trs:
        llh_t = llh_t.T

    # Parse geodetic position.
    lat = llh_t[0]
    lon = llh_t[1]
    hae = llh_t[2]

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
    klat = np.sqrt(1 - E2*np.sin(lat)**2)
    Rm = (A_E/klat**3)*(1 - E2)
    Rt = A_E/klat
    vN = -wnne_y*(Rm + hae)
    vE =  wnne_x*(Rt + hae)
    vD = -Dhae
    if trs:
        vne = np.column_stack((vN, vE, vD))
    else:
        vne = np.row_stack((vN, vE, vD))

    return vne


def vne_to_rpy(vne_t, grav_t, T, alpha=0.0, wind=None):
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

    Returns
    -------
    rpy_t : (3, K) or (K, 3) np.ndarray
        Matrix of vectors of attitude angles roll, pitch, and yaw, all in
        radians. These angles are applied in the context of a North, East, Down
        navigation frame to produce the body frame in a zyx sequence of passive
        rotations.
    """

    # Check input.
    if isinstance(vne_t, list):
        vne_t = np.array(vne_t)
    if isinstance(grav_t, list):
        grav_t = np.array(grav_t)
    trs = (vne_t.ndim == 2 and vne_t.shape[0] != 3)

    # Transpose.
    if trs:
        vne_t = vne_t.T

    # Filter the velocity.
    vN, vE, vD = vne_t

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
    ac = (vN*aE - vE*aN)/(vH + 1e-4) # cross product vH with axy
    rol = np.arctan(ac/grav_t)*(vH > 1e-6)

    # Assemble.
    if trs:
        rpy_t = np.column_stack((rol, pit, yaw))
    else:
        rpy_t = np.row_stack((rol, pit, yaw))

    return rpy_t


def inv_mech(llh_t, vne_t, rpy_t, T, grav_model=somigliana, show_progress=True):
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
    grav_model : function, default somigliana
        The gravity model function to use. This function should take a position
        vector of latitude (radians), longitude (radians), and height above
        ellipsoid (meters) and return the local acceleration of gravity vector
        (meters per second squared) in the navigation frame with a North, East,
        Down (NED) orientation.
    show_progress : bool, default True
        Flag to show the progress bar in the terminal.

    Returns
    -------
    fbbi_t : (3, K) or (K, 3) np.ndarray
        Matrix of specific force vectors (meters per second squared) of the body
        frame relative to the inertial frame, referenced in the body frame.
    wbbi_t : (3, K) or (K, 3) np.ndarray
        Matrix of rotation rate vectors (radians per second) of the body frame
        relative to the inertial frame, referenced in the body frame.
    """

    # Check input.
    if isinstance(llh_t, list):
        llh_t = np.array(llh_t)
    if isinstance(vne_t, list):
        vne_t = np.array(vne_t)
    if isinstance(rpy_t, list):
        rpy_t = np.array(rpy_t)
    trs = (llh_t.ndim == 2 and llh_t.shape[0] != 3)

    # Transpose.
    if trs:
        llh_t = llh_t.T
        vne_t = vne_t.T
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
        Cnb = rpy_to_dcm(rpy).T
        Cnb_p = rpy_to_dcm(rpy_p).T
        wbbn = inverse_rodrigues_rotation(Cnb.T @ Cnb_p)/T

        # rotation rates
        wnne = np.array([
            np.cos(llh[0])*Dllh[1],
            -Dllh[0],
            -np.sin(llh[0])*Dllh[1]])
        wnei = np.array([
            W_EI*np.cos(llh[0]),
            0.0,
            -W_EI*np.sin(llh[0])])
        wbbi = wbbn + Cnb.T @ (wnne + wnei)

        # specific force
        grav = grav_model(llh)
        fbbi = Cnb.T @ (Dvne + np.cross(2*wnei + wnne, vne) - grav)

        # results storage
        fbbi_t[:, k] = fbbi
        wbbi_t[:, k] = wbbi

        # progress bar
        if show_progress:
            progress(k, K - 1)

    # Transpose back.
    if trs:
        fbbi_t = fbbi_t.T
        wbbi_t = wbbi_t.T

    return fbbi_t, wbbi_t


def mech(fbbi_t, wbbi_t, llh0, vne0, rpy0, T, grav_model=somigliana,
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
    grav_model : function, default somigliana
        The gravity model function to use. This function should take a position
        vector of latitude (radians), longitude (radians), and height above
        ellipsoid (meters) and return the local acceleration of gravity vector
        (meters per second squared) in the navigation frame with a North, East,
        Down (NED) orientation.
    show_progress : bool, default True
        Flag to show the progress bar in the terminal.

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
    if isinstance(fbbi_t, list):
        fbbi_t = np.array(fbbi_t)
    if isinstance(wbbi_t, list):
        wbbi_t = np.array(wbbi_t)
    if isinstance(llh0, list):
        llh0 = np.array(llh0)
    if isinstance(vne0, list):
        vne0 = np.array(vne0)
    if isinstance(rpy0, list):
        rpy0 = np.array(rpy0)
    trs = (fbbi_t.ndim == 2 and fbbi_t.shape[0] != 3)

    # Initialize states.
    llh = llh0.copy()
    vne = vne0.copy()
    rpy = rpy0.copy()

    # Transpose.
    if trs:
        fbbi_t = fbbi_t.T
        wbbi_t = wbbi_t.T

    # storage
    K = fbbi_t.shape[1]
    llh_t = np.zeros((3, K))
    vne_t = np.zeros((3, K))
    rpy_t = np.zeros((3, K))

    # Initialize rotation matrix.
    Cnb = rpy_to_dcm(rpy).T

    # time loop
    for k in range(K):
        # inputs
        fbbi = fbbi_t[:, k]
        wbbi = wbbi_t[:, k]

        # rotation rates
        wnei = np.array([
            W_EI*np.cos(llh[0]),
            0.0,
            -W_EI*np.sin(llh[0])])
        klat = np.sqrt(1 - E2*np.sin(llh[0])**2)
        Rt = A_E/klat
        Rm = (Rt/klat**2)*(1 - E2)
        wnne = np.array([
            vne[1]/(Rt + llh[2]),
            -vne[0]/(Rm + llh[2]),
            -vne[1]*np.tan(llh[0])/(Rt + llh[2])])

        # derivatives
        Dllh = np.array([-wnne[1], wnne[0]/np.cos(llh[0]), -vne[2]])
        grav = grav_model(llh)
        Dvne = Cnb @ fbbi - np.cross(2*wnei + wnne, vne) + grav
        wbbn = wbbi - Cnb.T @ (wnne + wnei)

        # results storage
        llh_t[:, k] = llh
        vne_t[:, k] = vne
        rpy_t[:, k] = dcm_to_rpy(Cnb.T)

        # integration
        llh += Dllh * T
        vne += Dvne * T
        Cnb = Cnb @ rodrigues_rotation(wbbn * T)
        orthonormalize_dcm(Cnb)

        # progress bar
        if show_progress:
            progress(k, K)

    # Transpose back.
    if trs:
        llh_t = llh_t.T
        vne_t = vne_t.T
        rpy_t = rpy_t.T

    return llh_t, vne_t, rpy_t
