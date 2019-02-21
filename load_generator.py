import os
import numpy as np

def main():
    LOADS = np.arange(0.0,10.1, 0.5)

    _CONTENT = None
    # Line number that contain these routes in load1
    _ROUTE_171 = (571, 572, 723, 799, 800)
    _ROUTE_172 = (490, 499)
    _ROUTE_173 = (341, 416)
    _ROUTES = _ROUTE_171 + _ROUTE_172 + _ROUTE_173
    
    with open(os.path.join('models', 'sathorn-morning', 'Great-route', 'sathorn_w_20160422_great_load1.0.rou.xml'), 'r') as f:
        _CONTENT = f.read().split('\n')

    print("Generating loads...")
    for load in LOADS:
        _CONFIG = """<configuration>
    <input>
        <net-file value="sathorn_w_fixed_20160404.net.xml" />
        <route-files value="Great-route/sathorn_w_20160422_great_load{}.rou.xml" />
        <gui-settings-file value="sathorn_w.settings.xml" />
    </input>
    <time>
        <begin value="21600" />
	<end value="32400" />
    </time>
</configuration>""".format(load)
        
        if load == 1.0:
            print("skipping 1.0 [ default ]")
            continue
        print("Generating load {}/{}".format(load, 10.0))
        for route in _ROUTES:
            _ROW = _CONTENT[route].split(' ')
##            print(_ROW)
            _ROW[6] = 'vehsPerHour="{}"'.format(float(_ROW[6][len("vehsPerHour")+2:-1])*load)
##            print(_ROW)
            _CONTENT[route] = " ".join(_ROW)
        
        with open(os.path.join('models', 'sathorn-morning', 'Great-route', 'sathorn_w_20160422_great_load{}.rou.xml').format(load), 'w') as f:
            f.write("\n".join(_CONTENT))

        print("Generating config {}/{}".format(load, 10.0))
        with open(os.path.join('models', 'sathorn-morning', 'sathorn_w_great_load{}.sumo.cfg').format(load), 'w') as f:
            f.write(_CONFIG)
    print("Done!")
        
if __name__ == "__main__":
    main()
