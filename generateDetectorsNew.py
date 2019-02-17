from lxml import etree
from detector_constants import *
from constants import DETECTOR_FILE

#freq is non relevant to TraCI
arealAttr = {"id":"", "lane": "", "pos":"", "length":"",
            "freq":"100", "file":"areal.txt", "friendlyPos":"true"}

arealAttr = {"id":"", "lane": "", "pos":"", "length":"", "freq":"100", "file":"areal.txt"}

loopAttr = {"id":"", "lane":"", "pos":"", "freq":"100", "file":"detector.txt"}
phaseAttr = {"duration":"", "state":""}

loopStr = """ <root>  <inductionLoop file="out00.xml" freq="100" id="00" lane="L40_0" pos="500" />
    <inductionLoop file="out01.xml" freq="100" id="01" lane="L40_1" pos="500" />
    <inductionLoop file="out02.xml" freq="100" id="02" lane="L40_2" pos="500" />
    <inductionLoop file="out03.xml" freq="100" id="03" lane="L40_3" pos="500" />
    <inductionLoop file="out10.xml" freq="100" id="10" lane="L197#2_0" pos="60" />
    <inductionLoop file="out11.xml" freq="100" id="11" lane="L197#2_1" pos="60" />
    <inductionLoop file="out12.xml" freq="100" id="12" lane="L197#2_2" pos="60" />
    <inductionLoop file="out13.xml" freq="100" id="13" lane="L197#2_3" pos="60" />
    <inductionLoop file="out14.xml" freq="100" id="14" lane="L197#2_4" pos="60" />
    <inductionLoop file="out20.xml" freq="100" id="20" lane="L10189_0" pos="165" />
    <inductionLoop file="out21.xml" freq="100" id="21" lane="L10189_1" pos="165" />
    <inductionLoop file="out22.xml" freq="100" id="22" lane="L10189_2" pos="165" />
    <inductionLoop file="out23.xml" freq="100" id="23" lane="L10189_3" pos="165" />	
    <inductionLoop file="out30.xml" freq="100" id="30" lane="L239_0" pos="30" />
    <inductionLoop file="out31.xml" freq="100" id="31" lane="L239_1" pos="30" />
    <inductionLoop file="out32.xml" freq="100" id="32" lane="L239_2" pos="30" />
    <inductionLoop file="out33.xml" freq="100" id="33" lane="L239_3" pos="30" /> </root>"""



if __name__ == "__main__":
    #root of XML additional file
    root = etree.Element('additional')

    
    ## For upstream detectors
    for detector_list in (detector_sathornN, detector_sathornS, detector_charoenRat, detector_surasak):
        for cell_id, cell in enumerate(detector_list):
            for edge, pos, length in cell:
                for lane in range(NUM_LANES[edge]):
                    arealAttr["id"] = "e2_{}_{}_{}".format(edge, lane, cell_id)
                    arealAttr["lane"] = "{}_{}".format(edge, lane)
                    arealAttr["pos"] = str(pos)
                    arealAttr["length"] = str(length)
                    arealAttr["file"] = "./output/{}.txt".format(arealAttr["id"])
                    etree.SubElement(root, "laneAreaDetector", attrib = arealAttr)    
    
    ## For downstream detectors
    for detector_list in (detector_sathornN_down, detector_sathornS_down, detector_surasak_down):
        for cell_id, cell in enumerate(detector_list):
            for edge, pos, length in cell:
                for lane in range(NUM_LANES[edge]):
                    arealAttr["id"] = "e2_{}_{}_{}".format(edge, lane, cell_id)
                    arealAttr["lane"] = "{}_{}".format(edge, lane)
                    arealAttr["pos"] = str(pos)
                    arealAttr["length"] = str(length)
                    arealAttr["file"] = "./output/{}.txt".format(arealAttr["id"])
                    etree.SubElement(root, "laneAreaDetector", attrib = arealAttr)
                
    loop_root = etree.XML(loopStr)
    for child in loop_root:
        
        edge_lane = child.get("lane")
        pos = child.get("pos")
        
        loopAttr["id"] = "e1_{}".format(edge_lane)
        loopAttr["lane"] = "{}".format(edge_lane)
        loopAttr["pos"] = str(pos)
        loopAttr["file"] = "./output/{}.txt".format(loopAttr["id"])

        etree.SubElement(root, "inductionLoop", attrib = loopAttr)
    
        
    s = etree.tostring(root, pretty_print=True)
        
    with open(DETECTOR_FILE, 'wb') as f:
        f.write(s)
