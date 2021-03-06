# -*- coding: utf-8 -*-
from time import sleep
import time
import paho.mqtt.client as mqtt
import json
import thread
from threading import Thread


client = mqtt.Client()

# Anforderung:
# Erforderliche Parameter mit constanten Key Namen: Nr, fadeTime, wait, srcTopic, dstTopic, chOffset
# szene Keys müssen einzigartig sein!!!
# universe Keys innerhalb einer szene muessen einzigartig sein!!!
# Syntax: {szeneA:{Nr, fadeTime, wait, universeA:{srcTopic, dstTopic, chOffset}, universeB:{srcTopic, dstTopic, chOffset}}, szeneB:....}
# Gespeicherte Werte unter srcTopic {"1": 8, "2": 67, "3": 6, "4": 5, "relay": "on", "r": 8}
 
 
# console test data:

# mosquitto_pub -d  -u mqttClients -P MHaPlC86mI -t dmx/fader/programm -m "{\"sceneFoo2\": {\"Nr\":2, \"fadeTime\": 10, \"wait\": 0.5, \"universeFoo\":{\"srcTopic\": \"dmx/backup/szene/hell\", \"dstTopic\": \"dmx/mover_1/set/programm\", \"chOffset\": 0}, \"universeBar\":{\"srcTopic\": \"dmx/backup/szene/hell\", \"dstTopic\": \"dmx/mover_1/set/programm\", \"chOffset\": 14}, \"universebFoo\":{\"srcTopic\": \"dmx/backup/pos/Garten\", \"dstTopic\": \"dmx/mover_1/set/programm\", \"chOffset\": 0}, \"universeBarFoo\":{\"srcTopic\": \"dmx/backup/pos/Garten\", \"dstTopic\": \"dmx/mover_1/set/programm\", \"chOffset\": 14}},\"szeneBar1\": {\"Nr\":1, \"fadeTime\": 5.0, \"wait\": 1.0, \"universeFoo\":{\"srcTopic\": \"dmx/backup/pos/Terrasse\", \"dstTopic\": \"dmx/mover_1/set/programm\", \"chOffset\": 0}, \"universeBarFoo\":{\"srcTopic\": \"dmx/backup/pos/Terrasse\", \"dstTopic\": \"dmx/mover_1/set/programm\", \"chOffset\": 14}, \"universebFoo\":{\"srcTopic\": \"dmx/backup/szene/chillig_1\", \"dstTopic\": \"dmx/mover_1/set/programm\", \"chOffset\": 0}, \"universeBar\":{\"srcTopic\": \"dmx/backup/szene/chillig_2\", \"dstTopic\": \"dmx/mover_1/set/programm\", \"chOffset\": 14}}, \"szeneBar3\": {\"Nr\":3, \"fadeTime\": 8.0, \"wait\": 0.0, \"universeFooFoo\":{\"srcTopic\": \"dmx/backup/pos/Big_Baam\", \"dstTopic\": \"dmx/mover_1/set/programm\", \"chOffset\": 0}, \"universeBarFoo\":{\"srcTopic\": \"dmx/backup/pos/Big_Baam\", \"dstTopic\": \"dmx/mover_1/set/programm\", \"chOffset\": 14}} }"


 
# einige Globale Variablen zum Empfangen der Daten

SrcData = {}


# Eine Variable und eine Funktion zum Testen des Skripts
testProg = {"sceneFoo2": {"Nr":2, "fadeTime": 10, "wait": 0.5, "universeFoo":{"srcTopic": "dmx/backup/szene/hell", "dstTopic": "foo/bar", "chOffset": 0}, "universeBar":{"srcTopic": "dmx/backup/szene/hell", "dstTopic": "foofoo/bar", "chOffset": 14}}, "szeneBar1": {"Nr":1, "fadeTime": 2.5, "wait": 1.0, "universeFoo":{"srcTopic": "dmx/backup/pos/Garten", "dstTopic": "foo/bar", "chOffset": 2}, "universeBarFoo":{"srcTopic": "dmx/backup/pos/Garten", "dstTopic": "foo/foobar", "chOffset": 14}}, "szeneBar3": {"Nr":3, "fadeTime": 2.6, "wait": 0.8, "universeFooFoo":{"srcTopic": "dmx/backup/pos/Big_Baam", "dstTopic": "foo/bar", "chOffset": 2}, "universeBarFoo":{"srcTopic": "dmx/backup/pos/Big_Baam", "dstTopic": "foo/foobar", "chOffset": 15}} }

