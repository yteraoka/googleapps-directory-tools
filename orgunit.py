#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import codecs
import pprint
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
    status, r = execute_admin_api(sv.list(**params))
    if args.jsonPretty:
        print to_pretty_json(r['organizationUnits'])
    elif args.json:
        print to_json(r['organizationUnits'])
    else:
        show_resource_list(r, args.verbose)

def get_orgunit(sv, args):
    status, r = execute_admin_api(sv.get(customerId=args.customerId, orgUnitPath=args.orgUnitPath))
    if status == 404:
        sys.stderr.write('%s does not exist\n' % args.orgUnitPath)
        sys.exit(2)
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
    status, r = execute_admin_api(sv.insert(customerId=args.customerId, body=body))
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
        status, r = execute_admin_api(sv.patch(customerId=args.customerId, orgUnitPath=args.orgUnitPath, body=body))
        if status == 404:
            sys.stderr.write('%s does not exist\n' % args.orgUnitPath)
            sys.exit(2)
        if args.verbose:
            if args.jsonPretty:
                print to_pretty_json(r)
            elif args.json:
                print to_json(r)
            else:
                show_resource(r)

def delete_orgunit(sv, args):
    status, r = execute_admin_api(sv.delete(customerId=args.customerId, orgUnitPath=args.orgUnitPath))
    if status == 404:
        sys.stderr.write('%s does not exist\n' % args.orgUnitPath)
        sys.exit(2)

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

    service = get_directory_service(args)

    args.func(service.orgunits(), args)


if __name__ == '__main__':
    sys.stdout = codecs.getwriter('utf_8')(sys.stdout)
    main()
