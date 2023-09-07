# **R**otation of **3**-dimensional **F**rames

Functions
---------
This library includes four sets of functions: general array checks,
attitude-representation conversions, reference-frame conversions, and rotation
matrix (direction cosine matrix) utilities. The following table shows all the
attitude-representation conversions provided, where 'Vector' is short for
'rotation vector,' 'RPY is short for 'roll, pitch, and yaw,' and 'DCM' is short
for 'direction cosine matrix':

| To \\ From | Vector | Axis-angle | RPY    | DCM    | Quaternion |
| ---------- | :----: | :--------: | :----: | :----: | :--------: |
| Vector     |   -    |     x      |        |        |            |
| Axis-angle |   x    |     -      |   x    |   x    |     x      |
| RPY        |        |     x      |   -    |   x    |     x      |
| DCM        |        |     x      |   x    |   -    |     x      |
| Quaternion |        |     x      |   x    |   x    |     -      |

Because the conversion from rotation vector to axis-angle is so trivial, none of
the other attitude representations have conversions to rotation vectors. Here is
a list of the functions::

    axis_angle_to_vector -> vec     
        (ax, ang, degs=False)
    vector_to_axis_angle -> ax, ang 
        (vec, degs=False)
    rpy_to_axis_angle -> ax, ang 
        (r, p, y, degs=False)
    axis_angle_to_rpy -> r, p, y 
        (ax, ang, degs=False)
    dcm_to_axis_angle -> ax, ang 
        (C, degs=False)
    axis_angle_to_dcm -> C       
        (ax, ang, degs=False)
    quat_to_axis_angle -> ax, ang 
        (q, degs=False)
    axis_angle_to_quat -> q       
        (ax, ang, degs=False)
    dcm_to_rpy -> r, p, y 
        (C, degs=False)
    rpy_to_dcm -> C       
        (r, p, y, degs=False)
    rot -> C       
        (ang, ax=2, degs=False)
    quat_to_rpy -> r, p, y 
        (q, degs=False)
    rpy_to_quat -> q       
        (r, p, y, degs=False)
    quat_to_dcm -> C       
        (q)
    dcm_to_quat -> q       
        (C)

In addition to the conversion from the z, y, x sequence of Euler angles to a
DCM, the function `rot` is also provided for creating a DCM from a generic set
of Euler angles in any desired sequence of axes. Although this `rot` function
could be used, two additional functions are provided for generating rotation
matrices: `dcm_inertial_to_ecef` and `dcm_ecef_to_navigation`.

This library includes all twelve possible conversions among the following four
frames: ECEF (Earth-centered, Earth-fixed), geodetic (latitude, longitude, and
height above ellipsoid), local-level tangent, and local-level curvilinear::

    geodetic_to_ecef -> xe, ye, ze
        (lat, lon, hae, degs=None)
    ecef_to_geodetic -> lat, lon, hae
        (xe, ye, ze, degs=None)
    tangent_to_ecef -> xe, ye, ze
        (xt, yt, zt, xe0=None, ye0=None, ze0=None, ned=None)
    ecef_to_tangent -> xt, yt, zt
        (xe, ye, ze, xe0=None, ye0=None, ze0=None, ned=None)
    curvilinear_to_ecef -> xe, ye, ze
        (xc, yc, zc, xe0=None, ye0=None, ze0=None, ned=None)
    ecef_to_curvilinear -> xc, yc, zc
        (xe, ye, ze, xe0=None, ye0=None, ze0=None, ned=None)
    tangent_to_geodetic -> lat, lon, hae
        (xt, yt, zt, lat0=None, lon0=None, hae0=None, ned=None, degs=None)
    geodetic_to_tangent -> xt, yt, zt
        (lat, lon, hae, lat0=None, lon0=None, hae0=None, ned=None, degs=None)
    curvilinear_to_geodetic -> lat, lon, hae
        (xc, yc, zc, lat0=None, lon0=None, hae0=None, ned=None, degs=None)
    geodetic_to_curvilinear -> xc, yc, zc
        (lat, lon, hae, lat0=None, lon0=None, hae0=None, ned=None, degs=None)
    curvilinear_to_tangent -> xt, yt, zt
        (xc, yc, zc, lat0=None, lon0=None, hae0=None, ned=None, degs=None)
    tangent_to_curvilinear -> xc, yc, zc
        (xt, yt, zt, xe0=None, ye0=None, ze0=None, ned=None)

Passive Rotations
-----------------
Unless specifically otherwise stated, all rotations are interpreted as passive.
This means they represent rotations of reference frames, not of vectors.

Vectorization
-------------
When possible, the functions are vectorized in order to handle processing
batches of values. A set of scalars is a 1D array. A set of vectors is a 2D
array, with each vector in a column. So, a (3, 7) array is a set of seven
vectors, each with 3 elements. A set of matrices is a 3D array with each matrix
in a stack. The first index is the stack number. So, a (5, 3, 3) array is a
stack of five 3x3 matrices. Roll, pitch, and yaw are not treated as a vector but
as three separate quantities. The same is true for latitude, longitude, and
height above ellipsoid. A quaternion is passed around as an array.

Robustness
----------
In general, the functions in this library check that the inputs are of the
correct type and shape. They do not generally handle converting inputs which do
not conform to the ideal type and shape. Generally, the allowed types are float,
int, list, and np.ndarray.
