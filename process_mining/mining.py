import pm4py

from mining_helper import *

#Generate BPMN Model from example xes files
if __name__ == "__main__":
    
    print('PM4Py Version: ' + pm4py.__version__)
    
    finalModelEventLogPath ='C:/Users/alfer/Desktop/Dev Projects/ba-obs-pm/xes_export/discovery_with_new_classifier_utc_14_02.xes'
    
    log = pm4py.read_xes('C:/Users/alfer/Desktop/Dev Projects/ba-obs-pm/xes_export/example.xes')
    
    #faulty_log = pm4py.read_xes('C:/Users/alfer/Desktop/Dev Projects/ba-obs-pm/xes_export/example.xes')
    
    filtered_log = pm4py.filter_event_attribute_values(log, 'lifecycle:transition', ['complete'], level='event')
    filtered_log = pm4py.filter_start_activities(filtered_log, ['/api/fights', '/api/fights/randomfighters'])
    filtered_log = pm4py.filter_event_attribute_values(filtered_log, 'lifecycle:transition')
    #filtered_log = log
    
    bpmn_model = createBpmnModelFromLog(filtered_log, True)
    
    # keine neuen Informationen...
    #transition_system = pm4py.discover_transition_system(log, view='multiset')
    #pm4py.view_transition_system(transition_system)
    
    processMap = discoverProcessMap(filtered_log, True)
    
    #processMapPerf = discoverProcessDFGPerf(filtered_log, True)
    
    process_tree = discoverProcessTree(filtered_log)
    
    petri_net, im, fm = discoverPetriNet(filtered_log)
    
    #rebuilding petri_net?
    
    # rebuilding event log?
    
    fitness = pm4py.fitness_token_based_replay(log,petri_net, im, fm)
    writeJsonFile(fitness, "./process_mining/checking_traces/log_fitness")
    
    conformance_diagnostics = pm4py.conformance_diagnostics_token_based_replay(log,petri_net, im, fm)
    unfitting_traces = [trace for trace in conformance_diagnostics if not trace.get('trace_is_fit')]
    print('unfitting Traces: ' + str(len(unfitting_traces)))
    for trace_diagnostic in unfitting_traces: 
        print(trace_diagnostic)
        
    
    exportConformanceDiagnosisAsJson(conformance_diagnostics, "./process_mining/checking_traces")

    
    
    
    
