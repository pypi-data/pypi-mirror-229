from gym.envs.registration import register

register(
    id='gym_bwm-v0',
    entry_point='gym_bwm.envs:PandaEnv'
)
