import pickle
import os
import numpy as np
from util import _calculate_avg_green_time
import tensorflow as tf
from datetime import datetime
from ActionLogger import create_HistogramProto

_LOG_DIR = os.path.join(os.path.expanduser('~'), "ray_results")
_CELL_ORDER = ("surasak_0", "surasak_1", "surasak_2", "surasak_3", "surasak_4",
               "charoenRat_0", "charoenRat_1", "charoenRat_2", "charoenRat_3",
               "sathornS_0", "sathornS_1", "sathornS_2", "sathornS_3",
               "sathornN_0", "sathornN_1", "sathornN_2", "sathornN_3", "sathornN_4",
               "surasak_down", "sathornN_down", "sathornS_down"
               )
_TRAVEL_TIMES = ("travel_time_171", "travel_time_172", "travel_time_173")
_JAM_LENGTHS = ("jam_length_surasak", "jam_length_charoenRat", "jam_length_sathornS", "jam_length_sathornN")
_MEAN_SPEEDS = ("mean_speed_surasak", "mean_speed_charoenRat", "mean_speed_sathornS", "mean_speed_sathornN")
_WAITING_TIMES = ("waiting_time_surasak", "waiting_time_charoenRat", "waiting_time_sathornS", "waiting_time_sathornN")

def _reset_episode_user_data(episode):
    for i, cell in enumerate(_CELL_ORDER):
        episode.user_data["cell_occupancy_{}".format(cell)] = []
    episode.user_data["action"] = []
    episode.user_data["total_throughput"] = []
    episode.user_data["weighted_occupancy"] = []
    for travel_time in _TRAVEL_TIMES:
        episode.user_data[travel_time] = []
    for jam_length in _JAM_LENGTHS:
        episode.user_data[jam_length] = []
    for mean_speed in _MEAN_SPEEDS:
        episode.user_data[mean_speed] = []
    for waiting_time in _WAITING_TIMES:
        episode.user_data[waiting_time] = []

def _log_episode_user_data(episode):
##    print("this is epi length", episode.length)
    if episode.length == 0:
        return
    _observation = episode.last_observation_for()
    _info = episode.last_info_for()
##    print("this is in episode.length ", episode.length)
##    print(_info)

    for i, cell in enumerate(_CELL_ORDER):
        episode.user_data["cell_occupancy_{}".format(cell)].append(_observation[i])
##    episode.user_data["action"].append(episode.last_action_for())
##    print(_observation[-9:], " which is ", np.where(_observation[-9:])[0][0])
    #using obs one-hot encoding
    episode.user_data["action"].append(np.where(_observation[-9:])[0][0])
    episode.user_data["total_throughput"].append(_info['total_throughput'])
    episode.user_data["weighted_occupancy"].append(_info['weighted_occupancy'])
    for travel_time in _TRAVEL_TIMES:
        episode.user_data[travel_time].append(int(_info[travel_time]))
##        print(travel_time ," : ", _info[travel_time])
    for jam_length in _JAM_LENGTHS:
        episode.user_data[jam_length].append(_info[jam_length])
    for mean_speed in _MEAN_SPEEDS:
        episode.user_data[mean_speed].append(_info[mean_speed])
    for waiting_time in _WAITING_TIMES:
        episode.user_data[waiting_time].append(_info[waiting_time])
    
