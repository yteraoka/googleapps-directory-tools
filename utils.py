import simplejson as json

def to_json(resource):
    return json.dumps(resource, sort_keys=True, ensure_ascii=False).encode('utf-8')

def to_pretty_json(resource):
    return json.dumps(resource, sort_keys=True, ensure_ascii=False, indent=4 * ' ').encode('utf-8')
