import helper
import json

import xes

## Assert Nano Timestamps
nanos = 1675518981741190741
should = "2023-02-04T14:56:21.741191"
ergebnis = helper._extractNanoTimestampsAsISO(nanos)
assert ergebnis.value == should and ergebnis.key == 'time:timestamp', 'Assert Nao Timestamp fails'

## Assert TraceDict Append 
traceDict = {'123': [xes.Event()]}
traceID = '123'
ergebnis = helper._appendToTraceDict(traceDict, traceID, xes.Event())
assert len(traceDict) == 1 and len(traceDict.get(traceID)) == 2, 'Exist Append failed'

traceDict = {}
traceID = '123'
ergebnis = helper._appendToTraceDict(traceDict, traceID, xes.Event())
assert len(traceDict) == 1 and len(traceDict.get(traceID)) == 1, 'Non-Exist Append failed'

traceDict = {'123': [xes.Event()], '321': [xes.Event()]}
traceID = '123'
ergebnis = helper._appendToTraceDict(traceDict, traceID, xes.Event())
assert len(traceDict) == 2 and len(traceDict.get(traceID)) == 2, 'Exist and additional element Append failed'


## Assert handleSpansAttribute  
print('Assert handleSpansAttribute')
spanDict = json.loads(
    """
    {
        "traceId":"3019cbf7675200315b85ec481be38f4c",
        "spanId":"91f0fe0efe36b608",
        "parentSpanId":"2214b46d9d9445fb",
        "name":"SELECT Hero",
        "kind":"SPAN_KIND_CLIENT",
        "startTimeUnixNano":"1675518981741190741",
        "endTimeUnixNano":"1675518982192147062",
        "attributes":[
            {
                "key":"db.statement",
                "value":{
                    "stringValue":"select count(*) as col_0_0_ from Hero hero0_"
                }
            },
                {
                "key":"db.statement2",
                "value":{
                    "stringValue":"select count(*) as col_0_0_ from Hero hero0_"
                }
            }
        ],
        "status":{ }
    }"""
)
traceID = spanDict.get('traceId')
spanID = spanDict.get('spanId')
start = helper._extractNanoTimestampsAsISO(spanDict.get('startTimeUnixNano')).value
end = helper._extractNanoTimestampsAsISO(spanDict.get('endTimeUnixNano')).value
[eTraceId, eSpandId, eEventAtts, eStartAtt, eEndAtt] = helper._handleSpansAttribute(spanDict)

assert eTraceId == traceID, 'traceid wrong'
assert eSpandId == spanID, 'spandid wrong'
# extracts parentID, name, kind, and optional Attributes in example 2
assert len(eEventAtts) == 5, 'handleSpansAttribute: Attribute Anzahl wrong'
assert eStartAtt is not None and eStartAtt.value == start and eEndAtt is not None and eEndAtt.value == end, 'Check Time Attribute ' 
print(eEventAtts[0].key)
keys = [x.key for x in eEventAtts]
assert 'concept:name' in keys, 'concept:name missing'
keySet = set(keys)
assert len(keySet) == len(list(keys)), 'Multiple Keys exist!'
values = [x.value for x in eEventAtts]
assert None not in values, 'None Value exist!'


## Assert handleRessourceAttribute  
print('Assert handleRessourceAttribute')
scopSpanDict = json.loads(
    """
    {
        "attributes":[
            {
                "key":"service.name",
                "value":{
                    "stringValue":"rest-heroes"
                }
            },
            {
                "key":"service.version",
                "value":{
                    "stringValue":"1.0"
                }
            },
            {
                "key":"telemetry.sdk.language",
                "value":{
                    "stringValue":"java"
                }
            }
        ]  
    }"""
)

resourceAtts = helper._handleRessourceAttribute(scopSpanDict)
assert len(resourceAtts) == 1 and resourceAtts[0].value == 'rest-heroes'
assert 'org:resource' in [x.key for x in resourceAtts], 'org:resource missing'



## Assert handleScopeSpansAttribute  
print('Assert handleScopeSpansAttribute')
fTrace = open('./test_jsons/scopeSpan.json', 'r')
scopSpanDict = json.load(fTrace)
fTrace.close()
traceDict = dict()
traceID = "3019cbf7675200315b85ec481be38f4c"
helper._handleScopeSpansAttribute(scopSpanDict, traceDict, [xes.Attribute()])
# spans in example having same trace id => 1 key
# for every span 2 events are created, because lifecyle start and complete
assert len(traceDict) == 1 and len(traceDict.get(traceID)) == 4


print('Assert handleScopeSpansAttribute multiple traceIDs')
fTrace = open('./test_jsons/scopeSpanMultipleSpanIds.json', 'r')
scopSpanDict = json.load(fTrace)
fTrace.close()
traceDict = dict()
traceID1 = "3019cbf7675200315b85ec481be38f4c"
traceID2 = "abcde"
helper._handleScopeSpansAttribute(scopSpanDict, traceDict, [xes.Attribute()])
# spans in example having same trace id => 1 key
# for every span 2 events are created, because lifecyle start and complete
assert len(traceDict) == 2 and len(traceDict.get(traceID1)) == 2 and len(traceDict.get(traceID2)) == 2


print('Assert handleResourceSpansAttribute empty spans')
fTrace = open('./test_jsons/resSpanListEmpty.json', 'r')
resSpanList = json.load(fTrace)
fTrace.close()
traceDict = dict()
helper._handleResourceSpansAttribute(resSpanList, traceDict)
assert len(traceDict) == 0

# Test handleResourceSpansAttribute
fTrace = open('./test_jsons/resSpanList.json', 'r')
resSpanList = json.load(fTrace)
fTrace.close()
traceDict = dict()
helper._handleResourceSpansAttribute(resSpanList, traceDict)
assert len(traceDict) == 1 and len(traceDict.get(traceID)) == 6

# Test extractTraces
eventDict = {'trace1': [xes.Event(), xes.Event()], 'trace2': [xes.Event()], 'trace3': [xes.Event(), xes.Event(), xes.Event()]}
traces = helper._extractTraces(eventDict)

assert len(traces) == 3, 'Traces lenght'
assert len(traces[0].events) ==2 and len(traces[1].events) ==1  and len(traces[2].events) ==3, 'assumed event allocation correct'