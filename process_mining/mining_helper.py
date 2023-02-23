import pm4py

import json

import shutil
import os


def createBpmnModelFromLog(log, view=False):
    process_model = pm4py.discover_bpmn_inductive(log)
    if view:
        pm4py.view_bpmn(process_model)
    return process_model

def createBpmnModelFromLog(log, view=False):
    process_model = pm4py.discover_bpmn_inductive(log)
    if view:
        pm4py.view_bpmn(process_model)
    return process_model
    
def discoverProcessTreeInductive(log, view = False):
    process_tree = pm4py.discover_process_tree_inductive(log)
    if view:
        pm4py.view_process_tree(process_tree)
    return process_tree

def discoverProcessTree(log, view = False):
    process_tree = pm4py.discover_prefix_tree(log)
    if view:
        pm4py.view_process_tree(process_tree)
    return process_tree

def discoverPetriNet(log, view = False):
    net, im, fm  = pm4py.discover_petri_net_inductive(log)
    if view:
        pm4py.view_petri_net(net)
    return net, im, fm

def discoverPetriNetAlphaPlus(log, view = False):
                # Model is really bad...
            # does not show the two branches :(
    net, im, fm  = pm4py.discover_petri_net_alpha_plus(log)
    if view:
        pm4py.view_petri_net(net)
    return net, im, fm
    
def discoverProcessMap(log, view = False):
    dfg, start_activities, end_activities = pm4py.discover_dfg(log)
    if view:
        pm4py.view_dfg(dfg, start_activities, end_activities)
    return dfg, start_activities, end_activities

def discoverProcessDFGPerf(log, view = False):
    dfg, start_activities, end_activities = pm4py.discover_performance_dfg(log)
    if view:
        pm4py.view_dfg(dfg, start_activities, end_activities)
    return dfg, start_activities, end_activities
    
def filterActivities(event):
    log =  pm4py.filter_activities_rework()
    
    dfRelation = [('/api/fights/randomfighters')] 
    
    pm4py.filter_directly_follows_relation(log,dfRelation)
    
    pm4py.filter_eventually_follows_relation(log,dfRelation)
    
    return log 

def exportConformanceDiagnosisAsJson(result: list, pathToDirectory: str):
    unfittingDirectory = pathToDirectory+'/unfitting_traces'
    fittingDirectory= pathToDirectory+ '/fitting_traces'
    if os.path.isdir(unfittingDirectory):
        shutil.rmtree(unfittingDirectory)
    if os.path.isdir(fittingDirectory):
        shutil.rmtree(fittingDirectory)
    
    os.mkdir(unfittingDirectory)
    os.mkdir(fittingDirectory)
    
    unfitting_traces = list()
    fitting_traces= list()
    for index, trace in enumerate(result):
        if not trace.get('trace_is_fit'):
            unfitting_traces.append(trace)
            writeJsonFile(str(trace), unfittingDirectory+'/trace_'+str(index))
        else:
            fitting_traces.append(trace)
            writeJsonFile(str(trace), fittingDirectory+'/trace_'+str(index))
        
    return unfitting_traces, fitting_traces
        
def writeJsonFile(content: str, filePath: str):
    file = open(filePath+'.json', 'w+')
    jsonStr = json.dumps(content)
    file.write(jsonStr)
    file.close()
    
import csv
def openCSV(path):
    with open(path, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data

def sortFaultList(faultList: list):
    vFaults = [fault for fault in faultList if str(fault[0]).startswith('VillianFault')]
    fSwitchedFault = [fault for fault in faultList if str(fault[0]).startswith('fighterSwitched')]
    fUndefinedFault = [fault for fault in faultList if str(fault[0]).startswith('fighterUndefined')]
    return vFaults, fSwitchedFault, fUndefinedFault