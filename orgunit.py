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
    print "name:               %s" % resource['name']
    print "description:        %s" % resource['description']
    print "orgUnitPath:        %s" % resource['orgUnitPath']
    print "parentOrgUnitPath:  %s" % resource['parentOrgUnitPath']
    if resource.has_key('blockInheritance'):
        print "blockInheritance:   %s" % resource['blockInheritance']

def show_resource_list(resources, verbose):
    if resources.has_key('organizationUnits'):
        for resource in resources['organizationUnits']:
            if verbose:
                show_resource(resource)
                print ""
            else:
                print resource['orgUnitPath']

def list_orgunit(sv, args):
    params = {}
    params['customerId'] = args.customerId
    if args.orgUnitPath:
        params['orgUnitPath'] = args.orgUnitPath.decode('utf-8')
    if args.type:
        params['type'] = args.type
    r = sv.list(**params).execute()
    if args.jsonPretty:
        print to_pretty_json(r['organizationUnits'])
    elif args.json:
        print to_json(r['organizationUnits'])
    else:
        show_resource_list(r, args.verbose)

def get_orgunit(sv, args):
    r = sv.get(customerId=args.customerId,
               orgUnitPath=args.orgUnitPath).execute()
    if args.jsonPretty:
        print to_pretty_json(r)
    elif args.json:
        print to_json(r)
    else:
        show_resource(r)

def insert_orgunit(sv, args):
    body = { 'name': args.name,
             'parentOrgUnitPath': args.parentOrgUnitPath }
    if args.description:
        body['description'] = args.description
    if args.blockInheritance:
        body['blockInheritance'] = True if args.blockInheritance == 'true' else False
    r = sv.insert(customerId=args.customerId, body=body).execute()
    if args.verbose:
        if args.jsonPretty:
            print to_pretty_json(r)
        elif args.json:
            print to_json(r)
        else:
            show_resource(r)

def patch_orgunit(sv, args):
    body = {}
    if args.name:
        body['name'] = args.name
    if args.description:
        body['description'] = args.description
    if args.parentOrgUnitPath:
        body['parentOrgUnitPath'] = args.parentOrgUnitPath
    if args.blockInheritance:
      body['blockInheritance'] = True if args.blockInheritance == 'true' else False
    if len(body) > 0:
        r = sv.patch(customerId=args.customerId,
                     orgUnitPath=args.orgUnitPath,
                     body=body).execute()
        if args.verbose:
            if args.jsonPretty:
                print to_pretty_json(r)
            elif args.json:
                print to_json(r)
            else:
                show_resource(r)

def delete_orgunit(sv, args):
    r = sv.delete(customerId=args.customerId,
                  orgUnitPath=args.orgUnitPath).execute()

def main():
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    subparsers = parser.add_subparsers(help='sub command')

    #-------------------------------------------------------------------------
    # LIST
    #-------------------------------------------------------------------------
    parser_list = subparsers.add_parser('list', help='Retrieves a list of all organization units for an account')
    parser_list.add_argument('customerId', help='customer id')
    parser_list.add_argument('--orgUnitPath', help='full path to the organization unit')
    parser_list.add_argument('--type', choices=['all', 'children'], default='children',
                             help='all: all sub-org, children: immediate children only (default)')
    parser_list.add_argument('-v', '--verbose', action='store_true',
                             help='show organization unit data')
    parser_list.add_argument('--json', action='store_true', help='output in JSON')
    parser_list.add_argument('--jsonPretty', action='store_true', help='output in pretty JSON')
    parser_list.set_defaults(func=list_orgunit)

    #-------------------------------------------------------------------------
    # GET
    #-------------------------------------------------------------------------
    parser_get = subparsers.add_parser('get', help='Retrieves an organization unit')
    parser_get.add_argument('customerId', help='customer id')
    parser_get.add_argument('orgUnitPath', help='full path of the organization unit')
    parser_get.add_argument('--json', action='store_true', help='output in JSON')
    parser_get.add_argument('--jsonPretty', action='store_true', help='output in pretty JSON')
    parser_get.set_defaults(func=get_orgunit)

    #-------------------------------------------------------------------------
    # INSERT
    #-------------------------------------------------------------------------
    parser_insert = subparsers.add_parser('insert', help='Adds an organization unit')
    parser_insert.add_argument('customerId', help='customer id')
    parser_insert.add_argument('name', help='organization unit name')
    parser_insert.add_argument('parentOrgUnitPath', help='parent organization unit path')
    parser_insert.add_argument('--blockInheritance', choices=['true', 'false'])
    parser_insert.add_argument('--description')
    parser_insert.add_argument('-v', '--verbose', action='store_true', help='show all group data')
    parser_insert.add_argument('--json', action='store_true', help='output in JSON')
    parser_insert.add_argument('--jsonPretty', action='store_true', help='output in pretty JSON')
    parser_insert.set_defaults(func=insert_orgunit)

    #-------------------------------------------------------------------------
    # PATCH
    #-------------------------------------------------------------------------
    parser_patch = subparsers.add_parser('patch', help='Updates an organization unit')
    parser_patch.add_argument('customerId')
    parser_patch.add_argument('orgUnitPath', help='full path of the organization unit')
    parser_patch.add_argument('--name')
    parser_patch.add_argument('--description')
    parser_patch.add_argument('--orgUnitPath')
    parser_patch.add_argument('--parentOrgUnitPath')
    parser_patch.add_argument('--blockInheritance', choices=['true', 'false'])
    parser_patch.add_argument('-v', '--verbose', action='store_true', help='show all group data')
    parser_patch.add_argument('--json', action='store_true', help='output in JSON')
    parser_patch.add_argument('--jsonPretty', action='store_true', help='output in pretty JSON')
    parser_patch.set_defaults(func=patch_orgunit)

    #-------------------------------------------------------------------------
    # DELETE
    #-------------------------------------------------------------------------
    parser_delete = subparsers.add_parser('delete', help='Removes an organization unit')
    parser_delete.add_argument('customerId')
    parser_delete.add_argument('orgUnitPath', help='full path of the organization unit')
    parser_delete.set_defaults(func=delete_orgunit)

    args = parser.parse_args()

    # Set up a Flow object to be used if we need to authenticate.
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

    sv = service.orgunits()

    args.func(sv, args)


if __name__ == '__main__':
    main()
