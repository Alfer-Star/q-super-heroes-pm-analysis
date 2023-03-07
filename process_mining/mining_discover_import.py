import pm4py

from pm4py.objects.petri_net.utils import petri_utils

from mining_helper import *

from os import mkdir
#

import csv

#Generate BPMN Model from example xes files
if __name__ == "__main__":
    
    
    print('PM4Py Version: ' + pm4py.__version__)
    
    iterations = dict()
    iterations['IterZero']=[False,False,False,False,False]
    iterations['IterI'] = [True,False,False,False,False]
    iterations['IterII'] = [True,True,False,False,False]
    iterations['IterIII']=[True,True,True,False,False]
    iterations['IterIV']=[True,True,True,True,False]
    iterations['IterV']=[True,True,True,False,True]
    
    csvheader =  ['Iteration','percentfit', 'logfitness', 'traces', 'unfittingTraceslen', 'fittingTraceslen', 'withPTrans', 'missingVDataOperation', 'havingVDataOperation', 'withOtherFitnes', 'missingfighSendDataOperation' ]
    csvData = list()

    for name, boolList in iterations.items():
        print(name)
        print(boolList)
        iterI,iterII,iterIII,iterIV, iterV = boolList
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
            if not iterV:
                filtered_log = pm4py.filter_directly_follows_relation(filtered_log, [('/api/heroes/random','HeroService.findRandomHero'),('/api/villain/random', 'VillainService.findRandomVillain'), ('/api/fights', 'fights send') ])
            pnmlPath = './process_mining/iterIII/IterIII_petri_net.pnml' 
            # IterV uses iterIII PetriNet!
        if iterIV:
            pnmlPath = './process_mining/iterIV/IterIV_petri_net.pnml'
        

        petri_net, im, fm = pm4py.read_pnml(pnmlPath)
        
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

        csvData.append( [naming +'_original', round(fitness['perc_fit_traces'],4), round(fitness['log_fitness'],4),len(unfitting_traces_discovery_original)+ len(fitting_traces_discovery_original), len(unfitting_traces_discovery_original), len(fitting_traces_discovery_original)])
        ## Model Quality Discovery filtered Log
        
        pathModelQ = './process_mining/'+naming+'/discovery_filtered_'+naming
        try:
            os.makedirs(pathModelQ)
        except FileExistsError:
        # directory already exists
            pass
        
        fitness = pm4py.fitness_token_based_replay(filtered_log,petri_net, im, fm)
        writeJsonFile(fitness, pathModelQ + "/log_fitness")
        
        conformance_diagnostics = pm4py.conformance_diagnostics_token_based_replay(log,petri_net, im, fm)         
        (unfitting_traces_discovery, fitting_traces_discovery) = exportConformanceDiagnosisAsJson(conformance_diagnostics, pathModelQ)

        csvData.append( [naming +'_filtered', round(fitness['perc_fit_traces'],4), round(fitness['log_fitness'],4),len(unfitting_traces_discovery)+ len(fitting_traces_discovery), len(unfitting_traces_discovery), len(fitting_traces_discovery)])
    
    csvheader =  ['Iteration','percentfit', 'logfitness', 'traces', 'unfittingTraceslen', 'fittingTraceslen' ]
    with open('./process_mining/IterationDiscTable.csv', 'w+', encoding='UTF-8', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(csvheader)
        writer.writerows(csvData)