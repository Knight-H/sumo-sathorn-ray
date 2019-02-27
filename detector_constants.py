import pickle
import os, sys
import gc
# Imports 
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:   
    print("please declare environment variable 'SUMO_HOME'")
    sys.exit()
import sumolib

from constants import NET_FILE, edges, V_LENGTH, MIN_GAP

def pickle_generate():
    """Generate all pickle files necessary for detector variables""" 
    
    # Read net file
    net = sumolib.net.readNet(NET_FILE)

    ##### Length of all edges #####
    """
    LEN_EDGES is a dictionary where
           [edgeID] -> edge length
    """
    LEN_EDGES = {}
    
    ##### Total number of Lanes of Edges #####
    """
    NUM_LANES is a dictionary where
          [edgeID] -> no.# of lanes
    """
    NUM_LANES = {}
    for edge in edges:
        _edge = net.getEdge(edge)
        LEN_EDGES[edge] = _edge.getLength()
        NUM_LANES[edge] = _edge.getLaneNumber()

    with open(os.path.join('pickle', 'LEN_EDGES.pickle'), 'wb') as file:
        pickle.dump(LEN_EDGES, file, protocol=pickle.HIGHEST_PROTOCOL)
    with open(os.path.join('pickle', 'NUM_LANES.pickle'), 'wb') as file:
        pickle.dump(NUM_LANES, file, protocol=pickle.HIGHEST_PROTOCOL)


    ########## Detectors upstream in to Junction ##########
    """
    Each cell is defined as a tuple of (EDGE_ID, starting_position, ending_position)
    Note that this will be converted to position and length later
    """
    detector_sathornN = (
            (("L239", 0, LEN_EDGES["L239"]),),         # W0
            (("L249", 0, LEN_EDGES["L249"]),
             ("L232", 0, LEN_EDGES["L232"]),),         # W1
            (("L10009", 0, LEN_EDGES["L10009"]),),     # W2
            (("L40412", 0, LEN_EDGES["L40412"]),
             ("L40279", 0, LEN_EDGES["L40279"]),
             ("L40523", 0, LEN_EDGES["L40523"]),),     # W3
            (("L40539", 0, LEN_EDGES["L40539"]),)      # W4
        )
    detector_sathornS = (
            (("L197#2", 0, 30),),                      # E0
            (("L197#2", 30, LEN_EDGES["L197#2"]),
             ("L197#1", 0, LEN_EDGES["L197#1"]),
             ("L193#2", 0, LEN_EDGES["L193#2"]),),     # E1
            (("L193#1", 0, LEN_EDGES["L193#1"]),
             ("L37", 0, LEN_EDGES["L37"]),
             ("L250", 0, LEN_EDGES["L250"]),),         # E2
            (("L237", 0, LEN_EDGES["L237"]),
             ("L25", 0, LEN_EDGES["L25"]),)            # E3
        )
    detector_charoenRat = (
            (("L40", 0, 30),),                   # S0 
            (("L40", 30, 200),),                 # S1
            (("L40", 200, LEN_EDGES["L40"]),),   # S2
            (("L570", 0, LEN_EDGES["L570"]),
             ("L565", 0 , LEN_EDGES["L565"]),)   # S3
        )
    detector_surasak = (
            (("L10189", 0, 30),),                      # N0
            (("L10189", 30, LEN_EDGES["L10189"]),),    # N1
            (("L10130", 0, LEN_EDGES["L10130"]),),     # N2
            (("L64", 0, LEN_EDGES["L64"]),),           # N3
            (("L40404", 0, LEN_EDGES["L40404"]),
             ("L40273", 0, LEN_EDGES["L40273"]),
             ("L602", 0, LEN_EDGES["L602"]),
             ("L601", 0, LEN_EDGES["L601"]),)          # N4
        )

    ########## Detectors downstream out of Junction ##########


    detector_sathornN_down = (
            (("L10150", LEN_EDGES["L10150"]-50, LEN_EDGES["L10150"]),),
        )
    detector_sathornS_down = (
            (("L30", LEN_EDGES["L30"]-50, LEN_EDGES["L30"]),),
        )

    detector_surasak_down = (
            (("L72", LEN_EDGES["L72"]-50, LEN_EDGES["L72"]),),
        )


    # Changing to format ( EDGE_ID , POS, LENGTH )

    def detector_format(detector_list):
        detector_list = list(detector_list)
        for i, cell in enumerate(detector_list):
            detector_list[i] = list(detector_list[i])
            for j, detector in enumerate(cell):
                edge_id, starting_pos, ending_pos = detector
                detector_list[i][j] = (edge_id,                       #edge_id
                                       round(LEN_EDGES[edge_id]-ending_pos, 2), #pos
                                       round(ending_pos-starting_pos,2) )       #length
            detector_list[i] = tuple(detector_list[i])
        return tuple(detector_list)

    # Return all names of the detector in an edge
    def detector_name(detector_list):
        name_list = []
        for cell_id, cell in enumerate(detector_list):
            for edge, pos, length in cell:
                for lane in range(NUM_LANES[edge]):
                    name_list.append("e2_{}_{}_{}".format(edge, lane, cell_id))
        return name_list

    detector_sathornN = detector_format(detector_sathornN)
    detector_sathornS = detector_format(detector_sathornS)
    detector_charoenRat = detector_format(detector_charoenRat)
    detector_surasak = detector_format(detector_surasak)

    detector_sathornN_down = detector_format(detector_sathornN_down)
    detector_sathornS_down = detector_format(detector_sathornS_down)
    detector_surasak_down = detector_format(detector_surasak_down)

    detectors = detector_sathornN + detector_sathornS + detector_charoenRat + detector_surasak
    detectors_down = detector_sathornN_down + detector_sathornS_down + detector_surasak_down

    PICKLE_detector= {
            "detector_sathornN" : detector_sathornN,
            "detector_sathornS" : detector_sathornS,
            "detector_charoenRat" : detector_charoenRat,
            "detector_surasak" : detector_surasak,

            "detector_sathornN_down" : detector_sathornN_down,
            "detector_sathornS_down" : detector_sathornS_down,
            "detector_surasak_down"  : detector_surasak_down,

            "detectors" : detectors,
            "detectors_down" : detectors_down,
        }
    with open(os.path.join('pickle', 'detector.pickle'), 'wb') as file:
        pickle.dump(PICKLE_detector, file, protocol=pickle.HIGHEST_PROTOCOL)

    detector_names_sathornN = detector_name(detector_sathornN)
    detector_names_sathornS = detector_name(detector_sathornS)
    detector_names_charoenRat = detector_name(detector_charoenRat)
    detector_names_surasak = detector_name(detector_surasak)

    detector_names_sathornN_down = detector_name(detector_sathornN_down)
    detector_names_sathornS_down = detector_name(detector_sathornS_down)
    detector_names_surasak_down = detector_name(detector_surasak_down)

    PICKLE_detector_names= {
            "detector_names_sathornN" : detector_names_sathornN,
            "detector_names_sathornS" : detector_names_sathornS,
            "detector_names_charoenRat" : detector_names_charoenRat,
            "detector_names_surasak" : detector_names_surasak,

            "detector_names_sathornN_down" : detector_names_sathornN_down,
            "detector_names_sathornS_down" : detector_names_sathornS_down,
            "detector_names_surasak_down"  : detector_names_surasak_down,

        }
    
    with open(os.path.join('pickle', 'detector_names.pickle'), 'wb') as file:
        pickle.dump(PICKLE_detector_names, file, protocol=pickle.HIGHEST_PROTOCOL)

    # Return the cell capacities of a detector list
    # ACTUALLY NEED MAX CELL CAPACITY for the occupancy since no minGAP!!!
    def cell_capacities(detector_list):
        capacities = []
        for cell in detector_list:
            cell_capacity = 0
            for edge, _, _ in cell:
                cell_capacity += LEN_EDGES[edge]*NUM_LANES[edge]/(V_LENGTH)
            capacities.append(cell_capacity)
        return capacities
    cell_capacities_sathornN = cell_capacities(detector_sathornN)
    cell_capacities_sathornS = cell_capacities(detector_sathornS)
    cell_capacities_charoenRat = cell_capacities(detector_charoenRat)
    cell_capacities_surasak = cell_capacities(detector_surasak)
    print("cell_capacities of sathorn N:", cell_capacities_sathornN)
    
    PICKLE_cell_capacities = {
            "cell_capacities_sathornN": cell_capacities_sathornN,
            "cell_capacities_sathornS": cell_capacities_sathornS,
            "cell_capacities_charoenRat": cell_capacities_charoenRat,
            "cell_capacities_surasak" : cell_capacities_surasak,
        }
    with open(os.path.join('pickle', 'cell_capacities.pickle'), 'wb') as file:
        pickle.dump(PICKLE_cell_capacities, file, protocol=pickle.HIGHEST_PROTOCOL)

    
