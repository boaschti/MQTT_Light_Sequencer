# -*- coding: utf-8 -*-
from time import sleep
import time
 
 
# Anforderung:
# Erforderliche Parameter mit constanten Key Namen: Nr, fadeTime, wait, srcTopic, dstTopic, chOffset
# szene Keys müssen einzigartig sein!!!
# universe Keys innerhalb einer szene müssen einzigartig sein!!!
# Syntax: {szeneA:{Nr, fadeTime, wait, universeA:{srcTopic, dstTopic, chOffset}, universeB:{srcTopic, dstTopic, chOffset}}, szeneB:....}
# Gespeicherte Werte unter srcTopic {"1": 8, "2": 67, "3": 6, "4": 5, "relay": "on", "r": 8}
 
 
# einige Globale Variablen zum Empfangen der Daten
Data = ""
DataTopic =""
 
# Eine Variable und ein Funktion zum Testen des Skripts
testProg = {"sceneFoo2": {"Nr":2, "fadeTime": 10, "wait": 0.5, "universeFoo":{"srcTopic": "foo/bar", "dstTopic": "foo/bar", "chOffset": 0}, "universeBar":{"srcTopic": "bar/foo", "dstTopic": "foofoo/bar", "chOffset": 14}}, "szeneBar1": {"Nr":1, "fadeTime": 2.5, "wait": 1.0, "universeFoo":{"srcTopic": "bar/foobar", "dstTopic": "foo/bar", "chOffset": 2}, "universeBarFoo":{"srcTopic": "bar/barfoo", "dstTopic": "foo/foobar", "chOffset": 14}}, "szeneBar3": {"Nr":3, "fadeTime": 2.6, "wait": 0.8, "universeFooFoo":{"srcTopic": "bar/barfoo", "dstTopic": "foo/bar", "chOffset": 2}, "universeBarFoo":{"srcTopic": "bar/barfoo", "dstTopic": "foo/foobar", "chOffset": 15}} }
 
def getDummyData(sceneNr):
    #SrcData.append("13")
    if sceneNr == 2:
        return {"1": 8, "2": 67, "3": 6, "4": 5, "5": 100, "R":200, "Relay":"On"}
    else:
        return {"1": 150, "2": 0, "3": 100, "4": 200, "R":150}
 
 
def getMqttData(topic, scene, verbose):
 
    global Data
    global DataTopic
    if verbose:
        print("subscribe to %s" % topic)
    #subscribe(myProg[scene][universe]["srcTopic"])
    if verbose:
        print("warte auf Mqtt Daten...")
    # Timout 5s == 500
    Data = ""
    DataTopic =""
 
    for _ in range(500):
        sleep(0.01)
        # Todo delete following line SrcData = dumps(Data)
        SrcData = {}
        if SrcData:
            if verbose:
                print("Mqtt Daten empfangen")
            break
    if not SrcData:
        if verbose:
            print("Error! Keine Mqtt Daten empfangen")
        raise RuntimeError
 
    return SrcData
 
 
