from ronswanson.band_simulation import BandSimulation as Simulation
from joblib import Parallel, delayed
import json
import numpy as np
from tqdm.auto import tqdm
from ronswanson import ParameterGrid
from ronswanson.utils.logging import setup_logger
from ronswanson.simulation import gather
log = setup_logger(__name__)

pg = ParameterGrid.from_yaml('/Users/jburgess/coding/projects/ronswanson/scripts/parameters.yml')
def func(i):
    params = pg.at_index(i)
    simulation = Simulation(i, params, pg.energy_grid,'/Users/jburgess/coding/projects/ronswanson/scripts/test_database.h5')
    simulation.run()
iteration = [i for i in range(0, pg.n_points)]
Parallel(n_jobs=10)(delayed(func)(i) for i in tqdm(iteration, colour='#FC0A5A'))
gather('/Users/jburgess/coding/projects/ronswanson/scripts/test_database.h5', 0, clean=True)
