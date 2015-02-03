#! /usr/bin/python

import cgi, os
import cgitb; cgitb.enable()
#import urllib
import WarGearLib.General as WGL
from cStringIO import StringIO
import sys
import csv

debug = True  #this value is ignored
debugString = ""
# redirect stdout because WGLib library prints a lot of debug info
old_stdout = sys.stdout
mystdout = StringIO()



# for testing
def handleFile(fileContents,form):
  wgmap = WGL.WGMap()
  wgmap.loadMapFromXMLString(fileContents)
  print "Content-Type:application/xml";
  #print "Content-Disposition: attachment; filename=\""+urllib.urlencode(fileName)+"\"\n\n";
  print "Content-Disposition: attachment; filename=\"out.xml\"\n";
  #print "Content-Type:application/octet-stream; name=\"FileName\"\r\n";
  #print "Content-Disposition: attachment; filename=\"FileName\"\r\n\n";
  print wgmap.writeXML()


def handleContinentsFromNeighborsForm(wgmap,args):
  global debugString
 
  '''
  args:
    0 - BaseRegex
    1 - BaseCSV
    2 - BaseContinent
    3 - NeighborRegex
    4 - NeighborCSV
    5 - NeighborContinent
    6 - continentValue
    7 - factoryType
    8 - continentPrefix
    9 - MaxDistance
    10 - FactoryTarget
  '''
  
  baseIDSet = getTerritorySet(wgmap,args[0],args[1],args[2])
  neighborIDSet = getTerritorySet(wgmap,args[3],args[4],args[5])


  debugString += "Continents From Neighbors\n base (IDs): "
  for ID in baseIDSet:
    debugString += str(ID) + " "
  debugString += "\n neighbor (IDs):"
  for ID in neighborIDSet:
    debugString += str(ID) + " "
  debugString += "\n"

  _neighborDistance = None
  bonus = None
  
  _continentPrefix = ""
  _factory = None
  _factoryType = None
  
  # should we just ahve these be empty strings.
  if (args[9] != ""):
    _neighborDistance = args[9]
  if (args[6] != ""):
    bonus = args[6]
  if (args[8] != ""):
    _continentPrefix = args[8]
  if (args[10] != ""):
    _factory = args[10]
  if (args[7] != ""):
    _factoryType = args[7]

  wgmap.continentsFromNeighbors(baseIDSet, bonus, neighborIds=neighborIDSet, neighborDistance=_neighborDistance, continentPrefix=_continentPrefix, factory=_factory, factoryType=_factoryType)

def getTerritorySet(wgmap,regex="",csvList="",continent=""): 
   
  global debugString
   
  IDSet = set()
   
  if (regex != ""):
    IDSet.update(wgmap.getTerritoryIDsFromNameRegex(regex))
   
    
  if (csvList != ""):
    for row in csv.reader([csvList]):
      for name in row:
        IDSet.add(wgmap.getTerritoryIDFromName(name))

  if (continent != ""):
    memberString = wgmap.getContinentMembersFromName(continent)
    for memberID in memberString.split(","):
      IDSet.add(int(memberID))
    
  debugString += "\n<br \>IDSet: "
  for id1 in IDSet:
    debugString += "\"" + str(id1) + "\" "
  debugString += "\n<br \>"
    
  return IDSet

def handleFactoryMakerForm(wgmap,args):
  '''
  args:
  0 - memberRegex
  1 - memberCSV
  2 - memberContinent
  3 - factoryRegex
  4 - factoryCSV
  5 - factoryContinent
  6 - factoryValue
  7 - factoryType
  8 - namePrefix
  '''

  memberSet = getTerritorySet(wgmap,args[0],args[1],args[2])
  factorySet = getTerritorySet(wgmap,args[3],args[4],args[5])
  factoryValue = args[6]
  factoryType = args[7]
  namePrefix = args[8]
  
  
  

  if namePrefix != "":
    namePrefix += "-"
  #print "memberset: ",memberSet
  #return

  for factory in factorySet:
    factoryTName = wgmap.getTerritoryNameFromID(factory)
    memberNames = wgmap.getTerritoryNameFromIDs(memberSet)
    membersName = ', '.join(memberNames)
    name = "FACTORY-" + namePrefix + factoryTName + "-" + membersName
    wgmap.addContinent(name,memberSet,bonus=factoryValue,factory=factory,factoryType=factoryType)
  
 
        
