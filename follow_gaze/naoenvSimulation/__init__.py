from gym.envs.registration import register

register(
    id='NaoEnvSim-v0',
    entry_point='naoenvSimulation.naoenv:NaoEnv',
)
