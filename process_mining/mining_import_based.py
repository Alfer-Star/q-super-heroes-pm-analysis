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
            filtered_log = pm4py.filter_directly_follows_relation(filtered_log, [('/api/heroes/random','HeroService.findRandomHero'),('/api/villain/random', 'VillainService.findRandomVillain'), ('/api/fights', 'fights send') ])
            pnmlPath = './process_mining/iterIII/IterIII_petri_net.pnml' 
            # IterV uses iterIII PetriNet!
        if iterIV:
            pnmlPath = './process_mining/iterIV/IterIV_petri_net.pnml'
        

        petri_net, im, fm = pm4py.read_pnml(pnmlPath)

        ## Conformance Checking
          
        faulty_log = pm4py.read_xes('C:/Users/alfer/Desktop/Dev Projects/ba-obs-pm/xes_export/faultyEventLogV1.xes')
        
        if iterI and not iterIV:
            faulty_log =  pm4py.filter_event_attribute_values(faulty_log, 'lifecycle:transition', ['start'], level='event', retain=True)
        if iterII:
            faulty_log = pm4py.filter_event_attribute_values(faulty_log, 'concept:name', ['/api/fights', '/api/fights/randomfighters'])
        if iterIII and not iterV:
            faulty_log = pm4py.filter_directly_follows_relation(faulty_log, [('/api/heroes/random','HeroService.findRandomHero'),('/api/villain/random', 'VillainService.findRandomVillain'), ('/api/fights', 'fights send') ])
        
        pathConfCh = './process_mining/'+naming+'/conf_checking_'+naming
        try:
            os.makedirs(pathConfCh)
        except FileExistsError:
        # directory already exists
            pass
        
        fitness = pm4py.fitness_token_based_replay(faulty_log,petri_net, im, fm)
        writeJsonFile(fitness, pathConfCh + "/log_fitness")
        
        conformance_diagnostics = pm4py.conformance_diagnostics_token_based_replay(faulty_log,petri_net, im, fm)
            
        (unfitting_traces, fitting_traces) = exportConformanceDiagnosisAsJson(conformance_diagnostics, pathConfCh)
        
        ## Conformance with 
        calculateAlignment = False
        if(calculateAlignment):
            alignments_fitness = pm4py.fitness_alignments(faulty_log,petri_net, im, fm)
            print(alignments_fitness)
            alignments_diagnostics = pm4py.conformance_diagnostics_alignments(faulty_log,petri_net, im, fm)
            showAlignment = True
            if showAlignment:
                pm4py.view_alignments(faulty_log,alignments_diagnostics)
            pm4py.save_vis_alignments(faulty_log, alignments_diagnostics, pathConfCh+'/alignment.png')
        
        print('unfittingTraceslen: ' + str(len(unfitting_traces)))
        print('fittingTraceslen: '+str(len(fitting_traces)))
        withPTrans = [trace for trace in unfitting_traces if len(trace['transitions_with_problems']) >0 ]
        print('withPTrans' + str(len(withPTrans)))
        #Hier ist die Datenabank Operation nicht aktiviert worden 
        missingVDataOperation = [trace for trace in unfitting_traces if len([x for x in trace['enabled_transitions_in_marking'] if 'SELECT villains_database.Villain' in str(x) ])>0 ]
        print('missingVDataOperation' + str(len(missingVDataOperation)))
        # Andere Abweichung, die nicht mit der Datenbank zu tuen haben.
        havingVDataOperation = [trace for trace in unfitting_traces if len([x for x in trace['enabled_transitions_in_marking'] if 'SELECT villains_database.Villain' in str(x) ])<1 ]
        print('havingVDataOperation' + str(len(havingVDataOperation)))
        #print(havingVDataOperation)
        #print(missingVDataOperation)
        withOtherFitnesLen = 0
        missingfighSendDataOperationLen = 0
        if len(unfitting_traces) >0:
            fitnessFirst = unfitting_traces[0]['trace_fitness']
            withOtherFitnes = [trace for trace in unfitting_traces if trace['trace_fitness'] !=fitnessFirst ]
            withOtherFitnesLen = len(withOtherFitnes)
            print('withOtherFitnes' + str(withOtherFitnesLen))
            """ for x in withOtherFitnes:
                print(unfitting_traces.index(x)) """
            #print(withOtherFitnes)
            missingfighSendDataOperation = [trace for trace in unfitting_traces if len([x for x in trace['enabled_transitions_in_marking'] if 'fights send' in str(x) ])>0 ]
            missingfighSendDataOperationLen =len(missingfighSendDataOperation)
            print('missingfighSendDataOperation'+str(missingfighSendDataOperationLen))

        
        # header = ['Iteration','percentfit', 'logfitness', 'unfittingTraceslen', 'fittingTraceslen', 'withPTrans', 'missingVDataOperation', 'havingVDataOperation' ]
        csvData.append( [naming, round(fitness['perc_fit_traces'],4), round(fitness['log_fitness'],4),len(unfitting_traces)+ len(fitting_traces), len(unfitting_traces), len(fitting_traces), len(withPTrans), len(missingVDataOperation), len(havingVDataOperation),withOtherFitnesLen,missingfighSendDataOperationLen])
    
    with open('./process_mining/IterationConfTable.csv', 'w+', encoding='UTF-8', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(csvheader)
        writer.writerows(csvData)
    
    faultList = openCSV('./process_mining/faultcsvV2.csv')
    vFaults, fsFaults, fuFault = sortFaultList(faultList)

    print('vFaults:' + str(len(vFaults)))
    print('fsFaults: ' + str(len(fsFaults)))
    print('fuFault: ' + str(len(fuFault)))

# Running Script Interactively: exec(open('mining.py').read())<
print('I am ready to use!')
    
    
    
