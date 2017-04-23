import sys
import time
import pprint
import errno
import simplejson as json
from socket import error as socket_error
from oauth2client import tools
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from apiclient.discovery import build
from apiclient.errors import HttpError
from const import *

def to_json(resource):
    return json.dumps(resource, sort_keys=True, ensure_ascii=False)


def to_pretty_json(resource):
    return json.dumps(resource, sort_keys=True, ensure_ascii=False, indent=4 * ' ')


def get_credentials(args):
    flow = flow_from_clientsecrets(CLIENT_SECRETS,
            scope=SCOPES,
            message=MISSING_CLIENT_SECRETS_MESSAGE)
    storage = Storage(CREDENTIALS_PATH)
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        print 'invalid credentials'
        # Save the credentials in storage to be used in subsequent runs.
        credentials = tools.run_flow(flow, storage, args)

    return credentials

def get_directory_service(args):
    return get_service('admin', 'directory_v1', args)

def get_groupsettings_service(args):
    return get_service('groupssettings', 'v1', args)

def get_service(service_name, version, args):
    credentials = get_credentials(args)
    http = httplib2.Http()
    credentials.authorize(http)
    return build(service_name, version, http=http)


def execute_admin_api(req):
    r = None
    error = None
    retry = 0
    http_code = 0
    while r is None:
        try:
            r = req.execute(num_retries=10)
        except HttpError, e:
            http_code = e.resp.status
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
            elif e.resp.status == 404:
                return (404, None)
            elif e.resp.status == 409:
                return (409, None)
            else:
                raise
        except RETRIABLE_EXCEPTIONS, e:
            error = "A retriable error occurred: %s" % e

        if error is not None:
            retry += 1
            if retry > MAX_RETRIES:
                sys.stderr.write('retry count exceeds limit (%d) %s\n' % (MAX_RETRIES, error))
                raise

            sys.stderr.write('retry count: %d\n' % retry)
            time.sleep(0.5)

    return (200, r)
