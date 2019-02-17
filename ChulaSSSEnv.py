import numpy as np
import gym
from gym import error, spaces
import os, sys

from detector_constants import *
from constants import WITH_LIBSUMO, WITH_GUI, edge_sathornN, edge_sathornS, edge_charoenRat, edge_surasak, edge_sathornN_down, edge_sathornS_down, edge_surasak_down, edges

if WITH_LIBSUMO and not WITH_GUI: import libsumo as traci
else: import traci


class ChulaSSSEnv(gym.Env):
    """The main OpenAI Gym class of Chula-SSS

    action_space : 0 to 8
    observation_space :
        Upstream : North (5), South (4), East (4), West(5)
        Downstream: Southbound (1), Eastbound (1), Westbound(1)
        Traffic Light: action_space 1 to 9

    env_config is a Dictionary of all configurations that has the following fields:
        time_select : "morning"/"evening"
        great_edition : True/False                  # Great's Additional Flow (can only be true for morning)
    
        with_gui : True/False
        with_libsumo  : True/False                   # can only be true without GUI Note: doesn't handle here anymore!!!!
        no_internal_links : True/False
        time_to_teleport : -1 or [0, inf]       
        viewport : "whole_loop"/"surasak"
        step_length : (0,1]                              # seconds in step(); MUST BE <= 1 , see https://sourceforge.net/p/sumo/mailman/message/32876223/ 
        seed        :  [0,65535]       
        impatience_time : -1 or [0,inf]             # seconds to impatience -> driver use any gap even if other vehicle needs to brake(http://sumo.dlr.de/wiki/Definition_of_Vehicles,_Vehicle_Types,_and_Routes#Impatience)


        step_size [1,inf]     # the window size of simulation

        # Reward Function
        alpha: [0,inf]
        beta:  [0,inf]
    """
    
    metadata = {'render.modes': []}
    
    def __init__(self, env_config):
        print("i have env_config " , env_config)
        self.alpha = env_config['alpha']
        self.beta = env_config['beta']

        print("i am defining action space")
        # Define action space and observation space
        self.action_space = spaces.Discrete(9)

        # Map between action id and RedYellowGreen state
        #     First four 'G's are for cones
        self.action_map = {
            1: "GGGGrrrrgGGGGGGGGGGGGGGGGgggrrrrrrrrrrrrrGGGGGGGGGGGGGGGG",
            2: "GGGGrrrrgrrrrrrrrrrrrrrrrgggGGGGGGGGGGGGGrrrrrrrrrrrrrrrr",
            3: "GGGGGGGGgrrrrrrrrrrrrrrrrgggrrrrrrrGGGGGGrrrrrrrrrrrrrrrr",
            4: "GGGGrrrrgrrrrrrrrrrrrrrrrgggrrrrrrrrrrrrrGGGGGGGGGGGGGGGG",
            5: "GGGGrrrrgGGGGGGGGGGGGGGGGgggrrrrrrrrrrrrrrrrrrrrrrrrrrrrr",
            6: "GGGGrrrrgrrrrrrrrrrrrrrrrgggGGGGGGGrrrrrrrrrrrrrrrrrrrrrr",
            7: "GGGGrrrrgrrrrrrrrrrrrrrrrgggrrrrrrrGGGGGGrrrrrrrrrrrrrrrr",
            8: "GGGGGGGGgrrrrrrrrrrrrrrrrgggrrrrrrrrrrrrrrrrrrrrrrrrrrrrr",
            0: "GGGGrrrrgrrrrrrrrrrrrrrrrgggrrrrrrrrrrrrrrrrrrrrrrrrrrrrr",
            }
        # Map between action id and downstream edge (for use in throughput)
