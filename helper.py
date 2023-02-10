import xes
from xes import Log
from xes import Trace
from xes import Event
from progress.bar import Bar
from datetime import datetime

removedAttributes = list()

warnings = list()

def addOtelTraceToXesEventLog(parsedJson: list, log: Log):
    removedAttributes = list()
    # Trace and Event korrelation: traceID is Key and EventList is value
    # indiviual Traces or their tracid could exist in several traces  
    traceDict = dict()
    with Bar('Processing OtelExporter JSONs', max=len(parsedJson)) as bar:
        for json in parsedJson:
            _handleResourceSpansAttribute(json.get('resourceSpans'), traceDict)
            bar.next()
            
    for (key, eventlist) in traceDict.items():
        eventlist.sort(key = getEventTimestamp,reverse=False)
    print('Events Sorted')
                    
    log.traces = _extractTraces(traceDict)
    
    print("following Warnings "+ str(len(warnings)) +" appeared:")
    for (spanId, message) in warnings:
        print('Aufgetreten:'+ message + ' in' + spanId)

def getEventTimestamp(e: Event):
    first = next(filter(lambda a: a.key == 'time:timestamp', e.attributes))
    return datetime.fromisoformat(first.value)
    

def _handleResourceSpansAttribute(resSpanList: list, traceDict: dict):
    resSpanList = [dict(resSpan) for resSpan in resSpanList]
    for resSpan in resSpanList:
        ressource = resSpan.get('resource')
        resSpecificAtts = _handleRessourceAttribute(ressource)
        scopeSpans = resSpan.get('scopeSpans')
        for scopeSpan in scopeSpans:
            _handleScopeSpansAttribute(scopeSpan, traceDict, resSpecificAtts)
                
def _handleRessourceAttribute(resource: dict):
    return [xes.Attribute(type='string', key='org:resource', value=att.get('value').get('stringValue')) for att in resource.get('attributes') if att.get('key')=="service.name"]
    
def _handleScopeSpansAttribute(scopeSpan: dict, traceDict: dict, resSpecificAtts):
    # scope ist uninteressant, könnte als Gruppen Attribute aufgenommen werden
    # um festzuhalten welches source die Telemetrie Daten entstammen
    scope = dict(scopeSpan).get('scope')
    spanList = dict(scopeSpan).get('spans')
    for span in spanList:
            # Span Ebene, create Events from Spans
        [traceId,spanId, eventAtts, startAtt, endAtt]  = _handleSpansAttribute(span)
        
        #Lifecycle start
        startEvent = xes.Event()
        startEvent.attributes = eventAtts + resSpecificAtts
        startEvent.add_attribute(xes.Attribute('string','identity:id', spanId +'-1'))
        startEvent.add_attribute(xes.Attribute('string','lifecycle:transition', 'start'))
        startEvent.add_attribute(startAtt)
        _appendToTraceDict(traceDict=traceDict, traceId=traceId, event=startEvent)
        
        #Lifecycle complete
        endEvent = xes.Event()
        endEvent.attributes = eventAtts + resSpecificAtts
        endEvent.add_attribute(xes.Attribute('string','identity:id', spanId +'-2'))
        endEvent.add_attribute(xes.Attribute('string','spanId', spanId))
        endEvent.add_attribute(xes.Attribute('string','lifecycle:transition', 'complete'))
        endEvent.add_attribute(endAtt)
        _appendToTraceDict(traceDict=traceDict, traceId=traceId, event=endEvent)

def _handleSpansAttribute(spanDict: dict):
    abcKey = {'name':'concept:name', "parentSpanId": 'parentID', "kind":"kind"}
    fixAttributes = [xes.Attribute('string', value , spanDict.get(key) ) for key, value in abcKey.items()] 
    spanAttDict = spanDict.get('attributes')  
    SpanAttributesXES = list()
    
    SpanAttributesXES = [xes.Attribute('string',dict.get('key'), str(dict.get('value'))) for dict in spanAttDict]
    
    spanId =  spanDict.get('spanId')
    
    start = _extractNanoTimestampsAsISO(spanDict.get('startTimeUnixNano'))
    end = _extractNanoTimestampsAsISO(spanDict.get('endTimeUnixNano'))
    
    if datetime.fromisoformat(start.value) > datetime.fromisoformat(end.value):
        warnings.append((spanId, 'start Value is greater than end Value!'))
    
    traceid = spanDict.get('traceId')            
    return [traceid, spanId, fixAttributes + SpanAttributesXES, start, end]

def _appendToTraceDict(traceDict, traceId, event):
    if traceId in traceDict:
        newList = list(traceDict.get(traceId))
        newList.append(event)
        traceDict[traceId] = newList
    else:
        traceDict[traceId]=[event]
        
def _extractNanoTimestampsAsISO(time: str):
    return xes.Attribute('date', 'time:timestamp', datetime.fromtimestamp( int(time) / 1e9).isoformat() )
    

def _extractTraces(eventDict: dict) -> list:
    traceList = list()
    itemList = eventDict.items()
    for (traceID, eventList) in itemList:
        trace = xes.Trace()
        trace.events = eventList
        trace.add_attribute(xes.Attribute(key="concept:name", type='string', value=traceID))
        traceList.append(trace)
    return traceList
    
    
## Test Cases


     
     