import pm4py

from pm4py.objects.petri_net.utils import petri_utils

from mining_helper import *

from os import mkdir

#Generate BPMN Model from example xes files
if __name__ == "__main__":
    
    print('PM4Py Version: ' + pm4py.__version__)
    
    finalModelEventLogPath ='C:/Users/alfer/Desktop/Dev Projects/ba-obs-pm/xes_export/discovery_with_new_classifier_utc_14_02.xes'
    
    log = pm4py.read_xes('C:/Users/alfer/Desktop/Dev Projects/ba-obs-pm/xes_export/discovery2_faultfree.xes')
    
    iterI= True
    iterII= iterI and True
    iterIII= iterII and True
    iterIV = True
    
    alphaAlg = False
    
    filtered_log = log
    if iterI and not iterIV:
        filtered_log =  pm4py.filter_event_attribute_values(filtered_log, 'lifecycle:transition', ['start'], level='event', retain=True)
    if iterII:
        filtered_log = pm4py.filter_event_attribute_values(filtered_log, 'concept:name', ['/api/fights', '/api/fights/randomfighters'])
    if iterIII:
        #filtered_log = pm4py.filter_variants_top_k(filtered_log, 10)
        filtered_log = pm4py.filter_directly_follows_relation(filtered_log, [('/api/heroes/random','HeroService.findRandomHero'),('/api/villain/random', 'VillainService.findRandomVillain'), ('/api/fights', 'fights send') ])
    #filtered_log = pm4py.filter_start_activities(filtered_log, ['/api/fights', '/api/fights/randomfighters'])
    
    if alphaAlg:
        # Model is really bad...
        # does not show the two branches :(
        petri_net= discoverPetriNetAlphaPlus(filtered_log, True)
        
    bpmn_model = createBpmnModelFromLog(filtered_log, True)
    
    # keine neuen Informationen...
    #transition_system = pm4py.discover_transition_system(log, view='multiset')
    #pm4py.view_transition_system(transition_system)
    
    processMap = discoverProcessMap(filtered_log, True)
    
    #processMapPerf = discoverProcessDFGPerf(filtered_log, True)
    
    process_tree = discoverProcessTreeInductive(filtered_log)
    
    petri_net, im, fm = discoverPetriNet(filtered_log, True)
    if False:
        transition = petri_utils.get_transition_by_name(petri_net, 'VillainService.findRandomVillain')
        print(transition)
    
    ## Model Quality 
    
    printModelQ = False
    
    pathModelQ = './process_mining/discovery'
    try:
        os.makedirs(pathModelQ)
    except FileExistsError:
    # directory already exists
        pass
    
    fitness = pm4py.fitness_token_based_replay(log,petri_net, im, fm)
    writeJsonFile(fitness, pathModelQ + "/log_fitness")
    
    conformance_diagnostics = pm4py.conformance_diagnostics_token_based_replay(log,petri_net, im, fm)
    unfitting_traces = [trace for trace in conformance_diagnostics if not trace.get('trace_is_fit')]
    if printModelQ:
        print('unfitting Traces: ' + str(len(unfitting_traces)))
        for trace_diagnostic in unfitting_traces: 
            print(trace_diagnostic)
         
    (unfitting_traces_discovery, fitting_traces_discovery) = exportConformanceDiagnosisAsJson(conformance_diagnostics, pathModelQ)

    ## Conformance Checking
    
    faulty_log = pm4py.read_xes('C:/Users/alfer/Desktop/Dev Projects/ba-obs-pm/xes_export/example.xes')
    
    if iterI and not iterIV:
        faulty_log =  pm4py.filter_event_attribute_values(faulty_log, 'lifecycle:transition', ['start'], level='event', retain=True)
    if iterII:
        faulty_log = pm4py.filter_event_attribute_values(faulty_log, 'concept:name', ['/api/fights', '/api/fights/randomfighters'])
    if iterIII:
        #filtered_log = pm4py.filter_variants_top_k(filtered_log, 10)
        faulty_log = pm4py.filter_directly_follows_relation(faulty_log, [('/api/heroes/random','HeroService.findRandomHero'),('/api/villain/random', 'VillainService.findRandomVillain'), ('/api/fights', 'fights send') ])
    #filtered_log = pm4py.filter_start_activities(filtered_log, ['/api/fights', '/api/fights/randomfighters'])
    
    
    printConfCh = False
    
    pathConfCh = './process_mining/conf_checking'
    try:
        os.makedirs(pathConfCh)
    except FileExistsError:
    # directory already exists
        pass
    
    fitness = pm4py.fitness_token_based_replay(faulty_log,petri_net, im, fm)
    writeJsonFile(fitness, pathConfCh + "/log_fitness")
    
    conformance_diagnostics = pm4py.conformance_diagnostics_token_based_replay(faulty_log,petri_net, im, fm)
    unfitting_traces = [trace for trace in conformance_diagnostics if not trace.get('trace_is_fit')]
    if printConfCh:
        print('unfitting Traces: ' + str(len(unfitting_traces)))
        for trace_diagnostic in unfitting_traces: 
            print(trace_diagnostic)
        
    (unfitting_traces, fitting_traces) = exportConformanceDiagnosisAsJson(conformance_diagnostics, pathConfCh)
    
    # Running Script Interactively: exec(open(mining.py).read())
    
    
    faultList = openCSV('faultcsv.csv')
    vFaults, fsFaults, fuFault = sortFaultList(faultList)
    
    print('IAm Ready to use')
    
    
    
