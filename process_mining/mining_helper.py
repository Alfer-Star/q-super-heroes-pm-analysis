import pm4py

import json

import shutil
import os


def createBpmnModelFromLog(log, view=False):
    process_model = pm4py.discover_bpmn_inductive(log)
    if view:
        pm4py.view_bpmn(process_model)
    return process_model
    
def discoverProcessTree(log, view = False):
    process_tree = pm4py.discover_process_tree_inductive(log)
    if view:
        pm4py.view_process_tree(process_tree)
    return process_tree

def discoverPetriNet(log, view = False):
    net, im, fm  = pm4py.discover_petri_net_inductive(log)
    if view:
        pm4py.view_petri_net(net)
    return net, im, fm
    
def discoverProcessMap(log, view = False):
    dfg, start_activities, end_activities = pm4py.discover_dfg_typed(log)
    if view:
        pm4py.view_dfg(dfg, start_activities, end_activities)
    return dfg, start_activities, end_activities
    
def filterActivities(event):
    log =  pm4py.filter_activities_rework()
    
    #TODO:
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
    
    unfitting_traces = [trace for trace in result if not trace.get('trace_is_fit')]
    fitting_traces = [trace for trace in result if trace.get('trace_is_fit')]
    
    for index, uTrace in enumerate(unfitting_traces):
        writeJsonFile(str(uTrace), unfittingDirectory+'/trace_'+str(index))
    for index, uTrace in enumerate(fitting_traces):
        writeJsonFile(str(uTrace), fittingDirectory+'/trace_'+str(index))
        
def writeJsonFile(content: str, filePath: str):
    file = open(filePath+'.json', 'w+')
    jsonStr = json.dumps(content)
    file.write(jsonStr)
    file.close()