def on_episode_start(info):
    episode = info["episode"]
    print("episode {} started".format(episode.episode_id))
    _reset_episode_user_data(episode)
    _info = episode.last_info_for()
    # Directory for pickles
    _DIR_TO_WRITE = os.path.join(_LOG_DIR, _info['name'], 'pickle')
    if not os.path.exists(_DIR_TO_WRITE):
        os.makedirs(_DIR_TO_WRITE)
    # Check whether written graph yet
    _GRAPH_PICKLE = os.path.join(_DIR_TO_WRITE, 'isGraph.pickle')
    if not os.path.exists(_GRAPH_PICKLE):
        with open(_GRAPH_PICKLE, 'wb') as f:
            pickle.dump(False, f, pickle.HIGHEST_PROTOCOL)
        
    
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
    _ID = episode.episode_id

    _TIME_NOW = datetime.now().strftime("%Y-%m-%dT%H.%M.%S")
    
    print(" Writing pickle .. ")
    

    _AGGREGATE_PICKLE = {}

    # --- Occupancy ----
    for i, cell in enumerate(_CELL_ORDER):
        _occupancies = np.array(episode.user_data["cell_occupancy_{}".format(cell)], dtype = np.float16)
        episode.custom_metrics["cell_occupancy_{}".format(cell)] = np.mean(_occupancies, dtype=np.float16)
        
        _AGGREGATE_PICKLE["cell_occupancy_{}".format(cell)] = _occupancies

        
##        with open(os.path.join(_DIR_TO_WRITE, '{}-ep{}_cell_occupancy_{}.pickle'.format(_TIME_NOW,_ID, cell)), 'wb') as f:
##            pickle.dump(_occupancies, f, pickle.HIGHEST_PROTOCOL)

    # --- Action ---
    # Action List will not log in _TFLogger, so need custom logger
##    episode.custom_metrics["actions"] = np.array(episode.user_data["action"], dtype=np.uint8)
    _actions = np.array(episode.user_data["action"], dtype=np.uint8)

    _AGGREGATE_PICKLE["actions"] = _actions
    
##    with open(os.path.join(_DIR_TO_WRITE, '{}-ep{}_actions.pickle'.format(_TIME_NOW,_ID)), 'wb') as f:
##        pickle.dump(_actions, f, pickle.HIGHEST_PROTOCOL)

    _phase_dict = _calculate_avg_green_time(_actions, 10 ,5)
    for i in range(9): # action space, can also get from env
        episode.custom_metrics["green_time_avg_{}".format(i)] = _phase_dict[i][0]
        episode.custom_metrics["green_time_std_{}".format(i)] = _phase_dict[i][1]

    # --- Travel Time ---
    for travel_time in _TRAVEL_TIMES:
        episode.custom_metrics[travel_time] = np.mean(episode.user_data[travel_time], dtype=np.uint32)

        _AGGREGATE_PICKLE[travel_time] = np.array(episode.user_data[travel_time], dtype=np.uint32)
        
##        with open(os.path.join(_DIR_TO_WRITE, '{}-ep{}_{}.pickle'.format(_TIME_NOW,_ID, travel_time)), 'wb') as f:
##            pickle.dump(np.array(episode.user_data[travel_time], dtype=np.float16), f, pickle.HIGHEST_PROTOCOL)

    # --- Total Throughput ---                                 
    episode.custom_metrics["total_throughput"] = np.mean(episode.user_data["total_throughput"], dtype=np.uint16)

    _AGGREGATE_PICKLE["total_throughput"] = np.array(episode.user_data["total_throughput"], dtype=np.uint16)
    
##    with open(os.path.join(_DIR_TO_WRITE, '{}-ep{}_total_throughput.pickle'.format(_TIME_NOW,_ID)), 'wb') as f:
##        pickle.dump(np.array(episode.user_data["total_throughput"], dtype=np.uint8), f, pickle.HIGHEST_PROTOCOL)

    # --- Weighted Occupancy --- 
    episode.custom_metrics["weighted_occupancy"] = np.mean(episode.user_data["weighted_occupancy"], dtype=np.uint16)

    _AGGREGATE_PICKLE["weighted_occupancy"] = np.array(episode.user_data["weighted_occupancy"], dtype=np.uint16)
##    with open(os.path.join(_DIR_TO_WRITE, '{}-ep{}_weighted_occupancy.pickle'.format(_TIME_NOW,_ID)), 'wb') as f:
##        pickle.dump(np.array(episode.user_data["weighted_occupancy"], dtype=np.float16), f, pickle.HIGHEST_PROTOCOL)

    # --- Jam Length ---
    for jam_length in _JAM_LENGTHS:
        episode.custom_metrics[jam_length] = np.mean(episode.user_data[jam_length], dtype=np.uint16)
        _AGGREGATE_PICKLE[jam_length] = np.array(episode.user_data[jam_length], dtype=np.uint16)