##        DISCARDED since what about always green?
##        self.action_downstream_edge_map = {
##            1: (edge_sathornN_down[0], edge_sathornS_down[0]),
##            2: (edge_sathornS_down[0], edge_surasak_down[0]),
##            3: (),
##            4: ,
##            5: ,
##            6: ,
##            7: ,
##            8: ,
##            0: (),
##            }

        print("i am defining observation space")
        if env_config['observation_space'] == "no_downstream":
            self.observation_space = spaces.Tuple((spaces.Box(low=0, high=100, shape=(18,), dtype=np.float16),
                                                  self.action_space ))
        elif env_config['observation_space'] == "all3_no_downstream":
            self.observation_space = spaces.Tuple((spaces.Box(low=0, high=100, shape=(12,), dtype=np.float16),
                                                  self.action_space ))
        elif env_config['observation_space'] == "all3":
            self.observation_space = spaces.Tuple((spaces.Box(low=0, high=100, shape=(15,), dtype=np.float16),
                                                  self.action_space ))
        elif env_config['observation_space'] == "default":
            self.observation_space = spaces.Tuple((spaces.Box(low=0, high=100, shape=(21,), dtype=np.float16),
                                                  self.action_space ))

        else:
            error.Error("Define Observation Space in env_config")

        print("i am setting configurations")
        # Set up all Configurations
        self.root_dir = os.path.dirname(os.path.realpath(__file__))
        self.config_file = '{}/models/sathorn-{}/sathorn_w_great2.sumo.cfg'.format(self.root_dir,env_config['time_select']) \
                           if (env_config['time_select'] == "morning" and env_config['great_edition']) \
                           else '{}/models/sathorn-{}/sathorn_w.sumo.cfg'.format(self.root_dir, env_config['time_select'])
        self.net_file = '{}/models/sathorn-{}/sathorn_w_fixed_20160404.net.xml'.format(self.root_dir, env_config['time_select'])
        self.edited_file = '{}/models/sathorn-{}/sathon_wide_tls_20160418_edited.add.xml'.format(self.root_dir, env_config['time_select'])
        self.view_file = '{}/gui-settings/gui-settings-file-loop.xml'.format(self.root_dir) if (env_config['viewport'] == "whole_loop") \
                         else '{}/gui-settings/gui-settings-file-surasak.xml'.format(self.root_dir)
        self.detector_file = '{}/detectors/sathorn_w_detectors.add.xml'.format(self.root_dir)
        
        self.begin_time = 21600 if (env_config['time_select'] == "morning") else 53100
        self.end_time   = 32400 if (env_config['time_select'] == "morning") else 69300
        self.seed = str(env_config['seed'])
        self.step_length = str(env_config['step_length'])
        self.impatience_time = str(env_config['impatience_time'])
        self.time_to_teleport = str(env_config['time_to_teleport'])
        self.no_internal_links = "true" if env_config['no_internal_links'] else "false"
        self.step_size = env_config['step_size']

        self.cell_capacities = np.array(cell_capacities_surasak + cell_capacities_charoenRat + cell_capacities_sathornS + cell_capacities_sathornN)
        
        # Libsumo doesn't have class 'trafficlights' but name class 'trafficlight' instead
        self._trafficlights = traci.trafficlight if WITH_LIBSUMO and not WITH_GUI else traci.trafficlights
        
        # Begin SUMO
        sumoBinary = sumolib.checkBinary('sumo-gui') if env_config['with_gui'] else sumolib.checkBinary('sumo')
        print("Loading Config File {}".format(self.config_file))
        print("Loading Edited File {}".format(self.edited_file))

        self.cmd = [sumoBinary, '-c', self.config_file,
                  '-a', '{},{}'.format(self.edited_file, self.detector_file),
##                 '-a', '{}'.format(self.edited_file),
                   '--no-internal-links', self.no_internal_links, 
                   '--time-to-teleport', self.time_to_teleport,
                   '--ignore-junction-blocker', '-1',
                   '--random', 'false',
                   '--seed', self.seed,
                   '--start','true',
                   '--eager-insert', 'true',
                   '--quit-on-end','true',
                   '--no-warnings', 'true',
                   '--step-length', self.step_length ,
                   '--gui-settings-file', self.view_file,
                   '--time-to-impatience', self.impatience_time ,
                   ]
        
        print("starting traci with command" , " ".join(self.cmd))
        traci.start(self.cmd)
        self._step = self.begin_time
        # Begin with action id of 1 
        self._action = 1
        self._setTrafficLights(self._action)

    def reset(self):
        """Resets the state of the environment and returns an initial observation.

        Returns: observation (object): the initial observation of the
            space.
        """
        traci.close()

        traci.start(self.cmd)
        self._step = self.begin_time
        # Begin with action id of 1 
        self._action = 1
        self._setTrafficLights(self._action)
        
        return (np.zeros(shape=(21,)), 1)

    
    def step(self, action):
        """Run one timestep of the environment's dynamics. When end of
        episode is reached, you are responsible for calling `reset()`

        Input:
            action (object): an action provided by the environment

        Returns:
            observation (object): agent's observation of the current environment
            reward (float) : amount of reward returned after previous action
            done (boolean): whether the episode has ended, in which case further step() calls will return undefined results
            info (dict): contains auxiliary diagnostic information (helpful for debugging, and sometimes learning)
        
        """
        # Make yellow lights at the beginning of the timestep if change traffic phase
        if action != self._action:
            self._setYellowLights(self._action, action)

        total_throughput = 0
        # 5 steps for yellow lights
        for _ in range(5):
            self._step += 1
            traci.simulationStep(step=self._step)
            total_throughput += self._getThroughput()
            
        # Change traffic phase after 5 seconds and set self._action to be equal to the action
        if action != self._action:
            self._setTrafficLights(action)
            self._action = action
        
        # need to step 1 at a time since induction loop requires addition
        for _ in range(self.step_size-5):
            self._step += 1
            traci.simulationStep(step=self._step)
            total_throughput += self._getThroughput()

        


        observation = self._getObservation()
        reward = self._getReward(total_throughput, observation[0][:-3]) #neglect downstream
        done = (self._step >= self.end_time)        # done if step is more than end time
        _cars_inside = np.dot(observation[0][:-3]/100, self.cell_capacities)
        info = {"Throughput": total_throughput,
                "Cars inside" : _cars_inside
                }

        if WITH_LIBSUMO and not WITH_GUI:
            print("Step {}/{} Reward: {} Throughput: {} Backlog: {}".format(self._step,
                                                                            self.end_time,
                                                                            int(reward),
                                                                            total_throughput,
                                                                            int(_cars_inside)),
                  end = '\r'
                  )
        return observation, reward, done, info
    
    def close(self):
        """Override _close in your subclass to perform any necessary cleanup.
        Environments will automatically close() themselves when
        garbage collected or when the program exits.
        """
        traci.close()

    def _getReward(self, throughput, occupancy):
        """Returns the reward given throughput and occupancy OF UPSTREAM"""
        
        return self.alpha*throughput - self.beta*np.dot(occupancy/100, self.cell_capacities)
        

    def _getThroughput(self):
        """Returns the throughput at the last time step from 4 upstream (incoming) lanes"""
        throughput = 0
        for edge in (edge_sathornN[0], edge_sathornS[0], edge_charoenRat[0], edge_surasak[0]):
            for lane in range(NUM_LANES[edge]):
                throughput += traci.inductionloop.getLastStepVehicleNumber("e1_{}_{}".format(edge, lane))
        return throughput

    
    def _getObservation(self):
        """Returns the observation at the current state
        
        Returns:
            ie. 'default' observation_space:
                a Tuple containing
                - the np.array of the occupancy of each cell in the order
                  North - South - East - West with cells closest to junction first
                - the action ID of the current action
            spaces.Tuple((spaces.Box(low=0, high=100, shape=(21,), dtype=np.float16),
                                                  self.action_space ))
            
        """
        # All occupancies
        occupancies = []

        occupancies.extend(self._getOccupancy(detector_surasak))
        occupancies.extend(self._getOccupancy(detector_charoenRat))
        occupancies.extend(self._getOccupancy(detector_sathornS))
        occupancies.extend(self._getOccupancy(detector_sathornN))

        occupancies.extend(self._getOccupancy(detector_surasak_down))
        occupancies.extend(self._getOccupancy(detector_sathornN_down))
        occupancies.extend(self._getOccupancy(detector_sathornS_down))

        return (np.array(occupancies), self._action)
        
            
    def _getOccupancy(self, detector_list):
        """Returns a list of weighted average occupancies for each cell over a detector list"""
        occupancies = []
        for cell_id, cell in enumerate(detector_list):
            # Occupancies over EACH edge
            edge_occupancies = []
            # Length of EACH edge (used for weighted sum)
            len_edges = []
            for edge, _ , _  in cell:
                # Average occupancy of ONE edge
                avg_edge_occupancy = []
                for lane in range(NUM_LANES[edge]):
                    # Note: occupancies are [0,100]
                    avg_edge_occupancy.append(traci.lanearea.getLastStepOccupancy("e2_{}_{}_{}".format(edge, lane, cell_id)))
                avg_edge_occupancy = np.mean(avg_edge_occupancy)

                edge_occupancies.append(avg_edge_occupancy)
                len_edges.append(LEN_EDGES[edge])
                
            occupancies.append(np.average(edge_occupancies, weights=len_edges))
        return occupancies
        
            
        

    def _setYellowLights(self, action_id_current, action_id_future):
        """ Wrapper of setting yellow state of Traffic lights

        'y' (yellow) if change from green 'g'/'G' to red 'r'  else current phase (i)
        """
        
        self._trafficlights.setRedYellowGreenState('cluster_46_47',
                                                   "".join(['y' if ((i=='G' or i=='g') and v == "r" ) else i \
                                                            for i,v in zip(self.action_map[action_id_current],
                                                                           self.action_map[action_id_future])]))

    def _setTrafficLights(self, action_id):
        """ Wrapper of setting state of Traffic lights"""
        self._trafficlights.setRedYellowGreenState('cluster_46_47', self.action_map[action_id])
