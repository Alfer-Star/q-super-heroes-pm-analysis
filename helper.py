import xes
from xes import Log
from xes import Trace
from xes import Event
from xes import Attribute
from progress.bar import Bar
from datetime import datetime
from datetime import timezone

warnings = list()

def addOtelTraceToXesEventLog(parsedJson: list, log: Log):
    """ Extract Traces and Events from JSON Output of OTC File Exporter, 
        where every single Line in the JSON FIle contains an JSON object.
        Events in the extracted Traces are sorted.
        Extracted Traces are added to the given Event Log. """
    warnings = list()
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
                    
    _addParentalActivityAttribute(traceDict)
    print('ParentActivity Added')
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
        [traceId,spanId, name, eventAtts, startAtt, endAtt]  = _handleSpansAttribute(span)
        
        #Lifecycle start
        startEvent = xes.Event()
        startEvent.attributes = eventAtts + resSpecificAtts
        # startEvent.add_attribute(xes.Attribute('string','concept:name', name +' start'))
        startEvent.add_attribute(xes.Attribute('string','concept:name', name))
        startEvent.add_attribute(xes.Attribute('string','identity:id', spanId +'-1'))
        startEvent.add_attribute(xes.Attribute('string','spanId', spanId))
        startEvent.add_attribute(xes.Attribute('string','lifecycle:transition', 'start'))
        startEvent.add_attribute(startAtt)
        _appendToTraceDict(traceDict=traceDict, traceId=traceId, event=startEvent)
        
        #Lifecycle complete
        endEvent = xes.Event()
        endEvent.attributes = eventAtts + resSpecificAtts
        # endEvent.add_attribute(xes.Attribute('string','concept:name', name +' end'))
        endEvent.add_attribute(xes.Attribute('string','concept:name', name))
        endEvent.add_attribute(xes.Attribute('string','identity:id', spanId +'-2'))
        endEvent.add_attribute(xes.Attribute('string','spanId', spanId))
        endEvent.add_attribute(xes.Attribute('string','lifecycle:transition', 'complete'))
        endEvent.add_attribute(endAtt)
        _appendToTraceDict(traceDict=traceDict, traceId=traceId, event=endEvent)

def _handleSpansAttribute(spanDict: dict):
    abcKey = {"parentSpanId": 'parentID', "kind":"kind"}
    fixAttributes = [xes.Attribute('string', value , spanDict.get(key) ) for key, value in abcKey.items()] 
    spanAttDict = spanDict.get('attributes')  
    SpanAttributesXES = list()
    
    SpanAttributesXES = [xes.Attribute('string',dict.get('key'), str(dict.get('value'))) for dict in spanAttDict]
    
    spanId =  spanDict.get('spanId')
    
    name = spanDict.get('name')
    
    start = _extractNanoTimestampsAsISO(spanDict.get('startTimeUnixNano'))
    end = _extractNanoTimestampsAsISO(spanDict.get('endTimeUnixNano'))
    
    if datetime.fromisoformat(start.value) > datetime.fromisoformat(end.value):
        warnings.append((spanId, 'start Value is greater than end Value!'))
    
    traceid = spanDict.get('traceId')            
    return [traceid, spanId, name, fixAttributes + SpanAttributesXES, start, end]

def _appendToTraceDict(traceDict, traceId, event):
    if traceId in traceDict:
        newList = list(traceDict.get(traceId))
        newList.append(event)
        traceDict[traceId] = newList
    else:
        traceDict[traceId]=[event]
        
def _extractNanoTimestampsAsISO(time: str):
    timeInMS = int(time) / 1e9
    return xes.Attribute('date', 'time:timestamp', datetime.fromtimestamp(timeInMS, tz=timezone.utc).isoformat())
    

def _extractTraces(eventDict: dict) -> list:
    traceList = list()
    itemList = eventDict.items()
    for (traceID, eventList) in itemList:
        trace = xes.Trace()
        trace.events = eventList
        trace.add_attribute(xes.Attribute(key="concept:name", type='string', value=traceID))
        traceList.append(trace)
    return traceList
  
def _addParentalActivityAttribute(eventDict: dict):
    for (traceID, eventList) in eventDict.items():
        trace = xes.Trace()
        trace.events = eventList
        for event in eventList:
            parentID = getParentAttribute(event).value
            if(parentID != ''):
                # Liste enthält Aktivität mehrfach, da das Evnt einmal als start und complete event existiert, daher nur ein element benötigt
                parentNameAtt = [getCNameAttribute(parentEvent) for parentEvent in eventList if getSpanIDAttribute(parentEvent).value == parentID][0]
                event.add_attribute(xes.Attribute(key="sbc", type='string', value=parentNameAtt.value))
            
            
        
def getParentAttribute(e: Event)-> Attribute:
    return next(filter(lambda a: a.key == 'parentID', e.attributes))

def getSpanIDAttribute(e: Event)-> Attribute:
    return next(filter(lambda a: a.key == 'spanId', e.attributes))

def getCNameAttribute(e: Event)-> Attribute:
    return next(filter(lambda a: a.key == 'concept:name', e.attributes))
    
## Test Cases


     
     