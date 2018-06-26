from gym.envs.registration import register

register(
    id='NaoEnv-v0',
    entry_point='naoenv.naoenv:NaoEnv',
)
