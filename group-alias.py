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

from const import *
from utils import *

def show_resource(resource):
    if resource.has_key('primaryEmail'):
        print "primaryEmail: %s" % resource['primaryEmail']
    print "alias:        %s" % resource['alias']

def show_resource_list(resources, verbose):
    if resources.has_key('aliases'):
        for resource in resources['aliases']:
            if verbose:
                show_resource(resource)
                print ""
            else:
                print "%s %s" % (resource['primaryEmail'], resource['alias'])


def main(argv):
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    subparsers = parser.add_subparsers(help='sub command')

    #-------------------------------------------------------------------------
    # LIST
    #-------------------------------------------------------------------------
    parser_list = subparsers.add_parser('list', help='Lists all aliases for a group')
    parser_list.add_argument('groupKey', help='group email address, aliase or unique id')
    parser_list.add_argument('-v', '--verbose', action='store_true', help='show group all alias data')
    parser_list.add_argument('--json', action='store_true', help='output in JSON')
    parser_list.add_argument('--jsonPretty', action='store_true', help='output in pretty JSON')

    #-------------------------------------------------------------------------
    # INSERT
    #-------------------------------------------------------------------------
    parser_insert = subparsers.add_parser('insert', help='Adds an alias for the group')
    parser_insert.add_argument('groupKey', help='group email address, aliase or unique id')
    parser_insert.add_argument('alias', help='alias email address')
    parser_insert.add_argument('-v', '--verbose', action='store_true', help='show created alias data')
    parser_insert.add_argument('--json', action='store_true', help='output in JSON')
    parser_insert.add_argument('--jsonPretty', action='store_true', help='output in pretty JSON')

    #-------------------------------------------------------------------------
    # DELETE
    #-------------------------------------------------------------------------
    parser_delete = subparsers.add_parser('delete', help='Removes an alias')
    parser_delete.add_argument('groupKey', help='group email address, aliase or unique id')
    parser_delete.add_argument('alias', help='alias email address')

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

    service = build('admin', 'directory_v1', http=http)

    sv = service.groups()

    command = argv[1]

    if command == 'list':
        r = sv.aliases().list(groupKey=args.groupKey).execute()
        if args.jsonPretty:
            print to_pretty_json(r)
        elif args.json:
            print to_json(r)
        else:
            show_resource_list(r, args.verbose)
    elif command == 'insert':
        body = { 'alias': args.alias }
        r = sv.aliases().insert(groupKey=args.groupKey, body=body).execute()
        if args.verbose:
            if args.jsonPretty:
                print to_pretty_json(r)
            elif args.json:
                print to_json(r)
            else:
                show_resource(r)
    elif command == 'delete':
        r = sv.aliases().delete(groupKey=args.groupKey, alias=args.alias).execute()
    else:
        print "unknown command '%s'" % command
        return


if __name__ == '__main__':
    main(sys.argv)
