"""
Example on retrieving and plotting winds
----------------------------------------

This is a simple example for how to retrieve and plot winds from 2 radars
using PyDDA.

Author: Robert C. Jackson

"""

import pyart
import pydda
import numpy as np
from matplotlib import pyplot as plt


berr_grid = pyart.io.read_grid(pydda.tests.EXAMPLE_RADAR0)
cpol_grid = pyart.io.read_grid(pydda.tests.EXAMPLE_RADAR1)

sounding = pyart.io.read_arm_sonde(
    pydda.tests.SOUNDING_PATH)[1]

# Load sounding data and insert as an intialization
u_init, v_init, w_init = pydda.initialization.make_wind_field_from_profile(
        cpol_grid, sounding, vel_field='corrected_velocity')

print(u_init)
# Start the wind retrieval. This example only uses the mass continuity
# and data weighting constraints.
for cms in range(0, 17):
    Cm = 2**cms
    u_back = sounding.u_wind
    v_back = sounding.v_wind
    z_back = sounding.height
    Grids = pydda.retrieval.get_dd_wind_field([berr_grid, cpol_grid], u_init,
                                          v_init, w_init, Co=1.0, Cm=Cm,
                                          Cx=0.0, Cy=0., Cz=0.0, Cb=0,
                                          frz=5000.0, filter_window=5,
                                          mask_outside_opt=True, upper_bc=1,
                                          wind_tol=0.5, engine="tensorflow",
                                          u_back=u_back, v_back=v_back,
                                          z_back=z_back)
    pyart.io.write_grid('Darwin_tf%d.nc' % int(Cm), Grids[0])
