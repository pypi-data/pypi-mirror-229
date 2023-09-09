from gym.envs.registration import register
from gym_tom.envs.grid_world import GridWorldB

register(
    id="gym_tom/GridWorld-v0",
    entry_point="gym_tom.envs:GridWorldB",
)
