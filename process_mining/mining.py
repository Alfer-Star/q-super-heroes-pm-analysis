import pm4py

from pm4py.objects.petri_net.utils import petri_utils

from mining_helper import *

from os import mkdir
#


#Generate BPMN Model from example xes files
if __name__ == "__main__":
    
    
    print('PM4Py Version: ' + pm4py.__version__)
    
    iterations = dict()
    iterations['IterZero']=[False,False,False,False]
    iterations['IterI'] = [True,False,False,False]
    iterations['IterII'] = [True,True,False,False]
    iterations['IterIII']=[True,True,True,False]
    iterations['IterIV']=[True,True,True,True]

    for name, boolList in iterations.items():
        print(name)
        print(boolList)
        iterI,iterII,iterIII,iterIV = boolList
        naming =name
    
        log = pm4py.read_xes('C:/Users/alfer/Desktop/Dev Projects/ba-obs-pm/xes_export/discovery2_faultfree.xes')
        
        filtered_log = log
        if iterI and not iterIV:
            filtered_log =  pm4py.filter_event_attribute_values(filtered_log, 'lifecycle:transition', ['start'], level='event', retain=True)
        if iterII:
            filtered_log = pm4py.filter_event_attribute_values(filtered_log, 'concept:name', ['/api/fights', '/api/fights/randomfighters'])
        if iterIII:
            filtered_log = pm4py.filter_directly_follows_relation(filtered_log, [('/api/heroes/random','HeroService.findRandomHero'),('/api/villain/random', 'VillainService.findRandomVillain'), ('/api/fights', 'fights send') ])

            
        exportPath = 'process_mining/' +naming + '/' 
        
        try:
            os.makedirs(exportPath)
        except FileExistsError:
        # directory already exists
            pass
            
        bpmn_model = createBpmnModelFromLog(filtered_log, True)
        pm4py.write_bpmn(bpmn_model, exportPath+naming+'_bpmn_model')
        pm4py.save_vis_bpmn(bpmn_model, exportPath+naming+'_bpmn_model')
        
        dfg, start_activities, end_activities = discoverProcessMap(filtered_log, True)
        #pm4py.write_dfg(dfg,start_activities, end_activities,exportPath+naming+'_dfg')
        pm4py.save_vis_dfg(dfg, start_activities, end_activities, end_activities,exportPath+naming+'_dfg')
        
        petri_net, im, fm = discoverPetriNet(filtered_log, True)
        pm4py.write_pnml(petri_net, im, fm, exportPath+naming+'_petri_net')
        pm4py.save_vis_petri_net(petri_net, im, fm, exportPath+naming+'_petri_net')
        
        if False:
            transition = petri_utils.get_transition_by_name(petri_net, 'VillainService.findRandomVillain')
            print(transition)
            
            
        
        ## Model Quality Discovery original Log

        pathModelQ = './process_mining/'+naming+'/discovery_original_'+naming
        try:
            os.makedirs(pathModelQ)
        except FileExistsError:
        # directory already exists
            pass
        
        fitness = pm4py.fitness_token_based_replay(log,petri_net, im, fm)
        writeJsonFile(fitness, pathModelQ + "/log_fitness")
        
        conformance_diagnostics = pm4py.conformance_diagnostics_token_based_replay(log,petri_net, im, fm)
        (unfitting_traces_discovery_original, fitting_traces_discovery_original) = exportConformanceDiagnosisAsJson(conformance_diagnostics, pathModelQ)

        ## Model Quality Discovery filtered Log
        
        pathModelQ = './process_mining/'+naming+'/discovery_filtered_'+naming
        try:
            os.makedirs(pathModelQ)
        except FileExistsError:
        # directory already exists
            pass
        
        fitness = pm4py.fitness_token_based_replay(log,petri_net, im, fm)
        writeJsonFile(fitness, pathModelQ + "/log_fitness")
        
        conformance_diagnostics = pm4py.conformance_diagnostics_token_based_replay(log,petri_net, im, fm)         
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
        
        pathConfCh = './process_mining/'+naming+'/conf_checking_'+naming
        try:
            os.makedirs(pathConfCh)
        except FileExistsError:
        # directory already exists
            pass
        
        fitness = pm4py.fitness_token_based_replay(faulty_log,petri_net, im, fm)
        writeJsonFile(fitness, pathConfCh + "/log_fitness")
        
        conformance_diagnostics = pm4py.conformance_diagnostics_token_based_replay(faulty_log,petri_net, im, fm)
        unfitting_traces = [trace for trace in conformance_diagnostics if not trace.get('trace_is_fit')]
            
        (unfitting_traces, fitting_traces) = exportConformanceDiagnosisAsJson(conformance_diagnostics, pathConfCh)
    
    faultList = openCSV('./process_mining/faultcsv.csv')
    vFaults, fsFaults, fuFault = sortFaultList(faultList)
    
    # Running Script Interactively: exec(open('mining.py').read())
    print('I am ready to use!')
    
    
    
