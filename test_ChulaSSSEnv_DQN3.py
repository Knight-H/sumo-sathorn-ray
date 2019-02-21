import ray
import ray.tune  as tune

from ChulaSSSEnv import ChulaSSSEnv
import logger_callbacks
from ActionLogger import ActionLogger

if __name__ == "__main__":
    NAME = "test_ChulaSSSEnv_DQN3"
    ray.init(#object_store_memory=int(4e9),  # 4gb
             #redis_max_memory=int(2e9)  #2gb
             )
    experiment_spec = tune.Experiment(
        name = NAME,
        run = "DQN",
        checkpoint_freq = 5,
        checkpoint_at_end = True,
        stop = {
            "training_iteration" : 50
        },
        custom_loggers = [ActionLogger],
        config = {
            # === Configure Callbacks ===
            "callbacks": {
                    "on_episode_start": tune.function(logger_callbacks.on_episode_start),
                    "on_episode_step": tune.function(logger_callbacks.on_episode_step),
                    "on_episode_end": tune.function(logger_callbacks.on_episode_end),
                    "on_sample_end": tune.function(logger_callbacks.on_sample_end),
                    "on_train_result": tune.function(logger_callbacks.on_train_result),
            },
            
            # === Resources ===
            # Number of actors used for parallelism
            "num_workers": 0,
            # Number of GPUs to allocate to the driver. Note that not all algorithms
            # can take advantage of driver GPUs. This can be fraction (e.g., 0.3 GPUs).
            "num_gpus": 0,
            # Number of CPUs to allocate per worker.
            "num_cpus_per_worker": 4,
            # Number of GPUs to allocate per worker. This can be fractional.
            "num_gpus_per_worker": 0,
            # Any custom resources to allocate per worker.
            "custom_resources_per_worker": {},
            # Number of CPUs to allocate for the driver. Note: this only takes effect
            # when running in Tune.
            "num_cpus_for_driver": 1,


            # === Execution ===
            # Number of environments to evaluate vectorwise per worker.
##            "num_envs_per_worker": 1,
            # Default sample batch size
            "sample_batch_size": 4,
            # Training batch size, if applicable. Should be >= sample_batch_size.
            # Samples batches will be concatenated together to this size for training.
            "train_batch_size": 32,

            # === Model ===
            # Number of atoms for representing the distribution of return. When
            # this is greater than 1, distributional Q-learning is used.
            # the discrete supports are bounded by v_min and v_max
            "num_atoms" : 1,
            "v_min": -10.0,
            "v_max": 10.0,
            # Whether to use noisy network
            "noisy": False,
            # Whether to use dueling dqn
            "dueling": False,
            # Whether to use double dqn
            "double_q": False,
            # Hidden layer sizes of the state and action value networks
            "hiddens": [256],
            # N-step Q learning
            "n_step": 1,

            # === Exploration ===
            # Max num timesteps for annealing schedules. Exploration is annealed from
            # 1.0 to exploration_fraction over this number of timesteps scaled by
            # exploration_fraction
            "schedule_max_timesteps": 100000,
            # Number of env steps to optimize for before returning
                        #morning: 10800/10 = 1080 steps total 
            "timesteps_per_iteration": 1080,
            # Fraction of entire training period over which the exploration rate is
            # annealed
            "exploration_fraction": .5,
            # Final value of random action probability
            "exploration_final_eps": 0.1,
            # Update the target network every `target_network_update_freq` steps.
            "target_network_update_freq": 540,

            # === Replay buffer ===
            # Size of the replay buffer. Note that if async_updates is set, then
            # each worker will have a replay buffer of this size.
            "buffer_size": 100000,
            # If True prioritized replay buffer will be used.
            "prioritized_replay": True,
            # Alpha parameter for prioritized replay buffer.
            "prioritized_replay_alpha": 0.6,
            # Beta parameter for sampling from prioritized replay buffer.
            "prioritized_replay_beta": 0.4,
            # Fraction of entire training period over which the beta parameter is
            # annealed
            "beta_annealing_fraction": 0.2,
            # Final value of beta
            "final_prioritized_replay_beta": 0.4,
            # Epsilon to add to the TD errors when updating priorities.
            "prioritized_replay_eps": 1e-6,
            # Whether to LZ4 compress observations
            "compress_observations": True,
            
            
             # === Optimization ===
            # Learning rate for adam optimizer
            "lr": 5e-4,
            # Adam epsilon hyper parameter
            "adam_epsilon": 1e-8,
            # If not None, clip gradients during optimization at this value
            "grad_norm_clipping": 40,
            # How many steps of the model to sample before learning starts.
            "learning_starts": 2160,
            # Update the replay buffer with this many samples at once. Note that
            # this setting applies per-worker if num_workers > 1.
            "sample_batch_size": 4,
            # Size of a batched sampled from replay buffer for training. Note that
            # if async_updates is set, then each worker returns gradients for a
            # batch of this size.
            "train_batch_size": 32,

            # === Parallelism ===
            # Optimizer class to use.
            "optimizer_class": "SyncReplayOptimizer",
            # Whether to use a distribution of epsilons across workers for exploration.
            "per_worker_exploration": False,
            # Whether to compute priorities on workers.
            "worker_side_prioritization": False,
            # Prevent iterations from going lower than this time span
            "min_iter_time_s": 1,
            

            # === Environment ===
            # Discount factor of the MDP
            "gamma": 0.7,

            
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
                       "alpha":1,
                       "beta":0,
                        "name" : NAME,
                        "load": 1
                       }
            
            }
        
        )
    tune.run_experiments(experiment_spec, resume='prompt', raise_on_failed_trial=False)
