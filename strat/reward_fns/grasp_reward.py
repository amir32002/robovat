"""Reward function of the environments.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np

from strat.reward_fns import reward_fn
from strat.utils.logging import logger


class GraspReward(reward_fn.RewardFn):
    """Reward function of the environments."""
    
    def __init__(self,
                 name,
                 end_effector_name,
                 graspable_name,
                 terminate_after_grasp=True,
                 streaming_length=1000):
        """Initialize."""
        self.name = name 
        self.end_effector_name = end_effector_name
        self.graspable_name = graspable_name
        self.terminate_after_grasp = terminate_after_grasp
        self.streaming_length = streaming_length

        self.env = None
        self.end_effector = None
        self.graspable = None

        self.history = []

    def on_episode_start(self):
        """Called at the start of each episode."""
        self.end_effector = self.env.simulator.bodies[self.end_effector_name]
        self.graspable = self.env.simulator.bodies[self.graspable_name]

    def get_reward(self):
        """Returns the reward value of the current step."""
        if self.env.simulator:
            self.env.simulator.wait_until_stable(self.graspable)
            success = self.env.simulator.check_contact(
                self.end_effector, self.graspable)
        else:
            raise NotImplementedError

        self._update_history(success)
        success_rate = np.mean(self.history or [-1])
        logger.debug('Grasp Success: %r, Success Rate %.3f',
                     success, success_rate)

        return success, self.terminate_after_grasp

    def _update_history(self, success):
        self.history.append(success)

        if len(self.history) > self.streaming_length:
            self.history = self.history[-self.streaming_length:]
