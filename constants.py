import os
# ALL CONSTANTS

"""Select Morning/Evening"""
TIME_SELECT   = 0       # 0 for Morning, 1 for Evening
GREAT_EDITION = True    # Great's Additional Flow (can only be true for morning)

"""Configure Simulation"""
WITH_GUI        = False
WITH_LIBSUMO         = True     # can only be true without GUI
LOOP_VIEW       = False      # see whole loop or only surasak view
STEP_LENGTH     = "1"       # seconds in step(); MUST BE <= 1 , see https://sourceforge.net/p/sumo/mailman/message/32876223/ 
SEED            = "20"
IMPATIENCE_TIME = "300"  # seconds to impatience -> driver use any gap even if other vehicle needs to brake(http://sumo.dlr.de/wiki/Definition_of_Vehicles,_Vehicle_Types,_and_Routes#Impatience)

"""Constants to use"""
STEP_SIZE = 5         # size to use
V_LENGTH = 4.62       # vehicle length
MIN_GAP  = 2.373      # minimum gap


########## Edges in Junction ##########
edge_sathornN = ("L239", "L249", "L232", "L10009", "L40412", "L40279", "L40523", "L40539")
edge_sathornS = ("L197#2", "L197#1", "L193#2", "L193#1", "L37", "L250", "L237", "L25")
edge_charoenRat = ("L40", "L570", "L565")
edge_surasak = ("L10189", "L10130", "L64", "L40404", "L40273", "L602", "L601")
edge_sathornN_down = ("L10150", )
edge_sathornS_down = ("L30", )
edge_surasak_down = ("L72", )
edges = edge_sathornN + edge_sathornS + edge_charoenRat + edge_surasak + edge_sathornN_down + edge_sathornS_down + edge_surasak_down

# Configure Processed Constants

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
TIME_SELECT_STR = ["morning", "evening"][TIME_SELECT]
CONFIG_FILE = '{}/models/sathorn-{}/sathorn_w_great2.sumo.cfg'.format(ROOT_DIR, TIME_SELECT_STR) \
                   if (TIME_SELECT_STR == "morning" and GREAT_EDITION) \
                   else '{}/models/sathorn-{}/sathorn_w.sumo.cfg'.format(ROOT_DIR, TIME_SELECT_STR)
NET_FILE = '{}/models/sathorn-{}/sathorn_w_fixed_20160404.net.xml'.format(ROOT_DIR, TIME_SELECT_STR)
EDITED_FILE = '{}/models/sathorn-{}/sathon_wide_tls_20160418_edited.add.xml'.format(ROOT_DIR, TIME_SELECT_STR)
VIEW_FILE = '{}/gui-settings/gui-settings-file-loop.xml'.format(ROOT_DIR) if (LOOP_VIEW) \
                 else '{}/gui-settings/gui-settings-file-surasak.xml'.format(ROOT_DIR)
DETECTOR_FILE = '{}/detectors/sathorn_w_detectors.add.xml'.format(ROOT_DIR)



