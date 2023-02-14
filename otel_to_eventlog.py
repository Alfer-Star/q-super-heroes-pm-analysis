# Python program to read
# json file 

from helper import *

import xes
from xes import Extension

from assert_trace_strucure import processJSONFile, assertFilesHavingOtelJsonStructure

jsonPath = './traces/otelcol_data.json'
  
assertFilesHavingOtelJsonStructure('./traces')
print('Traces are legitim!')

# Opening JSON file
fTrace = open(jsonPath, 'r')
parsedTraces = processJSONFile(fTrace)
fTrace.close()

eventLog = xes.Log()
eventLog.add_default_extensions()
eventLog.add_extension(Extension(name="ID Extension",
                      prefix="identity",
                      uri="http://www.xes-standard.org/identity.xesext"))

eventLog.classifiers = [
    xes.Classifier(name="org:resource",keys="org:resource"),
    xes.Classifier(name="concept:name",keys="concept:name"),
    xes.Classifier(name="time:timestamp",keys="time:timestamp"),
    xes.Classifier(name="identity:id",keys="identity:id"),
    xes.Classifier(name="lifecycle:transition",keys="lifecycle:transition"),
    xes.Classifier(name="SpanId",keys="spanId"),
    xes.Classifier(name="parentSpan",keys="parentSpanId"),
]

addOtelTraceToXesEventLog(parsedTraces, eventLog)
print('Exportiere Event Log Bitte warten...')
open("./xes_export/example.xes", "w").write(str(eventLog))
print('Event Log XES Export erstellt!')



