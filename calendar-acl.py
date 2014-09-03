#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pprint
from apiclient.discovery import build
import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client import tools
import argparse
import simplejson as json

from const import *
from utils import *

def show_resource(resource):
    print "ruleId: %s" % resource['id']
    print "role:   %s" % resource['role']
    print "scope:  %s %s" % (resource['scope']['type'], resource['scope']['value'])


def show_resource_list(resources, verbose):
    for resource in resources:
        if verbose:
            show_resource(resource)
            print ""
        else:
            print "%s,%s,%s,%s" % (resource['id'],
                                resource['role'],
                                resource['scope']['type'],
                                resource['scope']['value'])


def main(argv):
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    subparsers = parser.add_subparsers(help='sub command')

    #-------------------------------------------------------------------------
    # LIST / SEARCH
    #-------------------------------------------------------------------------
    parser_list = subparsers.add_parser('list', help='Returns the rules in the access control list for the calendar')
    parser_list.add_argument('calendarId', help='calendear id')
    parser_list.add_argument('--maxResults', type=int, help='Acceptable values are 1 to 250')
    parser_list.add_argument('-v', '--verbose', action='store_true', help='show updated user data')
    parser_list.add_argument('--json', action='store_true', help='output in JSON')
    parser_list.add_argument('--jsonPretty', action='store_true', help='output in pretty JSON')

    #-------------------------------------------------------------------------
    # GET
    #-------------------------------------------------------------------------
    parser_get = subparsers.add_parser('get', help='Returns an access control rule')
    parser_get.add_argument('calendarId', help='calendar id')
    parser_get.add_argument('ruleId', help='rule id')
    parser_get.add_argument('--json', action='store_true', help='output in JSON')
    parser_get.add_argument('--jsonPretty', action='store_true', help='output in pretty JSON')

    #-------------------------------------------------------------------------
    # INSERT
    #-------------------------------------------------------------------------
    parser_insert = subparsers.add_parser('insert', help='Creates an access control rule')
    parser_insert.add_argument('calendarId', help='calendar id')
    parser_insert.add_argument('role', choices=['none', 'freeBusyReader', 'reader', 'writer', 'owner'])
    parser_insert.add_argument('type', choices=['default', 'user', 'group', 'domain'])
    parser_insert.add_argument('--value', help='email address or domain name')
    parser_insert.add_argument('-v', '--verbose', action='store_true', help='show created user data')
    parser_insert.add_argument('--json', action='store_true', help='output in JSON')
    parser_insert.add_argument('--jsonPretty', action='store_true', help='output in pretty JSON')

    #-------------------------------------------------------------------------
    # PATCH
    #-------------------------------------------------------------------------
    parser_patch = subparsers.add_parser('patch', help='Updates an access control rule')
    parser_patch.add_argument('calendarId', help='calendar id')
    parser_patch.add_argument('ruleId', help='rule id')
    parser_patch.add_argument('role', choices=['none', 'freeBusyReader', 'reader', 'writer', 'owner'])
    parser_patch.add_argument('type', choices=['default', 'user', 'group', 'domain'])
    parser_patch.add_argument('--value', help='email address or domain name')
    parser_patch.add_argument('-v', '--verbose', action='store_true', help='show updated user data')
    parser_patch.add_argument('--json', action='store_true', help='output in JSON')
    parser_patch.add_argument('--jsonPretty', action='store_true', help='output in pretty JSON')

    #-------------------------------------------------------------------------
    # DELETE
    #-------------------------------------------------------------------------
    parser_delete = subparsers.add_parser('delete', help='Deletes an access control rule')
    parser_delete.add_argument('calendarId', help='calendar id')
    parser_delete.add_argument('ruleId', help='rule id')

    args = parser.parse_args(argv[1:])

    FLOW = flow_from_clientsecrets(CLIENT_SECRETS,
                                   scope=SCOPES,
                                   message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage(CREDENTIALS_PATH)
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        print 'invalid credentials'
        # Save the credentials in storage to be used in subsequent runs.
        credentials = tools.run_flow(FLOW, storage, args)

    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)

    service = build('calendar', 'v3', http=http)

    sv = service.acl()

    command = argv[1]

    if command == 'list':
        acls = []
        pageToken = None
        params = {}
        params['calendarId'] = args.calendarId
        while True:
            if args.maxResults:
                params['maxResults'] = args.maxResults
            if pageToken:
                params['pageToken'] = pageToken

            r = sv.list(**params).execute()

            if r.has_key('items'):
                if args.jsonPretty or args.json:
                    for acl in r['items']:
                        acls.append(acl)
                else:
                    show_resource_list(r['items'], args.verbose)
            if r.has_key('nextPageToken'):
                pageToken = r['nextPageToken']
            else:
                break

        if args.jsonPretty:
            if len(acls) == 1:
                print to_pretty_json(acls[0])
            else:
                print to_pretty_json(acls)
        elif args.json:
            if len(acls) == 1:
                print to_json(acls[0])
            else:
                print to_json(acls)

    elif command == 'get':
        r = sv.get(calendarId=args.calendarId, ruleId=args.ruleId).execute()
        if args.jsonPretty:
            print to_pretty_json(r)
        elif args.json:
            print to_json(r)
        else:
            show_resource(r)
    elif command == 'insert':
        body = { 'role': args.role, 'scope': { 'type': args.type } }
        if args.type != 'default':
            if args.value is None:
                print '--value is required'
                sys.exit(1)
            body['scope']['value'] = args.value

        r = sv.insert(calendarId=args.calendarId, body=body).execute()
        if args.verbose:
            if args.jsonPretty:
                print to_pretty_json(r)
            elif args.json:
                print to_json(r)
            else:
                show_resource(r)
    elif command == 'patch':
        body = { 'role': args.role, 'scope': { 'type': args.type } }
        if args.type != 'default':
            if args.value is None:
                print '--value is required'
                sys.exit(1)
            body['scope']['value'] = args.value

        r = sv.patch(calendarId=args.calendarId, ruleId=args.ruleId, body=body).execute()
        if args.verbose:
            if args.jsonPretty:
                print to_pretty_json(r)
            elif args.json:
                print to_json(r)
            else:
                show_resource(r)
    elif command == 'delete':
        r = sv.delete(calendarId=args.calendarId, ruleId=args.ruleId).execute()
    else:
        print "unknown command '%s'" % command
        return


if __name__ == '__main__':
    main(sys.argv)