#testProg = {"sceneFoo2": {"Nr":2, "fadeTime": 10, "wait": 0.5, "universeFoo":{"srcTopic": "foo/bar", "dstTopic": "foo/bar", "chOffset": 0}, "universeBar":{"srcTopic": "bar/foo", "dstTopic": "foofoo/bar", "chOffset": 14}}, "szeneBar1": {"Nr":1, "fadeTime": 2.5, "wait": 1.0, "universeFoo":{"srcTopic": "bar/foobar", "dstTopic": "foo/bar", "chOffset": 2}, "universeBarFoo":{"srcTopic": "bar/barfoo", "dstTopic": "foo/foobar", "chOffset": 14}}, "szeneBar3": {"Nr":3, "fadeTime": 2.6, "wait": 0.8, "universeFooFoo":{"srcTopic": "bar/barfoo", "dstTopic": "foo/bar", "chOffset": 2}, "universeBarFoo":{"srcTopic": "bar/barfoo", "dstTopic": "foo/foobar", "chOffset": 15}} }
 
def getDummyData(sceneNr):
    if sceneNr == 2:
        return {"1": 8, "2": 67, "3": 6, "4": 5, "5": 100, "R":200, "Relay":"On"}
    else:
        return {"1": 150, "2": 0, "3": 100, "4": 200, "R":150}
 
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

def on_message(client, userdata, msg):
    global SrcData

    temp = json.loads(str(msg.payload))
    print("thread %i" % thread.get_ident())
    print(msg.topic + " " + str(msg.payload))
        
    for i in temp.keys():
        if type(temp[i]) is dict:
            t = Thread(target=runProgramm, args=(temp, False, True,))
            t.start()
            break
        else:
            SrcData[msg.topic] = json.loads(str(msg.payload))
            break

client.on_connect = on_connect
client.on_message = on_message



def getMqttData(topic, verbose):
    global SrcData
    
    if verbose:
        print("subscribe to %s" % topic)
    
    client.subscribe(topic)
    
    if verbose:
        print("thread %i" % thread.get_ident())
        print("warte auf Mqtt Daten...")
 
    # Timout 5s == 500
    for _ in range(500):
        if topic in SrcData:
            if verbose:
                print("Mqtt Daten empfangen")
            client.unsubscribe(topic)
            return SrcData[topic]
        sleep(0.1)

    if not topic in SrcData:
        client.publish("fader/info", "No MQTT Data received. Topic was: %s" %topic)
        if verbose:
            print("Error! Keine Mqtt Daten empfangen")
        raise RuntimeError
 
    client.unsubscribe(topic)
     
 