##        with open(os.path.join(_DIR_TO_WRITE, '{}-ep{}_{}.pickle'.format(_TIME_NOW,_ID, jam_length)), 'wb') as f:
##            pickle.dump(np.array(episode.user_data[jam_length], dtype=np.float16), f, pickle.HIGHEST_PROTOCOL)
    # --- Mean Speed ---
    for mean_speed in _MEAN_SPEEDS:
        episode.custom_metrics[mean_speed] = np.mean(episode.user_data[mean_speed], dtype=np.float32)
        _AGGREGATE_PICKLE[mean_speed] = np.array(episode.user_data[mean_speed], dtype=np.float32)
##        with open(os.path.join(_DIR_TO_WRITE, '{}-ep{}_{}.pickle'.format(_TIME_NOW,_ID, mean_speed)), 'wb') as f:
##            pickle.dump(np.array(episode.user_data[mean_speed], dtype=np.float16), f, pickle.HIGHEST_PROTOCOL)
            
    # --- Waiting Time ---
    for waiting_time in _WAITING_TIMES:
        episode.custom_metrics[waiting_time] = np.mean(episode.user_data[waiting_time], dtype=np.uint32)
        _AGGREGATE_PICKLE[waiting_time] = np.array(episode.user_data[waiting_time], dtype=np.uint32)
##        with open(os.path.join(_DIR_TO_WRITE, '{}-ep{}_{}.pickle'.format(_TIME_NOW,_ID, waiting_time)), 'wb') as f:
##            pickle.dump(np.array(episode.user_data[waiting_time], dtype=np.float16), f, pickle.HIGHEST_PROTOCOL)

    with open(os.path.join(_DIR_TO_WRITE, '{}-ep{}.pickle'.format(_TIME_NOW,_ID)), 'wb') as f:
        pickle.dump(_AGGREGATE_PICKLE, f, pickle.HIGHEST_PROTOCOL)


##    print("This is episode.user_data on end ", episode.user_data)
    
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
    _agent = info["agent"]

##    print(_result['custom_metrics'])

    EPISODE_NO = _result["episodes_total"]
    print("Ended Episode Total: ", EPISODE_NO)


    with open(_GRAPH_PICKLE, 'wb') as f:
        _IS_GRAPH = pickle.load(f)
            
    # --- Policy Graph ----
    if _result['custom_metrics'] and not _IS_GRAPH:
        print("I am writing agent in ", _agent._result_logger.logdir)
        policy_graph = _agent.local_evaluator.policy_map["default"].sess.graph
        writer = tf.summary.FileWriter(_agent._result_logger.logdir, policy_graph)
        
        t = _result.get("timesteps_total") or _result["training_iteration"]

        # Write actions
    ##    print(" This is actions ", _result['custom_metrics']['actions'])
    ##    actions = _result['custom_metrics']['actions']
    ##    _hist = create_HistogramProto(np.array(actions), bins=9)
    ##    action_stats = tf.Summary(value = [tf.Summary.Value(tag="actions", histo=_hist)])
    ##    writer.add_summary(action_stats, t)

        # Flush a lot before Segmentation Fault
    ##    writer.flush()

    ##    _green_times = _calculate_green_time(actions, 10 ,5)
    ##    for phase in _green_times:
    ##        _hist = create_HistogramProto(np.array(_green_times[phase]), bins=15)
    ##        action_stats = tf.Summary(value = [tf.Summary.Value(tag="action_green_time_{}".format(phase), histo=_hist)])
    ##        writer.add_summary(action_stats, t)
    ##
    ##        # Flush a lot before Segmentation Fault
    ##        if phase%3 == 0 and phase != 0:
    ##            writer.flush()

        writer.flush()

        
        writer.close()

        with open(_GRAPH_PICKLE, 'wb') as f:
            pickle.dump(True, f, pickle.HIGHEST_PROTOCOL)

