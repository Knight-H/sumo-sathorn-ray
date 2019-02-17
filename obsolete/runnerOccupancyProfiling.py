from constants import *

if LIBSUMO and not WITH_GUI: import libsumo as traci
else: import traci

from plotHelper import *

# Main Function
def main():
    step = float(BEGIN_TIME)

    SIMULATION_STEPS = (END_TIME-BEGIN_TIME)//5 + 1  # 1 for the beginning step
    print()
    
    while step < END_TIME:
        #break
        if step%3600 == 0:
            print("Current Time: {}:00".format(step//3600))

        for edge in edge_charoenRat:
            for lane in range(0,NUM_LANES[edge]):
                print("{}: {}".format(lane, traci.lanearea.getLastStepOccupancy("e2_{}_{}_0".format(edge,lane))))
        
        traci.simulationStep(step=step)
        step += STEP_SIZE
        
    
    
    print(step)
    traci.close()


if __name__ == "__main__":
    sumoBinary = 'sumo-gui' if WITH_GUI else 'sumo'
    print("Loading Config File {}".format(CONFIG_FILE))
    print("Loading Add File {}".format(EDITED_FILE))
    
    traci.start([sumoBinary, '-c', CONFIG_FILE,
                   '-a', '{},{}'.format(EDITED_FILE, DETECTOR_FILE),
                   '--time-to-teleport', '-1',
                   #'--no-internal-links', 'true',  #invisible cars
                   '--ignore-junction-blocker', '-1', #doesn't really matter
                   #'--collision.action', 'none',
                   #'--collision.check-junctions', 'true',
                   #'--collision.stoptime', '15',
                   #'--collision.mingap-factor', '0.2',
                   '--random', 'false',
                   '--seed', SEED,
                   '--start','true',
                   '--quit-on-end','true',
                   '--no-warnings', 'true',
                   '--eager-insert', 'true',
                   '--step-length', STEP_LENGTH,
                   '--gui-settings-file', VIEW_FILE,
                   '--time-to-impatience', IMPATIENCE_TIME,
                   ])
    main()
    
    