def fadeChannels(scene, savedDstData, universes, verbose):
 
    steps = {}
    channelsToFade = {}
    tempFadeData = {}
    maxDelta = 0
    stepTime = 0.0
 
    for device in universes:
        
        channelsModified = False
        for channel in scene[device]["srcData"].keys():
            # chOffset anwenden wenn der Channel eine Zahl ist und die Daten im key srcData anpassen
            if channel.isdigit() and scene[device]["chOffset"] != 0:
                # Wir müssen uns die neuen Daten unter einem neuen Key speichern da die Daten sonst evtl für andere Lampen auch verändert werden.
                # Das liegt daran, dass in Python Key mit gleichen Inhalt auf eine Id referenziert sind. Diese Id ändert sich beim ändern der Daten nicht 
                if "newSrcData" not in scene[device]:
                    scene[device]["newSrcData"] = {}
                newChannel = str(int(channel) + scene[device]["chOffset"])
                scene[device]["newSrcData"][newChannel] = scene[device]["srcData"][channel]
                channelsModified = True
            else:
                if "newSrcData" not in scene[device]:
                    scene[device]["newSrcData"] = {}
                scene[device]["newSrcData"][channel] = scene[device]["srcData"][channel]
                channelsModified = True
        if channelsModified:
            del scene[device]["srcData"]
            scene[device]["srcData"] = scene[device].pop("newSrcData")
            
        # Daten eines neuen Topics speichern
        if scene[device]["dstTopic"] not in savedDstData:
            savedDstData[scene[device]["dstTopic"]] = scene[device]["srcData"]
        # Topic als key im dict anlegen damit man es nachher befuellen kann
        if scene[device]["dstTopic"] not in steps:
            steps[scene[device]["dstTopic"]] = {}
            channelsToFade[scene[device]["dstTopic"]] = {}
            tempFadeData[scene[device]["dstTopic"]] = {}
        # Wir ermitteln uns den max Delta der Kanaele
        for channel in scene[device]["srcData"].keys():
            # Wir speichern uns nicht vorhandene Kanaele
            if channel not in savedDstData[scene[device]["dstTopic"]]:
                savedDstData[scene[device]["dstTopic"]][channel] = scene[device]["srcData"][channel]
            if type(scene[device]["srcData"][channel]) is int:
                delta = scene[device]["srcData"][channel] - savedDstData[scene[device]["dstTopic"]][channel]
            else:
                delta = 0
            if maxDelta < delta:
                maxDelta = delta
            if maxDelta < delta * -1:
                maxDelta = delta * -1
    if maxDelta:
        stepTime = float(scene["fadeTime"]) / float(maxDelta)
        # TODO pruefen ob die zeit nicht zu klein ist und evtl schrittweite vergroessern
 
    for device in universes:
        for channel in scene[device]["srcData"].keys():
            # Wir errechnen uns die benoetigten Steps der Kanaele
            if channel in savedDstData[scene[device]["dstTopic"]]:
                if type(scene[device]["srcData"][channel]) is int:
                    if maxDelta > 0:
                        steps[scene[device]["dstTopic"]][channel] = float((scene[device]["srcData"][channel] - savedDstData[scene[device]["dstTopic"]][channel])) / maxDelta
                    else:
                        steps[scene[device]["dstTopic"]][channel] = float(scene[device]["srcData"][channel] - savedDstData[scene[device]["dstTopic"]][channel])
 
        if verbose:
            print("dstAdd:")
            print(scene[device]["dstTopic"])
            print("Dim %s in %i steps to:" % (scene[device]["dstTopic"],maxDelta))
            print("StepTime: %f" %stepTime)
            print(scene[device]["srcData"])
            print("Delta:")
            print(steps[scene[device]["dstTopic"]])
 
    for channel in savedDstData[scene[device]["dstTopic"]].keys():
        if channel not in steps[scene[device]["dstTopic"]]:
            del savedDstData[scene[device]["dstTopic"]][channel]
        
    for device in universes:
        #Wir legen uns ein neues Quelldaten Dict an damit wir nur die Känäle senden die wir bearbeiten        
        for channel in steps[scene[device]["dstTopic"]].keys():
            channelsToFade[scene[device]["dstTopic"]][channel] = savedDstData[scene[device]["dstTopic"]][channel]
            
    # Wir wollen ueber alle Kanaele faden
    initVar = True
    dstreached = True
    extraLoop = False
    timeStamp = time.time()
    if verbose:
        print("timestamp %f, stepTime: %f" % (timeStamp,stepTime))
    # Wir bereiten die Schleife wegen eventuellen Rundungsfehlern mit einer extraLoop vor
    for i in range(maxDelta + 1):
        if not extraLoop:
            timeStamp = timeStamp + stepTime
        for device in universes:
            publishData = False
            for channel in scene[device]["srcData"].keys():
                # Init Dict mit den benoetigten Channels
                if initVar:
                    if type(scene[device]["srcData"][channel]) is int and not stepTime == 0.0:
                        tempFadeData[scene[device]["dstTopic"]][channel] = float(channelsToFade[scene[device]["dstTopic"]][channel]) + steps[scene[device]["dstTopic"]][channel]
                        channelsToFade[scene[device]["dstTopic"]][channel] = int(tempFadeData[scene[device]["dstTopic"]][channel])
                    else:
                        channelsToFade[scene[device]["dstTopic"]][channel] = scene[device]["srcData"][channel]
                    publishData = True
                # Errechne die neuen Dim Werte wenn der Zielwert noch nicht erreicht ist (Floating Point addition!!)
                # todo faden ausbauen wenn stepTime == 0.0
                elif channelsToFade[scene[device]["dstTopic"]][channel] != scene[device]["srcData"][channel]:
                    tempFadeData[scene[device]["dstTopic"]][channel] = tempFadeData[scene[device]["dstTopic"]][channel] + steps[scene[device]["dstTopic"]][channel]
                    channelsToFade[scene[device]["dstTopic"]][channel] = int(tempFadeData[scene[device]["dstTopic"]][channel])
                publishData = True
                if channelsToFade[scene[device]["dstTopic"]][channel] != scene[device]["srcData"][channel] and i + 1 == maxDelta:
                    dstreached = False
            
            # Wir wollen die Daten der zwischenschritte nur senden wenn es eine Step Time gibt. In der letzen Runde natürlich schon
            if stepTime > 0.0 or i +1 == maxDelta or i == maxDelta:
                if publishData:
                    client.publish(scene[device]["dstTopic"], json.dumps(channelsToFade[scene[device]["dstTopic"]]), retain = False)
                               
        initVar = False
 
        if verbose:
            print(channelsToFade)
 
        if dstreached:
            while timeStamp > time.time():
                pass
        elif not extraLoop:
            if verbose:
                print("extraLoop")
            dstreached = True
            extraLoop = True
        # Wenn kein Rundungsfehler vorliegt können wir die Schleife mit der richtigen Durchlaufzahl verlassen
        if i + 1 == maxDelta and not extraLoop:
            break
 
    if verbose:
        print("timestamp %f" % time.time())
    # Wir sind mit dem Faden fertig und speichern uns die EndWerte
    if not dstreached:
        if verbose:
            print("Oops something went wrong! Did not reached endpoint.")
        for device in universes:
            channelsToFade[scene[device]["dstTopic"]].update(scene[device]["srcData"])
 
    return channelsToFade
 
 
