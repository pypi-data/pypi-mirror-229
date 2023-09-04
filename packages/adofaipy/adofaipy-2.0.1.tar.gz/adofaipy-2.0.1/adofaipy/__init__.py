import re
import json

def getFileString(filename : str) -> str:
    """Returns the specified file in string format.
    It is reccomended to use getFileDict() unless absolutely necessary.
    """
    with open(filename, "r", encoding="utf-8-sig") as f:
        s = f.read()
        return s

def getFileDict(filename : str) -> dict:
    """Returns the specified file in the form of nested dictionaries and lists.
    """
    a = getFileString(filename)
    sp=re.split(r"(?<!\\)(?:\\\\)*(\")",a)

    for i in range(len(sp)):
        if i % 4 == 0:
            sp[i] = sp[i].replace("\n", "")
            sp[i] = sp[i].replace("\t", "")
            sp[i] = sp[i].replace(",]", "]")
            sp[i] = sp[i].replace(",}", "}")
            sp[i] = sp[i].replace(", ]", " ]")
            sp[i] = sp[i].replace(", }", " }")
            sp[i] = sp[i].replace(",  ]", "  ]")
            sp[i] = sp[i].replace(",  }", "  }")
            sp[i] = sp[i].replace("}{", "},{")
            sp[i] = sp[i].replace("][", "],[")
    
    a = ''.join(sp)
    final = json.loads(a)
    return final

def getAngles() -> None:
    try:
        raise DeprecationWarning
    except DeprecationWarning as dp:
        print("getAngles() is deprecated after adofaipy 2.0.0. Use the \"angleData\" field of the file dictionary instead.", dp)
#    index= filestring.find( "\"angleData\": [")
#    if index !=-1 :  
#        filestring = filestring[index:][:filestring[index:].index("],") + 2]
#    else :
#        filestring =  ""
#
#    filestring = filestring[14:][:-2].split(", ")
#    filestring = [int(i) for i in filestring]
#
#    return filestring

def setAngles() -> None:
    try:
        raise DeprecationWarning
    except DeprecationWarning as dp:
        print("setAngles() is deprecated after adofaipy 2.0.0. Use the \"angleData\" field of the file dictionary instead.", dp)
#    filestring = re.sub("\"angleData\": \[.*\],", "\"angleData\": [" + ', '.join([str(elem) for elem in angles]) + "],", filestring)
#    return filestring

def addEvent(event : dict, leveldict : dict) -> dict:
    """Adds the given dictionary as an action/decoration
    and returns a copy of the file as a dictionary.
	Remember to reassign this to the original dictionary!
    """
    
    isDecoration = True if event["eventType"] == "AddDecoration" else False

    if isDecoration:
        leveldict["decorations"].append(event)
    else:
        leveldict["actions"].append(event)
    return leveldict


def searchEvents(searchfor : dict, leveldict : dict) -> list[dict]:
    """Returns a list of events in leveldict of which searchfor is a subset.
    """
    matches = []
    for i in leveldict["actions"]:
        if searchfor.items() <= i.items():
            matches.append(i)
 
    for i in leveldict["decorations"]:
        if searchfor.items() <= i.items():
            matches.append(i)

    return matches

def removeEvents(searchfor : dict, leveldict : dict) -> list[dict]:
    """Removes all events in leveldict of which searchfor is a subset.
    This function directly modifies leveldict.
    Returns a list of removed events.
    """
    matches = []
    for i in leveldict["actions"]:
        if searchfor.items() <= i.items():
            matches.append(i)
            leveldict["actions"].remove(i)
 
    for i in leveldict["decorations"]:
        if searchfor.items() <= i.items():
            matches.append(i)
            leveldict["actions"].remove(i)

    return matches

def replaceField(searchfor : dict, field : str, new, leveldict : dict) -> None:
    """Changes the value of "field" to "new" in all events containing "searchfor"
    This function directly modifies leveldict.
    """
    eventlist = removeEvents(searchfor, leveldict)
    for i in range(len(eventlist)):
        if field in eventlist[i]:
            eventlist[i][field] = new

    for i in eventlist:
        filedict = addEvent(i,filedict)

def writeToFile(leveldict : dict, filename : str) -> None:
    """Writes the file dictionary to the specified file.
    """
    
    filestring = json.dumps(leveldict, indent=4)
    with open(filename, "w", encoding="utf-8-sig") as f:
        f.write(filestring)

def setSpeed() -> None:
    try:
        raise DeprecationWarning
    except DeprecationWarning as dp:
        print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def twirl() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def checkpoint() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def setHitsound() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def playSound() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def setPlanetRotation() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def pause() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def autoPlayTiles() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def scalePlanets() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def colorTrack() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def animateTrack() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def recolorTrack() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def moveTrack() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def positionTrack() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def moveDecorations() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def setText() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def customBackground() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def flash() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def moveCamera() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def setFilter() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def hallOfMirrors() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def shakeScreen() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def bloom() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def screenTile() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def screenScroll() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def repeatEvents() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def setConditionalEvents() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def setHoldSound() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def multiPlanet() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def hideJudgement() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def scaleMargin() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def scaleRadius() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def hold() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)

def addDecoration() -> None:
	try:
		raise DeprecationWarning
	except DeprecationWarning as dp:
		print("All event functions are deprecated after adofaipy 2.0.0. Directly pass a dictionary to addEvent() instead.", dp)
