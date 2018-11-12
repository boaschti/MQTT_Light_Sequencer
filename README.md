# This projekt is a light/channel sequencer. 
Absolutly no warranty for safety and funktionality!

### Features
- the Software runs in Python
- it gets saved data via MQTT
- it gets sequence data via MQTT
- it publishes data to MQTT 
- you can fade RGB lamps DMX lamps and every channel you want
- you can set a channel offset for each lamp (input channel can be from 1-5 and output channel is 11-16 (offset : 10))
- you can set a fade time, the skript search for the max delta between two channels an calculates steptime
- string data like: {"relay": "on"} will be untouched send to dstTopic
- data like: {"1": 1, "r": 0} and {"1": 100, "r": 80} will be faded in 100 steps (same dstTopic in both scenes!)
- a programm looks like {szeneA:{Nr, fadeTime, wait, universeA:{srcTopic, dstTopic, chOffset}, universeB:{srcTopic, dstTopic, chOffset}}, szeneB:....}
- the data looks like: {"1": 8, "2": 67, "3": 6, "4": 5, "relay": "on", "r": 8}