def handleDeleteContinent(wgmap,args):
  if (args[0] == ""):
    return;  
  wgmap.deleteContinent(args[0])
  
  
def handleAddBorders(wgmap, args):
  global debugString
  
  '''
  args:
    0 - fromCSVList
    1 - fromRegex
    2 - fromContinent
    3 - toCSVList
    4 - toRegex
    5 - toContinent
    6 - FTAttackModifier
    7 - FTDefenseModifier
    8 - TFAttackModifier
    9 - TFDefenseModifier
    10 - borderType
    11 - borderDirection
  '''
  
  fromIDSet = getTerritorySet(wgmap,args[0],args[1],args[2])
  toIDSet = getTerritorySet(wgmap,args[3],args[4],args[5])
    
    
  debugString += "Adding Borders\n from (IDs): "
  for ID in fromIDSet:
    debugString += str(ID) + " "
  debugString += "\n to (IDs):"
  for ID in toIDSet:
    debugString += str(ID) + " "
  debugString += "\n"

  ftaModifier = "0"
  ftdModifier = "0"
  tfaModifier = "0"
  tfdModifier = "0"
  bType = "Default"
  bDirection = "Two-way"
  
  if (args[6] != ""):
    ftaModifier = args[6]
  if (args[7] != ""):
    ftdModifier = args[7]
  if (args[8] != ""):
    tfaModifier = args[8]
  if (args[9] != ""):
    tfdModifier = args[9]
  if (args[10] != ""):
    bType = args[10]
  if (args[11] != ""):
    bDirection = args[11]
  
  
  wgmap.addBordersFromSetToSet(fromIDSet, toIDSet, 
                      ftattackmod=ftaModifier, ftdefendmod=ftdModifier,  
                      tfattackmod=tfaModifier, tfdefendmod=tfdModifier,  
                      borderType=bType, direction=bDirection )


  
def handleModifyBordersForm(wgmap, args):
  global debugString
  
  '''
  args:
    0 - fromCSVList
    1 - fromRegex
    2 - fromContinent
    3 - toCSVList
    4 - toRegex
    5 - toContinent
    6 - AttackModifier
    7 - DefenseModifier
    8 - borderType
    9 - borderDirection
  '''
  

  fromIDSet = getTerritorySet(wgmap,args[0],args[1],args[2])
  toIDSet = getTerritorySet(wgmap,args[3],args[4],args[5])
    
    
  debugString += "Modifying Borders\n from (IDs): "
  for ID in fromIDSet:
    debugString += str(ID) + " "
  debugString += "\n to (IDs):"
  for ID in toIDSet:
    debugString += str(ID) + " "
  debugString += "\n"

  aModifier = None
  dModifier = None
  bType = None
  bDirection = None
  
  if (args[6] != ""):
    aModifier = args[6]
  if (args[7] != ""):
    dModifier = args[7]
  if (args[8] != ""):
    bType = args[8]
  if (args[9] != ""):
    bDirection = args[9]
  
  
  wgmap.modifyBorders(fromIDSet, toIDSet, 
                      attackModifier=aModifier, defenseModifier=dModifier, 
                      borderType=bType, borderDirection=bDirection )
  
  
def handleSplitBordersForm(wgmap, args):
  global debugString
  
  '''
  args:
    0 - S1CSVList
    1 - S1Regex
    2 - S1Continent
    3 - S2CSVList
    4 - S2Regex
    5 - S2Continent
      '''
  

  S1IDSet = getTerritorySet(wgmap,args[0],args[1],args[2])
  S2IDSet = getTerritorySet(wgmap,args[3],args[4],args[5])
    
    
  debugString += "Spliting Borders\n S1(IDs): "
  for ID in S1IDSet:
    debugString += str(ID) + " "
  debugString += "\n S2 (IDs):"
  for ID in S2IDSet:
    debugString += str(ID) + " "
  debugString += "\n"

  wgmap.splitBorders(S1IDSet,S2IDSet)
  
  
def  handleAddFixedBonusContinents(wgmap,args):
  '''
  AddFixedBonusContinents;
  args:
  0 - BaseRegex
  1 - BaseCSV
  2 - BaseContinent
  3 - MemberRegex
  4 - MemberCSV
  5 - MemberContinent
  6 - FixedBonus
  7 - FactoryType
  8 - CNPrefix
  9 - NeighborDistance
  10 - FactoryTarget
  '''
  BaseIDSet = getTerritorySet(wgmap,args[0],args[1],args[2])
  MemberIDSet = getTerritorySet(wgmap,args[3],args[4],args[5])
 
  wgmap.addFixedBonusContinents(BaseIDSet,MemberIDSet,args[6],args[7],args[8],args[9],args[10])
  