def fadeChannels(scene, savedDstData, universes, verbose):
 
    steps = {}
    tempFadeData = {}
    maxDelta = 0
    stepTime = 0.0
 
    for device in universes:
        savedNewChannel = []
        for channel in scene[device]["srcData"].keys():
            # chOffset anwenden wenn der Channel eine Zahl ist und die Daten im key srcData anpassen
            if channel.isdigit() and scene[device]["chOffset"] != 0:
                newChannel = str(int(channel) + scene[device]["chOffset"])
                # Wir müssen uns die Channels merken, die wir verändert haben damit wir diese nachher nicht wieder löschen
                # Das passiert wenn der offset kleiner als die channelanzahl ist
                savedNewChannel.append(newChannel)
                scene[device]["srcData"][newChannel] = scene[device]["srcData"][channel]
                if not channel in savedNewChannel:
                    del scene[device]["srcData"][channel]
 
        # Daten eines neuen Topics speichern
        if scene[device]["dstTopic"] not in savedDstData:
            savedDstData[scene[device]["dstTopic"]] = scene[device]["srcData"]
        # Topic als key im dict anlegen damit man es nachher befüllen kann
        if scene[device]["dstTopic"] not in steps:
            steps[scene[device]["dstTopic"]] = {}
            tempFadeData[scene[device]["dstTopic"]] = {}
        # Wir ermitteln uns den max Delta der Kanäle
        for channel in scene[device]["srcData"].keys():
            # Wir speichern uns nicht vorhandene Kanäle
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
        # TODO prüfen ob die zeit nicht zu klein ist und evtl schrittweite vergrößern
 
    for device in universes:
        for channel in scene[device]["srcData"].keys():
            # Wir errechnen uns die benötigten Steps der Kanäle
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
            print(scene[device]["srcData"])
            print("Delta:")
           print(steps[scene[device]["dstTopic"]])
 
    # Wir wollen über alle Kanäle faden
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
            for channel in scene[device]["srcData"].keys():
                # Init Dict mit den benötigten Channels
                if initVar:
                    if type(scene[device]["srcData"][channel]) is int:
                        tempFadeData[scene[device]["dstTopic"]][channel] = float(savedDstData[scene[device]["dstTopic"]][channel]) + steps[scene[device]["dstTopic"]][channel]
                        savedDstData[scene[device]["dstTopic"]][channel] = int(tempFadeData[scene[device]["dstTopic"]][channel])
                    else:
                        savedDstData[scene[device]["dstTopic"]][channel] = scene[device]["srcData"][channel]
                # Errechne die neuen Dim Werte wenn der Zielwert noch nicht erreicht ist (Floating Point addition!!)
                elif savedDstData[scene[device]["dstTopic"]][channel] != scene[device]["srcData"][channel]:
                    tempFadeData[scene[device]["dstTopic"]][channel] = tempFadeData[scene[device]["dstTopic"]][channel] + steps[scene[device]["dstTopic"]][channel]
                    savedDstData[scene[device]["dstTopic"]][channel] = int(tempFadeData[scene[device]["dstTopic"]][channel])
                if savedDstData[scene[device]["dstTopic"]][channel] != scene[device]["srcData"][channel] and i + 1 == maxDelta:
                    dstreached = False
 
        initVar = False
 
        if verbose:
            print(savedDstData)
        # Todo send data here
 
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
            savedDstData[scene[device]["dstTopic"]].update(scene[device]["srcData"])
 
    return savedDstData
 
 
def runProgramm(myProg, testMode = False, verbose = False):
    savedDstData = {}
    # Sicherstellen, dass die Szenen nach einander ausgeführt werden deswegen zählen wir die Szenen und laufen
    # mit der sceneNr über die Schleife
    for sceneNr in range(1, 1+len(myProg.keys())):
        if verbose:
            print ("sceneNr: %i" % sceneNr)
        # Wir laufen über alle Szenen und prüfen auf die sceneNr
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
                    # todo del scene parameter
                   
                    #print("publish to %s" % myProg[scene][universe]["dstTopic"])
                    #print("channel offset %i" % myProg[scene][universe]["chOffset"])
                    if testMode:
                        myProg[scene][universe]["srcData"] = getDummyData(sceneNr)
                    else:
                        myProg[scene][universe]["srcData"] = getMqttData(myProg[scene][universe]["srcTopic"], scene, verbose)
                    del myProg[scene][universe]["srcTopic"]
 
                # Fade all channels
                savedDstData = fadeChannels(myProg[scene], savedDstData, universes, verbose)
 
                if verbose:
                    print("#################################")
                    print(savedDstData)
                    print("#################################")
 
                if verbose:
                    # Einige szene Daten printen
                    print("fadeTime %f" % myProg[scene]["fadeTime"])
                    print("wait %f" % myProg[scene]["wait"])
 
 
runProgramm(testProg, testMode = True, verbose = True)