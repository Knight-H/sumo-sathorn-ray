import numpy as np
import warnings

def _calculate_green_time(action_list, step_length, yellow_duration):
    """Calculate the green time for each phase

    Input:
        list of actions ie. [1, 1, 2, 3, 4, 5, 0 , 1... ]

    Ouput:
        Dictionary of [phase] -> [array of green times]
    """
    _PHASE_DICT = {i:[] for i in range(9)}
    
    subseq = 1
    current_action = action_list[0]
    for i in range(len(action_list)-1):
        if action_list[i] == action_list[i+1]:
            subseq += 1
        else:
            # subseq    is total number of states with that action
            # step_length   for the step_length
            # yellow_duration        for the yellow time
            _PHASE_DICT[current_action].append(subseq*step_length-yellow_duration)
            subseq = 1
            current_action = action_list[i+1]
    # After the last step, 
    _PHASE_DICT[current_action].append(subseq*step_length-yellow_duration)
    
    return _PHASE_DICT
    

def _calculate_avg_green_time(action_list, step_length, yellow_duration):
    """Calculate the average green time for each phase

    Input:
        list of actions ie. [1, 1, 2, 3, 4, 5, 0 , 1... ]

    Ouput:
        Dictionary of [phase] -> (mean duration, std dev)
    """
    _PHASE_DICT = _calculate_green_time(action_list, step_length, yellow_duration)

    for action in _PHASE_DICT:
        # return (mean duration, std) if has data, (-1, -1) if no data
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            _PHASE_DICT[action] = np.array((np.mean(_PHASE_DICT[action]),np.std(_PHASE_DICT[action])), dtype=np.float32)
        if np.isnan(_PHASE_DICT[action][0]) or np.isnan(_PHASE_DICT[action][1]):
            _PHASE_DICT[action] = (-1, -1)
    
    return _PHASE_DICT
