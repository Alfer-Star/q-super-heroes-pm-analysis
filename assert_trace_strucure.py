import os

import json

from io import TextIOWrapper

jsonPath = './traces'

def processJSONFile(file: TextIOWrapper):
    Lines =  file.readlines()
    return [json.loads(line) for line in Lines]    


def assertFilesHavingOtelJsonStructure(directory: str):
    traceFileLIst = os.walk(directory)
    for (dir_path, dir_names, file_names) in traceFileLIst:
        for fileName in [fp for fp in file_names if fp != '.gitkeep']:
            filePath=dir_path + '/' + fileName
            fTrace = open(filePath, 'r')
            LinesAsParsedJson = processJSONFile(fTrace)
            for line in LinesAsParsedJson:
                try:
                    assertOtelJsonStructure(line)
                except:
                    print('File did not pass: ' + filePath)


def assertOtelJsonStructure(parsedJson: dict):
    resourceSpans = parsedJson.get('resourceSpans')
    assert isinstance(resourceSpans, list)
    for ressourceSpan in resourceSpans:
        assertRessource(ressourceSpan.get('resource'))
                
        scopeSpans = ressourceSpan.get('scopeSpans')
        assertScopeSpans(scopeSpans)


def assertRessource(resource: dict):
    assert isinstance(resource, dict)
    attributes = resource.get('attributes')
    assert isinstance(attributes, list)
    # TODO: check exist attribute serviceName for ressource...
    
def assertScopeSpans(scopeSpans: list):
    assert isinstance(scopeSpans, list)
    for scopeSpan in scopeSpans:
        scope = scopeSpan.get("scope")
        
        spans = scopeSpan.get("spans")
        assert(isinstance(spans, list))
        for span in spans:
            assertSpan(span)
        
def assertSpan(span):
    assert "traceId" in span, 'has not traceId'
    assert "spanId" in span, 'has not spanId'
    assert "parentSpanId" in span, 'has not parentSpanId'
    assert "name" in span, 'has not name'
    assert "kind" in span, 'has not kind'
    assert "startTimeUnixNano" in span, 'has not startTimeUnixNano'
    assert "endTimeUnixNano" in span, 'has not endTimeUnixNano'
    assert "attributes" in span and isinstance(span.get('attributes'), list), 'has not attributes'


    