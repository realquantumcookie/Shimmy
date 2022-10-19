import inspect

import numpy as np
import pytest
from dm_control import suite
from dm_control.suite import (acrobot, ball_in_cup, cartpole, cheetah, dog,
                              finger, fish, hopper, humanoid, humanoid_CMU,
                              lqr, manipulator, pendulum, point_mass,
                              quadruped, reacher, stacker, swimmer, walker)
from PIL import Image

from shimmy import dm_control_wrapper

# Find all domains imported.
_DOMAINS = {
    name: module
    for name, module in locals().items()
    if inspect.ismodule(module) and hasattr(module, "SUITE")
}


@pytest.mark.parametrize("domain_name", _DOMAINS.keys())
def test_all_envs(domain_name):
    # for each possible task in the domain:
    for task_name in _DOMAINS[domain_name].SUITE:
        # load the suite
        env = suite.load(domain_name, task_name)

        # convert the environment
        env = dm_control_wrapper(env, render_mode="rgb_array")
        env.reset()

        term, trunc = False, False

        # run until termination
        while not term and not trunc:
            obs, rew, term, trunc, info = env.step(env.action_space.sample())


def test_seeding():
    # load envs
    env1 = suite.load("hopper", "stand")
    env2 = suite.load("hopper", "stand")

    # convert the environment
    env1 = dm_control_wrapper(env1, render_mode="rgb_array")
    env2 = dm_control_wrapper(env2, render_mode="rgb_array")
    env1.reset(seed=42)
    env2.reset(seed=42)

    for i in range(100):
        returns1 = env1.step(env1.action_space.sample())
        returns2 = env2.step(env2.action_space.sample())

        for stuff1, stuff2 in zip(returns1, returns2):
            if isinstance(stuff1, bool):
                assert stuff1 == stuff2, f"Incorrect returns on iteration {i}."
            elif isinstance(stuff1, np.ndarray):
                assert (stuff1 == stuff2).all(), f"Incorrect returns on iteration {i}."


def test_render():
    # load an env
    env = suite.load("hopper", "stand")

    # convert the environment
    env = dm_control_wrapper(env, render_mode="rgb_array")
    env.reset()

    frames = []
    for _ in range(100):
        obs, rew, term, trunc, info = env.step(env.action_space.sample())
        frames.append(env.render())

    frames = [Image.fromarray(frame) for frame in frames]
    frames[0].save(
        "array.gif", save_all=True, append_images=frames[1:], duration=50, loop=0
    )
