import pm4py

from mining_helper import *

#Generate BPMN Model from example xes files
if __name__ == "__main__":
    
    print('PM4Py Version: ' + pm4py.__version__)
    log = pm4py.read_xes('C:/Users/alfer/Desktop/Dev Projects/ba-obs-pm/xes_export/example.xes')
    
    #faulty_log = pm4py.read_xes('C:/Users/alfer/Desktop/Dev Projects/ba-obs-pm/xes_export/example.xes')
    
    bpmn_model = createBpmnModelFromLog(log)
    
    processMap = discoverProcessMap(log)
    
    process_tree = discoverProcessTree(log)
    
    petri_net, im, fm = discoverPetriNet(log)
    
    #rebuilding petri_net?
    
    # rebuilding event log?
    
    fitness = pm4py.fitness_token_based_replay(log,petri_net, im, fm)
    writeJsonFile(fitness, "./process_mining/checking_traces/log_fitness")
    
    conformance_diagnostics = pm4py.conformance_diagnostics_token_based_replay(log,petri_net, im, fm)
    unfitting_traces = [trace for trace in conformance_diagnostics if not trace.get('trace_is_fit')]
    print('unfitting Traces: ' + str(len(unfitting_traces)))
    for trace_diagnostic in unfitting_traces: 
        print(trace_diagnostic)
        
    print(str(conformance_diagnostics[0]))
    
    """for diagnostic in conformance_diagnostics:
        if not diagnostic.get('trace_is_fit'):
            print('______________________')
            print(diagnostic) """
    
    exportConformanceDiagnosisAsJson(conformance_diagnostics, "./process_mining/checking_traces")

    
    
    
    
