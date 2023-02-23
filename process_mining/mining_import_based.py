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

        pnmlPath = './process_mining/iterZero/IterZero_petri_net.pnml'
        filtered_log = log
        if iterI and not iterIV:
            filtered_log =  pm4py.filter_event_attribute_values(filtered_log, 'lifecycle:transition', ['start'], level='event', retain=True)
            pnmlPath = './process_mining/iterI/IterI_petri_net.pnml'
        if iterII:
            filtered_log = pm4py.filter_event_attribute_values(filtered_log, 'concept:name', ['/api/fights', '/api/fights/randomfighters'])
            pnmlPath = './process_mining/iterII/IterII_petri_net.pnml'
        if iterIII:
            filtered_log = pm4py.filter_directly_follows_relation(filtered_log, [('/api/heroes/random','HeroService.findRandomHero'),('/api/villain/random', 'VillainService.findRandomVillain'), ('/api/fights', 'fights send') ])
            pnmlPath = './process_mining/iterIII/IterIII_petri_net.pnml'
        if iterIV:
            pnmlPath = './process_mining/iterIV/IterIV_petri_net.pnml'

        petri_net, im, fm = pm4py.read_pnml(pnmlPath)

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
    
    
    
