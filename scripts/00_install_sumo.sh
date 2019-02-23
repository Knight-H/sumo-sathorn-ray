export SUMO_HOME=/opt/sumo
export SUMO_VERSION=1.0.1

sudo apt-get update && sudo apt-get -y install wget build-essential cmake  libxerces-c-dev libfox-1.6-dev libproj-dev libgdal-dev swig python3-dev

wget http://downloads.sourceforge.net/project/sumo/sumo/version%20$SUMO_VERSION/sumo-src-$SUMO_VERSION.tar.gz && tar xf sumo-src-$SUMO_VERSION.tar.gz && sudo mv sumo-$SUMO_VERSION $SUMO_HOME && rm sumo-src-$SUMO_VERSION.tar.gz


# find correct python version editing CMake
cd $SUMO_HOME && sed -i '74s/.*/set(Python_ADDITIONAL_VERSIONS 3.7 3.6 3.5 3.4 3.3 2.7) # it may help in finding the correct python for libsumo/' CMakeLists.txt && mkdir build/cmake-build && cd build/cmake-build && cmake ../..

make -j 16

cd ~ && git clone https://github.com/Knight-H/sumo-sathorn-ray

cd sumo-sathorn-ray 
