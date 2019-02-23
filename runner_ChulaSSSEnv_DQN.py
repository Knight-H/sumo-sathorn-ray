import ray
import ray.tune  as tune

from ChulaSSSEnv import ChulaSSSEnv
import logger_callbacks
from ActionLogger import ActionLogger
import argparse

from constants import STEP_LENGTH, IMPATIENCE_TIME, STEP_SIZE, GREAT_EDITION, WITH_GUI, WITH_LIBSUMO, VIEWPORT, TIME_SELECT_STR

def main():
    parser = argparse.ArgumentParser(description='ChulaSSSEnv DQN Runner')
    # === Flags for Name Arguments === 
    parser.add_argument('-A', '--algorithm', action='store',default='DQN', type=str,
                        help='The algorithm to train', choices=['DQN', 'APEX'])
    parser.add_argument('-O', '--observation', action='store', default='default', type=str,
                        help='The observation space', choices=['default', 'all3', "all3_no_downstream", "no_downstream"])
    parser.add_argument('-s', '--seed', action='store', default=20, type=int,
                        help='Seed number')
    parser.add_argument('-g', '--gamma', action='store', default=0.9, type=float,
                        help='Discount Factor')
    parser.add_argument('-a', '--alpha', action='store', default=10.0, type=float,
                        help='Reward throughput coefficient')
    parser.add_argument('-b', '--beta', action='store',  default=0.0, type=float,
                        help='Reward backlog coefficient')
    parser.add_argument('-l', '--learningRate', action='store', default=5e-4, type=str,
                        help='Learning Rate (scientific notation) ie. 5e-4')
    parser.add_argument('-T', '--annealTimeStep', action='store',  default='100k', type=str,
                        help='Exploration Annealing Timesteps (in k)')
    parser.add_argument('-e', '--epsilon', action='store', default=0.1, type=float,
                        help='The exploration fraction to anneal to')
    parser.add_argument('-p', '--prioritizedReplay', action='store_true',
                        help='Whether to use prioritized replay')
    parser.add_argument('-H', '--hidden', action='store',  default='256', type=str,
                        help='Hidden Layers (comma separated)')
    parser.add_argument('-N', '--noisy', action='store_true',
                        help='Noisy network')
    parser.add_argument('-D', '--dueling', action='store_true',
                        help='Dueling DQN')
    parser.add_argument('-d', '--double', action='store_true',
                        help='Double DQN')
    parser.add_argument('-u', '--updateFreq', action='store',  default=800, type=int,
                        help='Network update frequency')
    parser.add_argument('-B', '--buffer', action='store', default='100k', type=str,
                        help='Size of replay buffer (in k)')
    parser.add_argument('-L', '--load', action='store', default=1.0, type=float,
                        help='Load factor of Great routes')
    # === Flags for running arguments ===
    parser.add_argument('-i', '--trainIter', action='store', default=100000, type=int,
                        help='Training Iteration')
    parser.add_argument('-c', '--checkFreq', action='store',  default=5, type=int,
                        help='Checkpoint saving frequency')
    parser.add_argument('--learningStart', action='store', default=4320, type=int,
                        help='Steps before Learning starts')
    parser.add_argument('--trainBatch', action='store', default=4, type=int,
                        help='Training batch size')
    parser.add_argument('--sampleBatch', action='store', default=32, type=int,
                        help='Sample batch size')


    args = parser.parse_args()

    

    # Name Structure
    # Algorithm_ObservationSpace_Seed_Gamma_Alpha_Beta_LearningRate
    #          _ExplorationAnnealingTimesteps_ExplorationFraction
    #          _PrioritizedReplay_Hidden_Noisy_Dueling_DoubleQ_NetworkUpdateFreq_Buffer
    #          _LoadFactor
    #
    # ie. DQN_default_s20_g0.6_a10_b1_lr5e-4_et50k_e0.1_pr0_h256_n0_d0_qq0_u800_l1.0

    NAME = "{}_{}_s{}_g{}_a{}_b{}_lr{:.0e}_et{}_e{}_pr{:n}_h{}_n{:n}_d{:n}_qq{:n}_u{}_b{}_l{}".format(args.algorithm, args.observation, args.seed,
                                                                                               args.gamma, args.alpha, args.beta, args.learningRate,
                                                                                               args.annealTimeStep, args.epsilon, args.prioritizedReplay,
                                                                                              args.hidden, args.noisy, args.dueling, args.double,
                                                                                                      args.updateFreq, args.buffer, args.load
                                                                                              )
    print("Starting Experiment with name {}".format(NAME))
    
    OPT = NAME.split("_")

    OPTIONS = {"alg": OPT[0],
               "obs_space": OPT[1],
               "seed" : int(OPT[2][1:]),
               "gamma" : float(OPT[3][1:]),
               "alpha" : float(OPT[4][1:]),
               "beta" : float(OPT[5][1:]),
               "lr"   : float(OPT[6][2:]),
               "epsilon_ts" : int(OPT[7][2:-1])*1000,
               "epsilon" : float(OPT[8][1:]) ,
               "pr" :  bool(int(OPT[9][2:])),
               "hidden": list(map(int,OPT[10][1:].split(','))),
               "noisy" : bool(int(OPT[11][1:])),
               "dueling" : bool(int(OPT[12][1:])),
               "doubleQ" : bool(int(OPT[13][2:])),
               "update_freq" : int(OPT[14][1:]),
               "buffer" : int(OPT[15][1:-1])*1000,
               "load" : float(OPT[16][1:])
               }
    
    ray.init(#object_store_memory=int(4e9),  # 4gb
             #redis_max_memory=int(2e9)  #2gb
             )
    experiment_spec = tune.Experiment(
        name = NAME,
        run = OPTIONS["alg"],
        checkpoint_freq = args.checkFreq,
        checkpoint_at_end = True,
        stop = {
            "training_iteration" : args.trainIter
        },
        upload_dir = "gs://ray_results/",
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


            # === Model ===
            # Number of atoms for representing the distribution of return. When
            # this is greater than 1, distributional Q-learning is used.
            # the discrete supports are bounded by v_min and v_max
            "num_atoms" : 1,
            "v_min": -10.0,
            "v_max": 10.0,
            # Whether to use noisy network
            "noisy": OPTIONS['noisy'],
            # Whether to use dueling dqn
            "dueling": OPTIONS['dueling'],
            # Whether to use double dqn
            "double_q": OPTIONS['dueling'],
            # Hidden layer sizes of the state and action value networks
            "hiddens": OPTIONS['hidden'],
            # N-step Q learning
            "n_step": 1,

            # === Exploration ===
            # Max num timesteps for annealing schedules. Exploration is annealed from
            # 1.0 to exploration_fraction over this number of timesteps scaled by
            # exploration_fraction
            "schedule_max_timesteps": OPTIONS['epsilon_ts'],
            # Number of env steps to optimize for before returning
                        #morning: 10800/10 = 1080 steps total 
            "timesteps_per_iteration": 1080,
            # Fraction of entire training period over which the exploration rate is
            # annealed
            "exploration_fraction": 1,
            # Final value of random action probability
            "exploration_final_eps": OPTIONS['epsilon'],
            # Update the target network every `target_network_update_freq` steps.
            "target_network_update_freq": OPTIONS['update_freq'],
            

            # === Replay buffer ===
            # Size of the replay buffer. Note that if async_updates is set, then
            # each worker will have a replay buffer of this size.
            "buffer_size": OPTIONS['buffer'],
            # If True prioritized replay buffer will be used.
            "prioritized_replay": OPTIONS['pr'],
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
            "lr": OPTIONS['lr'],
            # Adam epsilon hyper parameter
            "adam_epsilon": 1e-8,
            # If not None, clip gradients during optimization at this value
            "grad_norm_clipping": 40,
            # How many steps of the model to sample before learning starts.
            "learning_starts": args.learningStart,
            # Update the replay buffer with this many samples at once. Note that
            # this setting applies per-worker if num_workers > 1.
            # Default sample batch size
            "sample_batch_size": args.sampleBatch,
            # Size of a batched sampled from replay buffer for training. Note that
            # if async_updates is set, then each worker returns gradients for a
            # batch of this size.
            # Training batch size, if applicable. Should be >= sample_batch_size.
            # Samples batches will be concatenated together to this size for training.
            "train_batch_size": args.trainBatch,

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
            "gamma": OPTIONS['gamma'],

            
            "env": ChulaSSSEnv,
            "env_config" : {"observation_space": OPTIONS['obs_space'],
                       "time_select" : TIME_SELECT_STR,
                       "great_edition" : GREAT_EDITION,
                       "with_gui" : WITH_GUI,
                       "with_libsumo" : WITH_LIBSUMO,
                       "no_internal_links" : True,
                       "time_to_teleport": -1,
                       "viewport": VIEWPORT,
                       "step_length": STEP_LENGTH,
                       "seed" : OPTIONS['seed'],
                       "impatience_time": IMPATIENCE_TIME,
                       "step_size" : STEP_SIZE,
                       "alpha":OPTIONS['alpha'],
                       "beta":OPTIONS['beta'],
                        "name" : NAME,
                        "load": OPTIONS['load']
                       }
            
            }
        
        )
    tune.run_experiments(experiment_spec, resume='prompt')

if __name__ == "__main__":
    main()

    
