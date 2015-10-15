import simplejson as json

def to_json(resource):
    return json.dumps(resource, sort_keys=True, ensure_ascii=False)

def to_pretty_json(resource):
    return json.dumps(resource, sort_keys=True, ensure_ascii=False, indent=4 * ' ')