def handleCollectorContinentsForm(wgmap, args):
  global debugString
  
  IDSet = getTerritorySet(wgmap,args[0],args[1],args[2])
  
  debugString += "Creating collectors from (IDs): "
  for ID in IDSet:
    debugString += str(ID) + " "
  debugString += "\n"
  wgmap.addCollectorContinents(IDSet,args[3],args[4])
  

def handleXMLFile(fileContents,form):
  global debug
  global debugString
  
  if form.getvalue('debug'):
    debug = True
  else:
    debug = False
    
  wgmap = WGL.WGMap()
  wgmap.loadMapFromXMLString(fileContents)
  
  sys.stdout = mystdout
  
  
  if 'cmdsToExecute' in form:
    C2E = form.getvalue('cmdsToExecute')
    for line in C2E.splitlines():
      debugString += "processing: "+line + "\n"
      ix1 = line.find(";")
      if ix1 > 0:
        functionName = line[0:ix1]
      else:
        functionName = line
      args = line[ix1+1:].split(";")
      debugString += "functionName: " + functionName + "\n"
      for arg in args:
        debugString += "arg: " + arg + "\n"
        
      if functionName == "deleteAllContinents":
        debugString += "executing: deleteAllContinents(False)\n"
        wgmap.deleteAllContinents(False)
        
      if functionName == "AddCollectorContinents":
        handleCollectorContinentsForm(wgmap,args)
      
      if functionName == "modifyBorders":
        handleModifyBordersForm(wgmap,args)
        
      if functionName == "ContinentsByNeighbors":
        handleContinentsFromNeighborsForm(wgmap,args)
      
      if functionName == "FactoryMaker":
        handleFactoryMakerForm(wgmap,args)
        
      if functionName == "DeleteContinent":
        handleDeleteContinent(wgmap,args)
        
      if functionName == "SplitBorders":
        handleSplitBordersForm(wgmap,args)
        
      if functionName == "AddFixedBonusContinents":
        handleAddFixedBonusContinents(wgmap,args)
      
      if functionName == "AddBorders":
        handleAddBorders(wgmap,args)
       
#    hb = form.getvalue('hordesBonus',"0")
#    hcs = form.getvalue("hordesContinentSuffix","")
#    br = form.getvalue('baseRegex',".*")
#    nr = form.getvalue('neighborRegex',".*")
#    wgmap.hordify(hb,hcs,br,nr)
                                
  sys.stdout = old_stdout
  
  if debug:
    print "Content-type: text/html\n"
    print  "Debug String:\n\n" + debugString + "\n\n"
    print  "WGLib Stdout:\n\n" + mystdout.getvalue() + "\n\n"       
    print  "Original Contents\n\n" +            fileContents     + "\n\n"     
    print "New Contents\n\n" 
    wgmap.printDOM()  
    print "\n\n"     
  else:                        
    print "Content-Type:application/xml"
  
   
    #print "Content-Type:application/octet-stream; name=\"out.xml\"";
    #print "Content-Disposition: attachment; filename=\""+urllib.urlencode(fileName)+"\"\n\n";
    print "Content-Disposition: attachment; filename=\"out.xml\"\n";
    #print "Content-Type:application/octet-stream; name=\"FileName\"\r\n";
    #print "Content-Disposition: attachment; filename=\"FileName\"\r\n\n";
    wgmap.printDOM()


#####################
# MAIN STARTS HERE
#####################


form = cgi.FieldStorage()

# Get filename here.
fileitem = form['filename']
#message = fileitem.filename
# Test if the file was uploaded
if fileitem.filename:
  # strip leading path from file name to avoid 
  # directory traversal attacks
  fn = os.path.basename(fileitem.filename)
  fileContents = fileitem.file.read()
  #handleFile(fileContents,form)
  handleXMLFile(fileContents,form)
  #message = 'The file "' + fn + '" was uploaded successfully'

else:
  print """\
  Content-Type: text/html\n
  <html>
  <body>
  <p>Error uploading file</p>
  </body>
  </html>
  """


#   
#print """\
##Content-Type: text/html\n
#<html>
#<body>
#   <p>%s</p>
#</body>
#</html>
#""" % (message,)