if __name__ == "__main__":
    print("Running in main, generating pickles...")
    pickle_generate()
else:
    print("detector_constants.py in module, loading pickles...")
    
    with open(os.path.join('pickle', 'LEN_EDGES.pickle'), 'rb') as file:
        LEN_EDGES = pickle.load(file)
    with open(os.path.join('pickle', 'NUM_LANES.pickle'), 'rb') as file:
        NUM_LANES = pickle.load(file)
    with open(os.path.join('pickle', 'detector.pickle'), 'rb') as file:
        PICKLE_detector = pickle.load(file)

        detector_sathornN = PICKLE_detector['detector_sathornN']
        detector_sathornS = PICKLE_detector['detector_sathornS']
        detector_charoenRat = PICKLE_detector['detector_charoenRat']
        detector_surasak = PICKLE_detector['detector_surasak']

        detector_sathornN_down = PICKLE_detector['detector_sathornN_down']
        detector_sathornS_down = PICKLE_detector['detector_sathornS_down']
        detector_surasak_down = PICKLE_detector['detector_surasak_down']

        detectors = PICKLE_detector['detectors']
        detectors_down = PICKLE_detector['detectors_down']
        del PICKLE_detector
    with open(os.path.join('pickle', 'detector_names.pickle'), 'rb') as file:
        PICKLE_detector_names = pickle.load(file)

        detector_names_sathornN = PICKLE_detector_names['detector_names_sathornN']
        detector_names_sathornS =  PICKLE_detector_names['detector_names_sathornS']
        detector_names_charoenRat = PICKLE_detector_names['detector_names_charoenRat']
        detector_names_surasak = PICKLE_detector_names['detector_names_surasak']

        detector_names_sathornN_down = PICKLE_detector_names['detector_names_sathornN_down']
        detector_names_sathornS_down = PICKLE_detector_names['detector_names_sathornS_down']
        detector_names_surasak_down = PICKLE_detector_names['detector_names_surasak_down']
        del PICKLE_detector_names
    with open(os.path.join('pickle', 'cell_capacities.pickle'), 'rb') as file:
        PICKLE_cell_capacities = pickle.load(file)

        cell_capacities_sathornN = PICKLE_cell_capacities['cell_capacities_sathornN']
        cell_capacities_sathornS = PICKLE_cell_capacities['cell_capacities_sathornS']
        cell_capacities_charoenRat = PICKLE_cell_capacities['cell_capacities_charoenRat']
        cell_capacities_surasak = PICKLE_cell_capacities['cell_capacities_surasak']
        del PICKLE_cell_capacities
        
    gc.collect()

        
    
