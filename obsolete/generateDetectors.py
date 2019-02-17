from lxml import etree
from constants import *

#freq is non relevant to TraCI
arealAttr = {"id":"", "lane": "", "pos":"", "length":"",
            "freq":"100", "file":"areal.txt", "friendlyPos":"true"}

arealAttr = {"id":"", "lane": "", "pos":"", "length":"", "freq":"100", "file":"areal.txt"}

loopAttr = {"id":"", "lane":"", "pos":"", "freq":"100", "file":"detector.txt"}
phaseAttr = {"duration":"", "state":""}

arealCount = 0


if __name__ == "__main__":
    #root of XML additional file
    root = etree.Element('additional')

    
    #Charoen Rat 
    for edge in edge_charoenRat:
        for lane in net.getEdge(edge).getLanes():
            arealAttr["id"] = "e2_"+lane.getID()+"_0"
            arealAttr["lane"] = lane.getID()
            arealAttr["pos"] = str(lane.getLength()- 30)
            arealAttr["length"] = "30"
            arealAttr["file"] = "./output/{}.txt".format(arealAttr["id"])
            arealCount += 1
            etree.SubElement(root, "laneAreaDetector", attrib = arealAttr)

            arealAttr["id"] = "e2_"+lane.getID()+"_1"
            arealAttr["pos"] = str(lane.getLength()- 200)
            arealAttr["length"] = "170"
            arealAttr["file"] = "./output/{}.txt".format(arealAttr["id"])
            arealCount += 1
            etree.SubElement(root, "laneAreaDetector", attrib = arealAttr)
            
            arealAttr["id"] = "e2_"+lane.getID()+"_2"
            arealAttr["pos"] = "0"
            arealAttr["length"] = str(lane.getLength()- 200)
            arealAttr["file"] = "./output/{}.txt".format(arealAttr["id"])
            arealCount += 1
            etree.SubElement(root, "laneAreaDetector", attrib = arealAttr)


    
    
    #Surasak
    for edge in edge_surasak:
        for lane in net.getEdge(edge).getLanes():
            if edge_surasak[0] in lane.getID():
                arealAttr["id"] = "e2_"+lane.getID()+"_0"
                arealAttr["lane"] = lane.getID()
                arealAttr["pos"] = str(lane.getLength()- 30)
                arealAttr["length"] = "30"
                arealAttr["file"] = "./output/{}.txt".format(arealAttr["id"])
                arealCount += 1
                etree.SubElement(root, "laneAreaDetector", attrib = arealAttr)

                
                if "L10189_2" in lane.getID(): ########ERRORR##########
                    arealAttr["id"] = "e2_"+lane.getID()+"_1"
                    arealAttr["pos"] = "0"  # was 3
                    arealAttr["length"] = str(lane.getLength()- 30)  #was -3
                    arealAttr["file"] = "./output/{}.txt".format(arealAttr["id"])
                    arealCount += 1
                    etree.SubElement(root, "laneAreaDetector", attrib = arealAttr)
                else:
                    arealAttr["id"] = "e2_"+lane.getID()+"_1"
                    arealAttr["pos"] = "0" # was 3
                    arealAttr["length"] = str(lane.getLength()- 30 ) #was -3
                    arealAttr["file"] = "./output/{}.txt".format(arealAttr["id"])
                    arealCount += 1
                    etree.SubElement(root, "laneAreaDetector", attrib = arealAttr)
                
                
                



            
            elif "L10130_0" in lane.getID() or "L10130_1" in lane.getID(): ########ERRORR##########
                arealAttr["id"] = "e2_"+lane.getID()+"_2"
                arealAttr["lane"] = lane.getID()
                arealAttr["pos"] = "3" 
                arealAttr["length"] = str(lane.getLength()-3)
                arealAttr["file"] = "./output/{}.txt".format(arealAttr["id"])
                arealCount += 1
                etree.SubElement(root, "laneAreaDetector", attrib = arealAttr)
            else:
                arealAttr["id"] = "e2_"+lane.getID()+"_2"
                arealAttr["lane"] = lane.getID()
                arealAttr["pos"] = "3" #changed to complement the error
                arealAttr["length"] = str(lane.getLength()-3)
                arealAttr["file"] = "./output/{}.txt".format(arealAttr["id"])
                arealCount += 1
                etree.SubElement(root, "laneAreaDetector", attrib = arealAttr)
            
            
    
    #Sathorn North 
    for edge in edge_sathornN:
        for lane in net.getEdge(edge).getLanes():
            if edge_sathornN[0] in lane.getID():
                arealAttr["id"] = "e2_"+lane.getID()+"_0"
                arealAttr["lane"] = lane.getID()
                arealAttr["pos"] = "0"
                arealAttr["length"] = str(lane.getLength())
                arealAttr["file"] = "./output/{}.txt".format(arealAttr["id"])
                arealCount += 1
                etree.SubElement(root, "laneAreaDetector", attrib = arealAttr)


            
            elif edge_sathornN[1]+"_0" in lane.getID(): ####EROR ## 3m still error!!!
                arealAttr["id"] = "e2_"+lane.getID()+"_1"
                arealAttr["lane"] = lane.getID()
                arealAttr["pos"] = "4"
                arealAttr["length"] = str(lane.getLength()-4)
                arealAttr["file"] = "./output/{}.txt".format(arealAttr["id"])
                arealCount += 1
                etree.SubElement(root, "laneAreaDetector", attrib = arealAttr)
            elif edge_sathornN[1] in lane.getID():
                arealAttr["id"] = "e2_"+lane.getID()+"_1"
                arealAttr["lane"] = lane.getID()
                arealAttr["pos"] = "4" #changed to complement error
                arealAttr["length"] = str(lane.getLength()-4)
                arealAttr["file"] = "./output/{}.txt".format(arealAttr["id"])
                arealCount += 1
                etree.SubElement(root, "laneAreaDetector", attrib = arealAttr)
            
            elif edge_sathornN[2]+"_1" in lane.getID():################################
                arealAttr["id"] = "e2_"+lane.getID()+"_1"
                arealAttr["lane"] = lane.getID()
                arealAttr["pos"] = "3" 
                arealAttr["length"] = str(lane.getLength()-3)
                arealAttr["file"] = "./output/{}.txt".format(arealAttr["id"])
                arealCount += 1
                etree.SubElement(root, "laneAreaDetector", attrib = arealAttr)
            elif edge_sathornN[2] in lane.getID():
                arealAttr["id"] = "e2_"+lane.getID()+"_1"
                arealAttr["lane"] = lane.getID()
                arealAttr["pos"] = "3" #changed to complement error
                arealAttr["length"] = str(lane.getLength()-3)
                arealAttr["file"] = "./output/{}.txt".format(arealAttr["id"])
                arealCount += 1
                etree.SubElement(root, "laneAreaDetector", attrib = arealAttr)

            
            elif edge_sathornN[3]+"_0" in lane.getID():###########################
                arealAttr["id"] = "e2_"+lane.getID()+"_2"
                arealAttr["lane"] = lane.getID()
                arealAttr["pos"] = "3"
                arealAttr["length"] = str(lane.getLength()-3)
                arealAttr["file"] = "./output/{}.txt".format(arealAttr["id"])
                arealCount += 1
                etree.SubElement(root, "laneAreaDetector", attrib = arealAttr)
            elif edge_sathornN[3] in lane.getID():
                arealAttr["id"] = "e2_"+lane.getID()+"_2"
                arealAttr["lane"] = lane.getID()
                arealAttr["pos"] = "3" #changed to complement error
                arealAttr["length"] = str(lane.getLength()-3)
                arealAttr["file"] = "./output/{}.txt".format(arealAttr["id"])
                arealCount += 1
                etree.SubElement(root, "laneAreaDetector", attrib = arealAttr)

            
            
            
            
            
            
            
    
    #Sathorn South
    for edge in edge_sathornS:
        for lane in net.getEdge(edge).getLanes():
            if edge_sathornS[0] in lane.getID():
                

                arealAttr["id"] = "e2_"+lane.getID()+"_0"
                arealAttr["lane"] = lane.getID()
                arealAttr["pos"] = str(lane.getLength()-30)
                arealAttr["length"] = "30"
                arealAttr["file"] = "./output/{}.txt".format(arealAttr["id"])
                arealCount += 1
                etree.SubElement(root, "laneAreaDetector", attrib = arealAttr)

                arealAttr["id"] = "e2_"+lane.getID()+"_1"
                arealAttr["lane"] = lane.getID()
                arealAttr["pos"] = "0"
                arealAttr["length"] = str(lane.getLength()-30)
                arealAttr["file"] = "./output/{}.txt".format(arealAttr["id"])
                arealCount += 1
                etree.SubElement(root, "laneAreaDetector", attrib = arealAttr)
                



            elif edge_sathornS[1]+"_0" in lane.getID(): ########################################
                arealAttr["id"] = "e2_"+lane.getID()+"_1"
                arealAttr["lane"] = lane.getID()
                arealAttr["pos"] = "3"
                arealAttr["length"] = str(lane.getLength()-3)
                arealAttr["file"] = "./output/{}.txt".format(arealAttr["id"])
                arealCount += 1
                etree.SubElement(root, "laneAreaDetector", attrib = arealAttr)
            elif edge_sathornS[1] in lane.getID():
                arealAttr["id"] = "e2_"+lane.getID()+"_1"
                arealAttr["lane"] = lane.getID()
                arealAttr["pos"] = "0" #changed to complement error , 3 before
                arealAttr["length"] = str(lane.getLength())
                arealAttr["file"] = "./output/{}.txt".format(arealAttr["id"])
                arealCount += 1
                etree.SubElement(root, "laneAreaDetector", attrib = arealAttr)

            elif edge_sathornS[2] in lane.getID():
                
                arealAttr["id"] = "e2_"+lane.getID()+"_1"
                arealAttr["lane"] = lane.getID()
                arealAttr["pos"] = "0"
                arealAttr["length"] = str(lane.getLength())
                arealAttr["file"] = "./output/{}.txt".format(arealAttr["id"])
                arealCount += 1
                etree.SubElement(root, "laneAreaDetector", attrib = arealAttr)
            
            elif edge_sathornS[3] in lane.getID() or edge_sathornS[4] in lane.getID() or edge_sathornS[5] in lane.getID():
                arealAttr["id"] = "e2_"+lane.getID()+"_2"
                arealAttr["lane"] = lane.getID()
                arealAttr["pos"] = "0"
                arealAttr["length"] = str(lane.getLength())
                arealAttr["file"] = "./output/{}.txt".format(arealAttr["id"])
                arealCount += 1
                etree.SubElement(root, "laneAreaDetector", attrib = arealAttr)
    
    
        
    s = etree.tostring(root, pretty_print=True)
        
    with open(DETECTOR_FILE, 'wb') as f:
        f.write(s)
