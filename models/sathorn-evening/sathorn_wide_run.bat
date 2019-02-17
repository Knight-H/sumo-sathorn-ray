export SUMO_HOME=/usr/lib/sumo/
#sumo-gui --time-to-teleport 300 --no-internal-links true --ignore-junction-blocker 1 --random true -c sathorn_w.sumo.cfg -a sathon_wide_tls_20160418_edited.add.xml --summary summary.xml

/opt/sumo/bin/sumo-gui --time-to-teleport -1 --no-internal-links true --ignore-junction-blocker 1 --random false --seed 10 -c sathorn_w.sumo.cfg -a sathon_wide_tls_20160418_edited.add.xml --summary summary.xml
