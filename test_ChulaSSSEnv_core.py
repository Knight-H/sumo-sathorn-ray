from ChulaSSSEnv import ChulaSSSEnv
import numpy as np

if __name__ == "__main__":
    env = ChulaSSSEnv(env_config= {"observation_space": "default",
                       "time_select" : "morning",
                       "great_edition" : True,
                       "with_gui" : False,
                       "with_libsumo" : True,
                       "no_internal_links" : True,
                       "time_to_teleport": -1,
                       "viewport": "surasak",
                       "step_length": 1,
                       "seed" : 20,
                       "impatience_time": 300,
                       "step_size" : 5,
                        "alpha" : 1,
                        "beta" : 1 ,
                       })
    # Test actions
    for i in range(20):
        env.step(action=1)
    for i in range(20):
        env.step(action=2)
    for i in range(20):
        env.step(action=7)
    # Test reset
    print("Observation of reset {}".format(env.reset()))

    # Test Observation
    for i in range(100):
        observation, reward, done, info = env.step(action=2)
        print("Occupancy: {} Action: {} Reward: {}  Done: {} Info: {}".format(observation[0].astype(int),observation[1] , reward, done, info))
    for i in range(100):
        observation, reward, done, info = env.step(action=2)
        print("Occupancy: {} Action: {} Reward: {}  Done: {} Info: {}".format(observation[0].astype(int),observation[1] , reward, done, info))
    env.close()
