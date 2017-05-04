#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import codecs
import pprint
import argparse
import re

from const import *
from utils import *

def show_resource(email, resource):
    print "email: %s" % email
    print "clientId: %s" % resource['clientId']
    print "displayText: %s" % resource['displayText']
    print "nativeApp: %s" % resource['nativeApp']
    for scope in resource['scopes']:
        print "scopes: %s" % scope


def show_resource_list(email, resource):
    if 'items' not in resource: 
        return

    for item in resource['items']:
        print "%s\t%s\t%s" % (email, item['clientId'], item['displayText'])


def item_filter(r, scopes, whitelist):
    r2 = {}
    r2['items'] = []

    if r.has_key('items'):
        for item in r['items']:
            if item['clientId'] in whitelist:
                continue
            matched = False
            for scope in item['scopes']:
                if scopes is None or scope in scopes:
                    matched = True
            if matched == True:
                r2['items'].append(item)

    for k in r:
        if k != 'items':
            r2[k] = r[k]

    return r2


def get_whitelist(file):
    clientids = []

    if file is None:
        return clientids

    for line in file:
        clientids.append(re.sub(r'[,#].*$', '', line).strip())

    return clientids


def list_tokens(sv, args):
    status, r = execute_admin_api(sv.list(userKey=args.userKey))

    if status == 404:
        sys.stderr.write('%s does not exist\n' % args.userKey)
        sys.exit(2)

    whitelist = get_whitelist(args.whitelist)

    r = item_filter(r, args.scopes, whitelist)

    if args.jsonPretty:
        print to_pretty_json(r)
    elif args.json:
        print to_json(r)
    else:
        show_resource_list(args.userKey, r)


def get_tokens(sv, args):
    status, r = execute_admin_api(sv.get(userKey=args.userKey, clientId=args.clientId))

    if status == 404:
        sys.stderr.write('%s %s does not exist\n' % (args.userKey, args.clientId))
        sys.exit(2)

    if args.jsonPretty:
        print to_pretty_json(r)
    elif args.json:
        print to_json(r)
    else:
        show_resource(args.userKey, r)


def delete_tokens(sv, args):
    status, r = execute_admin_api(sv.delete(userKey=args.userKey, clientId=args.clientId))

    if status == 404:
        sys.stderr.write('%s does not exist\n' % args.userKey)
        sys.exit(2)


def main():
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    subparsers = parser.add_subparsers(help='sub command')

    #-------------------------------------------------------------------------
    # LIST
    #-------------------------------------------------------------------------
    parser_list = subparsers.add_parser('list', help='Lists all aliases for a user')
    parser_list.add_argument('userKey', help='user\'s email address, alias or unique id')
    parser_list.add_argument('--scopes', action='append', help='list if scope contains this')
    parser_list.add_argument('--whitelist', type=file, help='allowed clientId list file')
    parser_list.add_argument('--json', action='store_true', help='output in JSON')
    parser_list.add_argument('--jsonPretty', action='store_true', help='output in pretty JSON')
    parser_list.set_defaults(func=list_tokens)

    #-------------------------------------------------------------------------
    # GET
    #-------------------------------------------------------------------------
    parser_get = subparsers.add_parser('get', help='Adds an alias')
    parser_get.add_argument('userKey', help='user\'s email address, alias or unique id')
    parser_get.add_argument('clientId', help='The Client ID of the application the token')
    parser_get.add_argument('-v', '--verbose', action='store_true', help='show created alias data')
    parser_get.add_argument('--json', action='store_true', help='output in JSON')
    parser_get.add_argument('--jsonPretty', action='store_true', help='output in pretty JSON')
    parser_get.set_defaults(func=get_tokens)

    #-------------------------------------------------------------------------
    # DELETE
    #-------------------------------------------------------------------------
    parser_delete = subparsers.add_parser('delete', help='Removes an alias')
    parser_delete.add_argument('userKey', help='user\'s email address, alias or unique id')
    parser_delete.add_argument('clientId', help='The Client ID of the application the token')
    parser_delete.set_defaults(func=delete_tokens)

    args = parser.parse_args()

    service = get_directory_service(args)

    args.func(service.tokens(), args)


if __name__ == '__main__':
    sys.stdout = codecs.getwriter('utf_8')(sys.stdout)
    main()
