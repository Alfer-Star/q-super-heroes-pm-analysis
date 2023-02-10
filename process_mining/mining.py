import pm4py

if __name__ == "__main__":
    log = pm4py.read_xes('C:/Users/alfer/Desktop/Dev Projects/ba-obs-pm/xes_export/example.xes')
    process_model = pm4py.discover_bpmn_inductive(log)
    pm4py.view_bpmn(process_model)