def runProgramm(myProg, testMode = False, verbose = False):
    if not hasattr(runProgramm, "savedDstData"):
        runProgramm.savedDstData = {}
        
    # Sicherstellen, dass die Szenen nach einander ausgefuehrt werden deswegen zaehlen wir die Szenen und laufen
    # mit der sceneNr ueber die Schleife
    for sceneNr in range(1, 1+len(myProg.keys())):
        if verbose:
            print ("sceneNr: %i" % sceneNr)
        # Wir laufen über alle Szenen und pruefen auf die sceneNr
        for scene in myProg.keys():
            if myProg[scene]["Nr"] == sceneNr:
                sceneData = myProg[scene].keys()
                if verbose:
                    print("Scene: %s" % scene)
                # Wir extrahiern aus der Szene die Universe Daten. Die Key Namen der eceptItems sind bekannt.
                eceptItems = ['Nr','fadeTime','wait']
                universes = []
                for temp in sceneData:
                    if temp not in eceptItems:
                        universes.append(temp)
                if verbose:
                    print("Universes:")
                    print(universes)
                # Wir holen uns die Quelldaten der Universen indem wir uns auf das srcTopic subscriben
                for universe in universes:
                   
                    #print("publish to %s" % myProg[scene][universe]["dstTopic"])
                    #print("channel offset %i" % myProg[scene][universe]["chOffset"])
                    if testMode:
                        myProg[scene][universe]["srcData"] = getDummyData(sceneNr)
                    else:
                        myProg[scene][universe]["srcData"] = getMqttData(myProg[scene][universe]["srcTopic"], verbose)
                    del myProg[scene][universe]["srcTopic"]
 
                # Fade all channels
                runProgramm.savedDstData.update(fadeChannels(myProg[scene], runProgramm.savedDstData, universes, verbose))
 
                if verbose:
                    print("#################################")
                    print(runProgramm.savedDstData)
                    print("#################################")
 
                if verbose:
                    # Einige szene Daten printen
                    print("fadeTime %f" % myProg[scene]["fadeTime"])
                    print("wait %f" % myProg[scene]["wait"])
 
 
#Todo diese variablen sollen per argument uebergeben werden
client.connect("192.168.178.38", 1883, 60)
client.loop_start()
client.subscribe("dmx/fader/programm")

#runProgramm(testProg, testMode = False, verbose = True)

while(1):
    sleep(0.1)
    

