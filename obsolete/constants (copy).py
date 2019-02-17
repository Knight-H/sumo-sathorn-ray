import os, sys
# Imports 
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:   
    print("please declare environment variable 'SUMO_HOME'")
    sys.exit()
import sumolib


# ALL CONSTANTS

"""Select Morning/Evening"""
TIME_SELECT   = 0       # 0 for Morning, 1 for Evening
GREAT_EDITION = True    # Great's Additional Flow (can only be true for morning)

"""Configure Simulation"""
WITH_GUI        = True
LIBSUMO         = False     # can only be true without GUI
LOOP_VIEW       = False      # see whole loop or only surasak view
STEP_LENGTH     = "1"       # seconds in step(); MUST BE <= 1 , see https://sourceforge.net/p/sumo/mailman/message/32876223/ 
SEED            = "20"
IMPATIENCE_TIME = "300"  # seconds to impatience -> driver use any gap even if other vehicle needs to brake(http://sumo.dlr.de/wiki/Definition_of_Vehicles,_Vehicle_Types,_and_Routes#Impatience)

"""Constants to use"""
STEP_SIZE = 5         # size to use
V_LENGTH = 4.62       # vehicle length
MIN_GAP  = 2.373      # minimum gap

#  Configure Constants Here

TIME_SELECT_STR = ("sathorn-morning", "sathorn-evening")[TIME_SELECT]
CONFIG_FILE = './models/{}/sathorn_w_great2.sumo.cfg'.format(TIME_SELECT_STR) if (TIME_SELECT==0 and GREAT_EDITION) else './models/{}/sathorn_w.sumo.cfg'.format(TIME_SELECT_STR)
##CONFIG_FILE = './models/{}/sathorn_w_great_edit_knight.sumo.cfg'.format(TIME_SELECT_STR)
NET_FILE = './models/{}/sathorn_w_fixed_20160404.net.xml'.format(TIME_SELECT_STR)
EDITED_FILE = './models/{}/sathon_wide_tls_20160418_edited.add.xml'.format(TIME_SELECT_STR)
VIEW_FILE = './gui-settings/gui-settings-file-loop.xml' if LOOP_VIEW else './gui-settings/gui-settings-file-surasak.xml'
#VIEW_FILE = './gui-settings/gui-settings-file-nara.xml'
DETECTOR_FILE = './detectors/sathorn_w_detectors.add.xml'

BEGIN_TIME = 21600 if (TIME_SELECT == 0) else 53100
END_TIME   = 32400 if (TIME_SELECT == 0) else 69300


########## Edges in Junction ##########
edge_sathornN = ("L239", "L249", "L232", "L10009", "L40412", "L40279", "L40523", "L40539")
edge_sathornS = ("L197#2", "L197#1", "L193#2", "L193#1", "L37", "L250", "L237", "L25")
edge_charoenRat = ("L40", "L570", "L565")
edge_surasak = ("L10189", "L10130", "L64", "L40404", "L40273", "L602", "L601")
edges = edge_sathornN + edge_sathornS + edge_charoenRat + edge_surasak

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


########## Detectors in Junction ##########
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
detectors = (detector_sathornN, detector_sathornS, detector_charoenRat, detector_surasak)

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

# Print out all names of the detector in an edge

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

detector_names_sathornN = detector_name(detector_sathornN)
detector_names_sathornS = detector_name(detector_sathornS)
detector_names_charoenRat = detector_name(detector_charoenRat)
detector_names_surasak = detector_name(detector_surasak)
