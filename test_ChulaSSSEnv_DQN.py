import ray
import ray.tune  as tune

from ChulaSSSEnv import ChulaSSSEnv

if __name__ == "__main__":
    ray.init()
    experiment_spec = tune.Experiment(
        name = "experiment_dqn",
        run = "DQN",
        config = {
            "num_gpus": 0,
            "num_workers": 1,
            "env": ChulaSSSEnv,
            "env_config" : {"observation_space": "default",
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
                       "step_size" : 10,
                       "alpha":10,
                       "beta":1,
                       }
            }
        
        )
    tune.run_experiments(experiment_spec, resume=True)
