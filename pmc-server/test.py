import argparse

import Queue

import threading

import epics
from epics import caget, caput, camonitor

import time

import json

from flask import Flask, Response, request, send_from_directory


app = Flask(__name__, static_url_path="")

#list of variables to monitor
#plantVariablesToMonitor = [epics.PV("PMC::TEST::VAR1"), epics.PV("PMC::TEST::VAR2"), epics.PV("PMC::TEST::VAR3"), epics.PV("PMC::TEST::VAR4")]

#live database simulating the plant
plantVariablesDB = []


#Synchronised queue between the SSE stream_data function and the pvValueChanged. One queue per consumer thread. Should be further protected with semaphores
threadQueues = {}

#see http://cars9.uchicago.edu/software/python/pyepics3/pv.html#pv-callbacks-label for other arguments that could be retrieved
def pvValueChanged(pvname=None, value=None, **kw):
    for k, q in threadQueues.iteritems():
        q.put((pvname, value), True)

def updatePlantVariablesDB(pvName, pvValue):
    for pv in plantVariablesDB:
        if (pv["name"] == pvName):
            pv["value"] = pvValue
            break


#Call back for the Server Side Event. One per connection will loop on the while and consume from its own queue
def streamData():
    try:
        while True:
            tid = str(threading.current_thread())
            if tid not in threadQueues:
                # The first time send all the variables
                threadQueues[tid] = Queue.Queue()
                encodedPy = {"plantVariables": [ ] }
                for pv in plantVariablesDB:
                    pvName = pv["name"]
                    value = pv["value"]
                    encodedPy["plantVariables"].append({"name" : pvName, "value" : value})
                encodedJson = json.dumps(encodedPy)
            else:
                # Just monitor on change 
                monitorQueue = threadQueues[tid]
                print monitorQueue
                updatedPV = monitorQueue.get(True)
                pvName = updatedPV[0]
                pvValue = updatedPV[1]
                encodedPy = {"plantVariables": [ {"name" : pvName, "value" : pvValue}] }
                encodedJson = json.dumps(encodedPy)
                monitorQueue.task_done()
                print encodedJson 
            yield "data: {0}\n\n".format(encodedJson)
    except Exception:
        print "Exception ignored"
        #ignore

#Gets all the pv information
@app.route("/getplantinfo")
def getplantinfo():
    encodedPy = {"variables": plantVariablesDB }
    encodedJson = json.dumps(encodedPy)
    print encodedJson
    return encodedJson
  
#Try to update the values in the plant
@app.route("/submit", methods=["POST", "GET"])
def submit():
    if (request.method == "GET"):
        updateJSon = request.args["update"]
        print updateJSon
        jSonUpdateVariables = json.loads(updateJSon)
        for varName in jSonUpdateVariables:
            newValue = jSonUpdateVariables[varName]
            print str(newValue)
            updatePlantVariablesDB(varName, newValue)
            #Warn others that the plant values have changed!
            for k, q in threadQueues.iteritems():
                q.put((varName, newValue), True)

            #caput(k, request.args[k])
    return "done"

#Return the available schedules
@app.route("/getschedules")
def getschedules():
    scheduleNames = []
    with open("static/schedules.json") as jsonFile:
        schedulesJson = json.load(jsonFile)
        schedules = schedulesJson["schedules"]
        for s in schedules:
            scheduleNames.append(s["name"]);
    return json.dumps(scheduleNames)

#Return the available libraries
@app.route("/getlibraries")
def getlibraries():
    librariesNames = []
    with open("static/libraries.json") as jsonFile:
        librariesJson = json.load(jsonFile)
        libraries = librariesJson["libraries"]
        for a in libraries:
            varName = a["variable"]
            varLibraries = a["libraries"]

            varInfo = {}
            varInfo["variable"] = varName
            varInfo["names"] = []
            for va in varLibraries:
                varInfo["names"].append(va["name"])

            librariesNames.append(varInfo)
    return json.dumps({"libraries": librariesNames})

#Returns the library information associated to a given variable
@app.route("/getlibrary", methods=["POST", "GET"])
def getlibrary():
    values = {}
    if (request.method == "GET"):
        requestedVariable = request.args["variable"]
        requestedLibraryName = request.args["libraryName"]
        with open("static/libraries.json") as jsonFile:
            librariesJson = json.load(jsonFile)
            allLibraries = librariesJson["libraries"]
            for v in allLibraries:
                if (v["variable"] == requestedVariable):
                    variableLibraries = v["libraries"]
                    for a in variableLibraries:
                        if (a["name"] == requestedLibraryName):
                            values = a["values"]
                            break
                    break
    return json.dumps(values)


#Returns the variables associated to a given schedule
@app.route("/getschedule", methods=["POST", "GET"])
def getschedule():
    if (request.method == "GET"):
        requestedSchedule = request.args["schselect"]
        with open("static/schedules.json") as jsonFile:
            schedulesJson = json.load(jsonFile)
            schedules = schedulesJson["schedules"]
            for s in schedules:
                if (s["name"] == requestedSchedule):
                    variables = s["variables"]
                    break
    return json.dumps(variables)


@app.route("/stream")
def stream():
    return Response(streamData(), mimetype="text/event-stream")

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/tmp/<filename>")
def tmp(filename):
    return send_from_directory('tmp', filename)

if __name__ == "__main__":
    epics.ca.find_libca()
    
    parser = argparse.ArgumentParser(description = "Flask http server to prototype ideas for ITER level-1")
    parser.add_argument("-H", "--host", default="127.0.0.1", help="Server port")
    parser.add_argument("-p", "--port", type=int, default=5000, help="Server IP")

    args = parser.parse_args()

    with open("plant-variables.json") as jsonFile:
        plantVariablesDBJSon = json.load(jsonFile)
        #Assume the first plant for the time being
        plantVariablesDB = plantVariablesDBJSon["plants"][0]["variables"]
        

    for pv in plantVariablesDB:
        pv["value"] = pv["initialValue"]
        if pv["epicsPV"] == "true":
            camonitor(pv["name"], None, pvValueChanged)

    app.debug = True
    app.run(threaded= True, host=args.host, port=args.port)
