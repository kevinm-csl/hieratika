#!/usr/bin/env python
__copyright__ = """
    Copyright 2017 F4E | European Joint Undertaking for ITER and
    the Development of Fusion Energy ('Fusion for Energy').
    Licensed under the EUPL, Version 1.1 or - as soon they will be approved
    by the European Commission - subsequent versions of the EUPL (the "Licence")
    You may not use this work except in compliance with the Licence.
    You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
 
    Unless required by applicable law or agreed to in writing, 
    software distributed under the Licence is distributed on an "AS IS"
    basis, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
    or implied. See the Licence permissions and limitations under the Licence.
"""
__license__ = "EUPL"
__author__ = "Andre' Neto"
__date__ = "17/11/2017"

##
# Standard imports
##
import ast
import ConfigParser
import fnmatch
import logging
import os
import shutil
import time
import timeit
import threading
from xml.etree import cElementTree
from xml.dom import minidom

##
# Project imports
##
from hieratika.server import HieratikaServer
from hieratika.page import Page
from hieratika.schedule import Schedule
from hieratika.util.lockpool import LockPool
from hieratika.variable import Variable

##
# Logger configuration
##
log = logging.getLogger("{0}".format(__name__))

##
# Class definition
##
class PSPSServer(HieratikaServer):
    """ Access must be multiprocess and multithread safe.
    """

    #Xml namespaces
    xmlns = {"ns0": "http://www.iter.org/CODAC/PlantSystemConfig/2014",
             "xsi": "http://www.w3.org/2001/XMLSchema-instance"}

    def __init__(self):
        super(PSPSServer, self).__init__()
        self.xmlIds = {}
        #cachedXmls is local to each process since cElementTree cannot be pickled by the multiprocessing Manager
        self.cachedXmls = {}
        self.recordTag = "{{{0}}}record".format(self.xmlns["ns0"])

    def load(self, manager, config):
        ok = True
        try:
            self.pages = manager.list()
            numberOfLocks = config.getint("server-impl", "numberOfLocks")
            self.maxXmlIds = config.getint("server-impl", "maxXmlIds")
            self.maxXmlCachedTrees = config.getint("server-impl", "maxXmlCachedTrees")
            self.baseDir = config.get("server-impl", "baseDir")
            self.standalone = config.getboolean("server-impl", "standalone")
            self.defaultExperts = ast.literal_eval(config.get("server-impl", "defaultExperts"))
            self.lockPool = LockPool(numberOfLocks, manager)
            #This is to protect the local resources cachedXmls and xmlIds (which are local to the process)
            self.mux = threading.Lock() 
            self.loadPages()
        except (ConfigParser.Error, KeyError) as e:
            log.critical(str(e))
            ok = False 
    
        return ok

    def getXmlId(self, xmlPath):
        """ Creates a unique key and associates it to an xml file path. (needed to have shorter keys as path may potentially be very long).
            Args:
                xmlPath(str): path to the xml file.
            Returns:
                A key which univocally identifies this xml path. 
        """
        self.mux.acquire()
        if (len(self.xmlIds) > self.maxXmlIds):
            log.info("Reached maximum number of cached xmlIds :{0}".format(self.maxXmlIds))
            keys = self.xmlIds.keys()
            for k in keys:
                if (not self.lockPool.isKeyInUse(self.xmlIds[k])):
                    del(self.xmlIds[k])
            log.info("After cleaning the number of cached xmlIds is {0}".format(len(self.xmlIds)))

        try:
            ret = self.xmlIds[xmlPath]
        except KeyError:
            ret = str(time.time())
            self.xmlIds[xmlPath] = ret
        self.mux.release()
        return ret

    def findVariableInXml(self, xmlRoot, variableName):       
        """ Walks the xml tree and finds a given variable.
            Args:
                xmlRoot (xmlElement): xml element pointing at the root of the psps file.
            Returns:
                An xmlElement poiting at the variable identified by variableName (using the @ symbol as a separator for folders).
        """
        idx = variableName.find("@")
        if (idx != -1):
            plantSystemName = variableName[:idx]
            variableName = variableName[idx + 1:]
            path = variableName.split("@")
        else:
            plantSystemName = variableName
            path = []
           
        plantRootXml = xmlRoot.find("./ns0:plantSystems/ns0:plantSystem[ns0:name='{0}']".format(plantSystemName), self.xmlns)
        if (plantRootXml is not None):
            r = plantRootXml
            #Skip the plantRecords (iff the length of the path is > 0 since I might need to read the name and the description before plantRecords)
            if (len(path) > 0):
                pr = r.find("./ns0:plantRecords", self.xmlns)
                if (pr is not None):
                    r = pr
            for i, p in enumerate(path):
                memberFound = False
                #Check if it is pointing at records
                records = r.find("./ns0:records", self.xmlns)
                if (records is None):
                    #Then must have a folder with this member name
                    r = r.find("./ns0:folders", self.xmlns)
                    if (r is None):
                        log.critical("Wrong xml structure. ns0:folders is missing")
                        return None
                    else:
                        folders = r.findall("./ns0:folder", self.xmlns)
                        for f in folders:
                            n = f.find("./ns0:name", self.xmlns)
                            if (n is not None):
                                folderName = n.text
                                if (folderName == p):
                                    #Found the folder with this member name. Continue.
                                    r = f
                                    memberFound = True
                                    break
                            else:
                                log.critical("Wrong xml structure. ns0:name is missing in folder")
                else:
                    #Reached a record. This must the last name of the variable!
                    if (i != (len(path) - 1)):
                        log.critical("Wrong xml structure. ns0:records were not expected at this location for variable {0}".format(variableName))
                        return None
                    records = records.findall("./ns0:record", self.xmlns)
                    for rec in records:
                        n = rec.find("./ns0:name")
                        if (n is not None):
                            recordName = n.text
                            if (p == recordName):
                                r = rec
                                memberFound = True
                                break
                        else:
                            log.critical("Wrong xml structure. ns0:name is missing in record")
                if (not memberFound):
                    log.critical("Could not find member {0} for variable {1}".format(p, variableName))
        return r


    def createVariableFromRecord(self, rec):
        """ Helper function to create a Variable from a psps record.
            Args:
                rec (xmlElement): xml Element pointing at ns0:record.
            Returns:
                A Variable constructed from the ns0:record elements
        """
        try:
            nameXml = rec.find("./ns0:name", self.xmlns)
            aliasXml = rec.find("./ns0:alias", self.xmlns)
            typeFromXml = self.convertVariableTypeFromXml(rec.attrib["{" + self.xmlns["xsi"] + "}type"])
            descriptionXml = rec.find("./ns0:description", self.xmlns)
            valuesXml = rec.find("./ns0:values", self.xmlns)
            valueXml = valuesXml.find("./ns0:value", self.xmlns)
            value = []
            if (valueXml is not None):
                value = ast.literal_eval(valueXml.text)
            if (not isinstance(value, list)):
                value = [value]
            numberOfElements = ast.literal_eval(rec.attrib["size"])
            #TODO handle permissions in xml (currently only the default ones are supported)
            variable = Variable(nameXml.text, aliasXml.text, typeFromXml, descriptionXml.text, self.defaultExperts, numberOfElements, value)
            log.debug("Loaded {0}".format(variable))
        except Exception as e:
            #Not very elegant to catch all the possible exceptions...
            log.critical("Wrong xml structure. {0}".format(e))
            variable = None
        return variable

    def getVariableInfo(self, r, parent):
        """ Recursively gets all the variable information, including information of any member variables.
            
            Args:
                r (xmlElement): points at the current the xml Element in the tree. 
                parent (Variable): the Variable to which this variable should be added as a member.

            Returns:
                The fully populated (including any member substructures) parent Variable.
        """
        #At this point the xml can only be pointing at a set of records or at a list of folders (the case where it is pointing at the record must be trapped before)
        records = r.find("./ns0:records", self.xmlns)
        if (records is None):
            r = r.find("./ns0:folders", self.xmlns)
            if (r is not None):
                folders = r.findall("./ns0:folder", self.xmlns)
                for f in folders:
                    n = f.find("./ns0:name")
                    if (n is not None):
                        member = Variable(n.text, n.text, "", "")
                        parent.addMember(member)
                        self.getVariableInfo(f, member)
                    else:
                        log.critical("Wrong xml structure. ns0:name is missing in folder")
                else:
                    log.critical("Wrong xml structure. ns0:folders is missing in folder")
        else:
            records = records.findall("./ns0:record", self.xmlns)
            for rec in records:
                member = self.createVariableFromRecord(rec) 
                if (member is not None):
                    if (parent is None):
                        parent = member
                    else:
                        parent.addMember(member)
                else:
                    return None

        return parent

    def getVariablesInfo(self, pageName, requestedVariables):
        xmlFileLocation = "{0}/psps/configurations/{1}/000/plant.xml".format(self.baseDir, pageName)
        log.debug("Loading plant configuration from {0}".format(xmlFileLocation))
        perfStartTime = timeit.default_timer()
        variables = []
        xmlId = self.getXmlId(xmlFileLocation)
        self.lockPool.acquire(xmlId)
        tree = self.getCachedXmlTree(xmlFileLocation)

        if (tree is not None):
            xmlRoot = tree.getroot()
            for variableName in requestedVariables:
                variable = None
                r = self.findVariableInXml(xmlRoot, variableName)
                if (r.tag == self.recordTag): 
                    #If it pointing already inside a record just create the member variable (and set the name to the full path, so that it is clear that a variable may be part of a structure)
                    variable = self.createVariableFromRecord(r) 
                    if (variable is not None):
                        #Reset the parent to point at the member
                        variable.setName(variableName)
                else:
                    parentNameXml = r.find("./ns0:name", self.xmlns)
                    if (parentNameXml is not None):
                        parentName = parentNameXml.text
                    else:
                        parentName = ""
                    parentDescriptionXml = r.find("./ns0:description", self.xmlns)
                    if (parentDescriptionXml is not None):
                        parentDescription = parentDescriptionXml.text
                    else:
                        parentDescription = ""
                    #Set the name of the parent to the full path, so that it is clear that a variable may be part of a structure
                    parent = Variable(variableName, parentName, "", parentDescription)

                    #Skip the plantRecords (iff the length of the path is > 0 since I might need to read the name and the description before plantRecords)
                    pr = r.find("./ns0:plantRecords", self.xmlns)
                    if (pr is not None):
                        r = pr
                    #Recursively add all the variables information
                    variable = self.getVariableInfo(r, parent)
                    
                if (variable is not None):
                    variables.append(variable)
        self.lockPool.release(xmlId)
        perfElapsedTime = timeit.default_timer() - perfStartTime
        log.debug("Took {0} s to get the information for all the {1} variables in the plant for page {2}".format(perfElapsedTime, len(requestedVariables), pageName))
        return variables 

    def getPages(self):
        return self.pages

    def getPage(self, pageName):
        page = None
        try:
            idx = self.pages.index(pageName)
        except ValueError as e:
            log.critical("Failed to get page {0}".format(e))
            idx = -1
        if (idx >= 0):
            page = self.pages[idx]
        return page

    def getSchedules(self, username, pageName):
        schedules = []
        allSchedulesXml = self.getAllSchedulesXmls(username, pageName)

        for xmlFile in allSchedulesXml:
            description = ""
            xmlId = self.getXmlId(xmlFile)
            self.lockPool.acquire(xmlId)
            tree = self.getCachedXmlTree(xmlFile)
            if (tree is not None):
                xmlRoot = tree.getroot()
                description = xmlRoot.find("./ns0:description", self.xmlns)
                if (description is not None):
                    description = description.text
            self.lockPool.release(xmlId)
            filePath = xmlFile.split("/")
            name = filePath[-1]
            name = name.split(".xml")
            if (len(name) > 1):
                name = name[-2]
            schedule = Schedule(xmlFile, name, pageName, username, description)
            schedules.append(schedule);

        return schedules

    def getSchedule(self, scheduleUID):
        schedule = None
        xmlId = self.getXmlId(xmlFile)
        self.lockPool.acquire(xmlId)
        tree = self.getCachedXmlTree(xmlFile)
        if (tree is not None):
            xmlRoot = tree.getroot()
            description = xmlRoot.find("./ns0:description", self.xmlns)
            if (description is not None):
                description = description.text
            filePath = xmlFile.split("/")
            schedule = Schedule(xmlFile, filePath[-1], pageName, username, description)
        self.lockPool.release(xmlId)
        return schedule

    def getScheduleVariablesValues(self, scheduleUID):
        xmlId = self.getXmlId(scheduleUID)
        self.lockPool.acquire(xmlId)
        variables = self.getAllVariablesValues(scheduleUID)
        self.lockPool.release(xmlId)
        return variables

    def commitSchedule(self, tid, scheduleUID, variables):
        updatedVariables = {}
        xmlId = self.getXmlId(scheduleUID)
        self.lockPool.acquire(xmlId)
        for name in variables:
            value = variables[name]
            if(self.updateVariable(name, scheduleUID, value)):
                updatedVariables[name] = value

        tree = self.getCachedXmlTree(scheduleUID)
        tree.write(scheduleUID)
        self.lockPool.release(xmlId)
        return updatedVariables 

    def updatePlant(self, pageName, variables):
        updatedVariables = {}
        xmlPath = "{0}/psps/configurations/{1}/000/plant.xml".format(self.baseDir, pageName)
        xmlId = self.getXmlId(xmlPath)
        self.lockPool.acquire(xmlId)
        for name in variables:
            value = variables[name]
            if(self.updateVariable(name, xmlPath, value)):
                updatedVariables[name] = value
        tree = self.getCachedXmlTree(xmlPath)
        tree.write(xmlPath)
        self.lockPool.release(xmlId)
        return updatedVariables 

    def createSchedule(self, name, description, username, pageName, sourceScheduleUID):
        ok = True
        log.info("Creating a new schedule for user: {0} for page: {1} with name: {2}".format(username, pageName, name))
        if (sourceScheduleUID is None):
            sourceScheduleUID = "{0}/psps/configurations/{1}/000/plant.xml".format(self.baseDir, pageName)
            destFolderNumber = "000"
        else: 
            filePath = sourceScheduleUID.split("/")
            if (len(filePath) < 2):
                log.critical("Could not parse the sourceScheduleUID {0} to find the last folder name (which should be a number)".format(sourceScheduleUID))
                ok = False
            destFolderNumber = filePath[-2]

        if (ok):
            if (not name.endswith(".xml")):
                name = name + ".xml"
            if (self.standalone):
                destScheduleUID = "{0}/psps/configurations/{1}/{2}/{3}".format(self.baseDir, pageName, destFolderNumber, name)
            else:
                destScheduleUID = "{0}/users/{1}/configurations/{2}/{3}/{4}".format(self.baseDir, username, pageName, destFolderNumber, name)
            try:
                shutil.copy2(sourceScheduleUID, destScheduleUID) 
            except IOError as e:
                log.critical("Failed to create schedule {0}".format(e))
                ok = False

        if (ok):
            xmlId = self.getXmlId(destScheduleUID)
            self.lockPool.acquire(xmlId)
            tree = self.getCachedXmlTree(destScheduleUID)
            if (tree is not None):
                xmlRoot = tree.getroot()
                nameXml = xmlRoot.find("./ns0:name", self.xmlns)
                if (nameXml is not None):
                    nameXml.text = name 
                descriptionXml = xmlRoot.find("./ns0:description", self.xmlns)
                if (descriptionXml is not None):
                    descriptionXml.text = description
                tree.write(destScheduleUID)
                log.info("Created schedule with uid {0}".format(destScheduleUID))
            else:
                log.critical("Failed to create schedule with uid {0}".format(destScheduleUID))
            self.lockPool.release(xmlId)
        return destScheduleUID

    def convertVariableTypeFromXml(self, xmlVariableType):
        """ Helper function which converts a psps record type to a hieratika type.
        
        Args:
            xmlVariableType(str): the psps record type to convert.
        Returns:
            The hieratika converted type.
        """
        toReturn = "string"
        if (xmlVariableType == "recordDouble"):
            toReturn = "float64" 
        elif (xmlVariableType == "recordFloat"):
            toReturn = "float32" 
        elif (xmlVariableType == "recordString"):
            toReturn = "string" 
        else:
            log.critical("Could not convert type {0}".format(xmlVariableType))
        return toReturn

    def getAllSchedulesXmls(self, username, pageName):
        """ Helper function which gets all psps configurations associated to a given page for a given user.
       
        Args:
            username (str): the username to search.
            pageName (str): the configuration to search.
        Returns:
            All the schedules files found for a given configuration.
        """
        matches = []
        if (self.standalone):
            directory = "{0}/psps/configurations/{1}".format(self.baseDir, pageName)
        else:
            directory = "{0}/users/{1}/configurations/{2}".format(self.baseDir, username, pageName)
        for root, dirnames, filenames in os.walk(directory):
            for filename in fnmatch.filter(filenames, '*.xml'):
                if (filename != "plant.xml"):
                    matches.append(os.path.join(root, filename))
        return matches

    def loadPages(self):
        """ Loads the list of available pages (which corresponds to the number of different configurations)
        """
        directory = "{0}/psps/configurations/".format(self.baseDir)
        for root, dirnames, filenames in os.walk(directory):
            for dirname in dirnames:
                page = Page(dirname, dirname, dirname)
                self.pages.append(page)
                log.info("Registered page {0}".format(page))
            #Only want the first sub level
            break
    def getCachedXmlTree(self, xmlPath):
        """ Parses the xml defined by the xmlPath and caches it in memory.
            This method is not thread-safe and expects the methods acquire and release to be called by the caller.
            
            Args:
                xmlPath (str): path to the xml file to be parsed.
            Returns:
                The parsed Xml file or None if an error occurs.
        """
        self.mux.acquire()
        if (len(self.cachedXmls) > self.maxXmlCachedTrees):
            log.info("Reached maximum number of cached xml trees :{0} > {1}".format(len(self.cachedXmls), self.maxXmlCachedTrees))
            toDeleteMaxSize = (len(self.cachedXmls) / 2) + 1
            #Sort by access time. Remember that the values of cachedXmls are tupples containing the path, the parsed cElementTree and the last access time
            sortedByTime = sorted(self.cachedXmls.values(), key=lambda tup:tup[2])
            i = 0
            while i < toDeleteMaxSize:
                log.debug("Deleting xml (from memory) with key {0}".format(sortedByTime[i][0]))
                del(self.cachedXmls[sortedByTime[i][0]])
                i = i + 1
            log.info("After cleaning the number of cached xml is {0}".format(len(self.cachedXmls)))


        try:
            ret = self.cachedXmls[xmlPath][1]
            self.cachedXmls[xmlPath][2] = time.time()
        except Exception as e:
            try:
                #The xmlPath is also stored as value in order to accelerate the cleaning above
                self.cachedXmls[xmlPath] = (xmlPath, cElementTree.parse(xmlPath), time.time())
                ret = self.cachedXmls[xmlPath][1]
            except Exception as e:
                log.critical("Error loading xml file {0}: {1}".format(xmlPath, str(e)))
                ret = None
        self.mux.release()
        return ret

    def updateVariable(self, variableName, xmlPath, variableValue):
        """ Updates the value of the a variable in a given xml (plant or schedule).
            This method is not thread-safe and expects the methods acquire and release to be called by the caller.
            Note that this change is not sinked to disk.
    
        Args:
            variableName (str): the name of the variable to update.
            xmlPath (str): the xml to be updated (identified with the path to the original file).
            variableValue (str): the value of the variable to be updated.

        Returns:
            True if the variable is sucessfully updated.
        """

        #Allow only one process to interact with a given xml at the time
        #Makes sure that this is both multi-processing and multi-threading safe
        log.debug("Updating {0} in {1} with value {2}".format(variableName, xmlPath, variableValue))

        ok = False
        #Update the Xml
        tree = self.getCachedXmlTree(xmlPath)
        if (tree is not None):
            root = tree.getroot()
            #TODO for the time being I will encode the plant system name as the first @ token. This needs discussion at some stage
            idx = variableName.find("@")
            if (idx != -1):
                plantSystemName = variableName[:idx]
                variableName = variableName[idx + 1:]
                path = variableName.split("@")
               
                r = root.find("./ns0:plantSystems/ns0:plantSystem[ns0:name='{0}']/ns0:plantRecords".format(plantSystemName), self.xmlns)
                for p in path[:-1]:
                    r = r.find("./ns0:folders/ns0:folder[ns0:name='{0}']".format(p), self.xmlns)
                    if (r == None):
                        log.critical("Could not find {0} . Failed while looking for {1}".format(variableName, p))
                        break

                variable = {}
                if (r is not None):
                    r = r.find("./ns0:records/ns0:record[ns0:name='{0}']".format(path[-1]), self.xmlns)
                    if (r != None):
                        valueXml = r.find("./ns0:values/ns0:value", self.xmlns)
                        valueXml.text = str(variableValue)
                        ok = True
                    else:
                        log.critical("Could not find the record for variable {0}".format(variableName))
            else:
                log.critical("No plant system defined for variable {0}".format(variableName))

        return ok

    def getVariableValue(self, r, variableName, variables):
        """ Recursively gets all the variable values for a given plantSystem node in the xml.
            
            Args:
                r (xmlElement): walks the xml Tree. The first time this function is called it shall point at the plantRecords.
                variableName (str): the name of the variable. It is constructed as the function recursively walks the tree. The separator is the @ symbol.
                variables (__dict__): dictionary where the value of the variable is stored.
        """
        records = r.find("./ns0:records", self.xmlns)
        if (records is None):
            r = r.find("./ns0:folders", self.xmlns)
            if (r is None):
                log.critical("Wrong xml structure. ns0:folders is missing")
                return None
            else:
                folders = r.findall("./ns0:folder", self.xmlns)
                variableNameBeforeFolders = variableName
                for f in folders:
                    n = f.find("./ns0:name")
                    if (n is not None):
                        variableName = variableNameBeforeFolders + "@" + n.text
                        self.getVariableValue(f, variableName, variables)
                    else:
                        log.critical("Wrong xml structure. ns0:name is missing in folder")
        else:
            records = records.findall("./ns0:record", self.xmlns)
            variableNameBeforeRecord = variableName
            for rec in records:
                n = rec.find("./ns0:name")
                if (n is not None):
                    variableName = variableNameBeforeRecord + "@" + n.text
                    valuesXml = rec.find("./ns0:values", self.xmlns)
                    if (valuesXml is not None):
                        valueXml = valuesXml.find("./ns0:value", self.xmlns)
                        try:
                            value = ast.literal_eval(valueXml.text)
                        except Exception as e:
                            log.critical("Could not evaluate the value for variable with name {0}".format(variableName))
                        variables[variableName] = value
                else:
                    log.critical("Wrong xml structure. ns0:name is missing in record")
                log.debug("Retrieved value for variable [{0}]".format(variableName))

    def getAllVariablesValues(self, xmlPath):
        variables = {}
        tree = self.getCachedXmlTree(xmlPath)
        if (tree is not None):
            xmlRoot = tree.getroot()
            plantSystemsRootXml = xmlRoot.findall(".//ns0:plantSystem", self.xmlns)
            for plantSystemXml in plantSystemsRootXml:
                plantSystemName = plantSystemXml.find("./ns0:name", self.xmlns).text
                plantRecordsXml = plantSystemXml.find("./ns0:plantRecords", self.xmlns)
                self.getVariableValue(plantRecordsXml, plantSystemName, variables)
        return variables

