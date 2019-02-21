import pickle
import os
import numpy as np
from util import _calculate_avg_green_time


_LOG_DIR = os.path.join(os.path.expanduser('~'), "ray_results")
_CELL_ORDER = ("surasak_0", "surasak_1", "surasak_2", "surasak_3", "surasak_4",
               "charoenRat_0", "charoenRat_1", "charoenRat_2", "charoenRat_3",
               "sathornS_0", "sathornS_1", "sathornS_2", "sathornS_3",
               "sathornN_0", "sathornN_1", "sathornN_2", "sathornN_3", "sathornN_4"
               )
_TRAVEL_TIMES = ("travel_time_171", "travel_time_172", "travel_time_173")
_JAM_LENGTHS = ("jam_length_surasak", "jam_length_charoenRat", "jam_length_sathornS", "jam_length_sathornN")

_temp_episode = {}  # since episode is not passed to on_result

def _reset_episode_user_data(episode):
    for i, cell in enumerate(_CELL_ORDER):
        episode.user_data["cell_occupancy_{}".format(cell)] = []
    episode.user_data["action"] = []
    for travel_time in _TRAVEL_TIMES:
        episode.user_data[travel_time] = []
    episode.user_data["total_throughput"] = []
    episode.user_data["backlog"] = []
    for jam_length in _JAM_LENGTHS:
        episode.user_data[jam_length] = []


def _log_episode_user_data(episode):
##    print("this is epi length", episode.length)
    if episode.length == 0:
        return
    _observation = episode.last_observation_for()
    _info = episode.last_info_for()

    for i, cell in enumerate(_CELL_ORDER):
        episode.user_data["cell_occupancy_{}".format(cell)].append(_observation[i])
    episode.user_data["action"].append(episode.last_action_for())
    for travel_time in _TRAVEL_TIMES:
        episode.user_data[travel_time].append(_info[travel_time])
    episode.user_data["total_throughput"].append(_info['total_throughput'])
    episode.user_data["backlog"].append(_info['backlog'])
    for jam_length in _JAM_LENGTHS:
        episode.user_data[jam_length].append(_info[jam_length])
    

def on_episode_start(info):
    episode = info["episode"]
    print("episode {} started".format(episode.episode_id))
    _reset_episode_user_data(episode)
    
def on_episode_step(info):
    ## Logging in user_data:
    ##    - Actions
    ##    - Travel Time for route171, 172, 173
    ##    - total_throughput
    ##    - backlog (from cell_occupancy)
    ##    - jam length
    episode = info["episode"]
    _log_episode_user_data(episode)
    
def on_episode_end(info):
    episode = info["episode"]
    _info = episode.last_info_for()

    for i, cell in enumerate(_CELL_ORDER):
        _temp_episode["cell_occupancy_{}".format(cell)] = episode.user_data["cell_occupancy_{}".format(cell)].copy()
    _temp_episode["action"] = episode.user_data["action"].copy()
    for travel_time in _TRAVEL_TIMES:
        _temp_episode[travel_time] = episode.user_data[travel_time]
    _temp_episode["total_throughput"] = episode.user_data["total_throughput"]
    _temp_episode["backlog"] = episode.user_data["backlog"]
    for jam_length in _JAM_LENGTHS:
        _temp_episode[jam_length] = episode.user_data[jam_length].copy()
    _temp_episode['name'] = _info['name']
    
    _reset_episode_user_data(episode)
    
    # Can write custom metrics. Will give mean, max, min
##    episode.custom_metrics["custom_result_on_end"] = 7.777
    print("episode {} ended with length {}".format(episode.episode_id, episode.length))
    
    
def on_sample_end(info):
    pass
##    print("returned sample batch of size {}".format(info["samples"].count))

def on_train_result(info):
    # write all user_data to pickle
    # reset all user_data
    _result = info["result"] # you can mutate the result dict to add new fields to return, which int32 and float32 will be handled by _TFLogger

    episode = _temp_episode
    print("Episode User Data on end ", _temp_episode)
    
    EPISODE_NO = _result["episodes_total"]
    print("Ended Episode Number: ", EPISODE_NO)
    
    print(" Writing pickle .. ")
    # Directory for pickles
    _DIR_TO_WRITE = os.path.join(_LOG_DIR, _temp_episode['name'], 'pickle')
    if not os.path.exists(_DIR_TO_WRITE):
        os.makedirs(_DIR_TO_WRITE)

    # --- Occupancy ----
    for i, cell in enumerate(_CELL_ORDER):
        _occupancies = np.array(_temp_episode["cell_occupancy_{}".format(cell)], dtype = np.float16)
        _result["cell_occupancy_{}".format(cell)] = np.mean(_occupancies, dtype=np.float32) # else no log
        with open(os.path.join(_DIR_TO_WRITE, 'ep{}_cell_occupancy_{}.pickle'.format(EPISODE_NO, cell)), 'wb') as f:
            pickle.dump(_occupancies, f, pickle.HIGHEST_PROTOCOL)

    # --- Action ---
    # Action List will not log in _TFLogger, so need custom logger
    _result["actions"] = _temp_episode["action"]
    with open(os.path.join(_DIR_TO_WRITE, 'ep{}_actions.pickle'.format(EPISODE_NO)), 'wb') as f:
        pickle.dump(_temp_episode["action"], f, pickle.HIGHEST_PROTOCOL)

    _phase_dict = _calculate_avg_green_time(_temp_episode["action"], 10 ,5)
    for i in range(9): # action space, can also get from env
        _result["green_time_avg_{}".format(i)] = _phase_dict[i][0]
        _result["green_time_std_{}".format(i)] = _phase_dict[i][1]

    # --- Travel Time ---
    for travel_time in _TRAVEL_TIMES:
        _result[travel_time] = np.mean(_temp_episode[travel_time], dtype=np.float32)
        with open(os.path.join(_DIR_TO_WRITE, 'ep{}_{}.pickle'.format(EPISODE_NO, travel_time)), 'wb') as f:
            pickle.dump(_temp_episode[travel_time], f, pickle.HIGHEST_PROTOCOL)

    # --- Total Throughput ---                                 
    _result["total_throughput"] = np.mean(_temp_episode["total_throughput"], dtype=np.float32)
    with open(os.path.join(_DIR_TO_WRITE, 'ep{}_total_throughput.pickle'.format(EPISODE_NO)), 'wb') as f:
        pickle.dump(_temp_episode["total_throughput"], f, pickle.HIGHEST_PROTOCOL)

    # --- Backlog --- 
    _result["backlog"] = np.mean(_temp_episode["backlog"], dtype=np.float32)
    with open(os.path.join(_DIR_TO_WRITE, 'ep{}_total_throughput.pickle'.format(EPISODE_NO)), 'wb') as f:
        pickle.dump(_temp_episode["backlog"], f, pickle.HIGHEST_PROTOCOL)

    # --- Jam Length ---
    for jam_length in _JAM_LENGTHS:
        _result[jam_length] = np.mean(_temp_episode[jam_length], dtype=np.float32)
        with open(os.path.join(_DIR_TO_WRITE, 'ep{}_{}.pickle'.format(EPISODE_NO, jam_length)), 'wb') as f:
            pickle.dump(_temp_episode[jam_length], f, pickle.HIGHEST_PROTOCOL)
    
