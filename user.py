#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import codecs
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

def show_active_resource(resource):
    print "primaryEmail:               %s" % resource['primaryEmail']
    print "name:                       %s %s" % (resource['name']['familyName'], resource['name']['givenName'])
    if resource.has_key('agreeToTerms'):
        print "agreedToTerms:              %s" % resource['agreedToTerms']
    if resource.has_key('changePasswordAtNextLogin'):
        print "changePasswordAtNextLogin:  %s" % resource['changePasswordAtNextLogin']
    print "creationTime:               %s" % resource['creationTime']
    print "customerId:                 %s" % resource['customerId']
    for email in resource['emails']:
        if email.has_key('primary'):
            print "email:                      %s (primary)" % email['address']
        else:
            print "email:                      %s" % email['address']
    print "includeInGlobalAddressList: %s" % resource['includeInGlobalAddressList']
    print "ipWhitelisted:              %s" % resource['ipWhitelisted']
    print "isAdmin:                    %s" % resource['isAdmin']
    print "isDelegatedAdmin:           %s" % resource['isDelegatedAdmin']
    print "isMailboxSetup:             %s" % resource['isMailboxSetup']
    print "lastLoginTime:              %s" % resource['lastLoginTime']
    if resource.has_key('nonEditableAliases'):
        for email in resource['nonEditableAliases']:
            print "nonEditableAliases:         %s" % email
    print "orgUnitPath:                %s" % resource['orgUnitPath']
    print "suspended:                  %s" % resource['suspended']

def show_deleted_resource(resource):
    print "primaryEmail:               %s" % resource['primaryEmail']
    print "lastLoginTime:              %s" % resource['lastLoginTime']
    print "creationTime:               %s" % resource['creationTime']
    print "deletionTime:               %s" % resource['deletionTime']

def show_resource(resource):
    if resource.has_key('deletionTime'):
        show_deleted_resource(resource)
    else:
        show_active_resource(resource)

def show_resource_list(resources, verbose):
    for resource in resources:
        if verbose:
            show_resource(resource)
            print ""
        else:
            if resource.has_key('deletionTime'):
                print "%s\t%s" % (resource['primaryEmail'], resource['deletionTime'])
            else:
                print "%-32s %s %s" % (resource['primaryEmail'],
                                       resource['name']['familyName'],
                                       resource['name']['givenName'])

def list_user(sv, args):
    users = []
    pageToken = None
    while True:
        params = {}
        if args.domain:
            params['domain'] = args.domain
        if args.customer:
            params['customer'] = args.customer
        if args.reverse:
            params['sortOrder'] = 'DESCENDING'
        if args.showDeleted:
            params['showDeleted'] = 'true'
        if args.orderBy:
            params['orderBy'] = args.orderBy
        if args.query:
            params['query'] = args.query.decode('utf-8')
        if args.maxResults:
            params['maxResults'] = args.maxResults
        if pageToken:
            params['pageToken'] = pageToken

        if not params.has_key('domain') and not params.has_key('customer'):
            print "Either the customer or the domain parameter must be provided"
            sys.exit(1)

        r = sv.list(**params).execute()

        if r.has_key('users'):
            if args.jsonPretty or args.json:
                for user in r['users']:
                    users.append(user)
            else:
                show_resource_list(r['users'], args.verbose)
        if r.has_key('nextPageToken'):
            pageToken = r['nextPageToken']
        else:
            break

    if args.jsonPretty:
        if len(users) == 1:
            print to_pretty_json(users[0])
        else:
            print to_pretty_json(users)
    elif args.json:
        if len(users) == 1:
            print to_json(users[0])
        else:
            print to_json(users)

def get_user(sv, args):
    r = sv.get(userKey=args.userKey).execute()
    if args.jsonPretty:
        print to_pretty_json(r)
    elif args.json:
        print to_json(r)
    else:
        show_resource(r)

def insert_user(sv, args):
    body = { 'name': { 'familyName': args.familyName.decode('utf-8'),
                       'givenName': args.givenName.decode('utf-8') },
             'password': args.password,
             'primaryEmail': args.primaryEmail }
    if args.changePasswordAtNextLogin:
        body['changePasswordAtNextLogin'] = True if args.changePasswordAtNextLogin == 'true' else False
    if args.suspended:
        body['suspended'] = True if args.suspended == 'true' else False
    if args.orgUnitPath:
        body['orgUnitPath'] = args.orgUnitPath.decode('utf-8')
    r = sv.insert(body=body).execute()
    if args.verbose:
        if args.jsonPretty:
            print to_pretty_json(r)
        elif args.json:
            print to_json(r)
        else:
            show_resource(r)

def patch_user(sv, args):
    body = {}
    if args.familyName or args.givenName:
        body['name'] = {}
    if args.familyName:
        body['name']['familyName'] = args.familyName.decode('utf-8')
    if args.givenName:
        body['name']['givenName'] = args.givenName.decode('utf-8')
    if args.orgUnitPath:
        body['orgUnitPath'] = args.orgUnitPath.decode('utf-8')
    if args.suspended:
        body['suspended'] = True if args.suspended == 'true' else False
    if args.changePasswordAtNextLogin:
        body['changePasswordAtNextLogin'] = True if args.changePasswordAtNextLogin == 'true' else False
    if args.password:
        body['password'] = args.password
    if args.primaryEmail:
        body['primaryEmail'] = args.primaryEmail
    if len(body):
        r = sv.patch(userKey=args.userKey, body=body).execute()
        if args.verbose:
            if args.jsonPretty:
                print to_pretty_json(r)
            elif args.json:
                print to_json(r)
            else:
                show_resource(r)
    else:
        print 'no update column'

def delete_user(sv, args):
    r = sv.delete(userKey=args.userKey).execute()

def undelete_user(sv, args):
    body = { 'orgUnitPath': args.orgUnitPath.decode('utf-8') }
    r = sv.undelete(userKey=args.userKey, body=body).execute()

def setadmin_user(sv, args):
    r = sv.makeAdmin(userKey=args.userKey, body={ 'status': True }).execute()

def unsetadmin_user(sv, args):
    r = sv.makeAdmin(userKey=args.userKey, body={ 'status': False }).execute()

def bulk_insert_user(sv, args):
    f = open(args.jsonfile, 'r')
    users = json.load(f, 'utf-8')
    for user in users:
        r = sv.insert(body=user).execute()
        if args.verbose:
            if args.jsonPretty:
                print to_pretty_json(r)
            elif args.json:
                print to_json(r)
            else:
                show_resource(r)

def main():
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    subparsers = parser.add_subparsers(help='sub command')

    #-------------------------------------------------------------------------
    # LIST / SEARCH
    #-------------------------------------------------------------------------
    parser_list = subparsers.add_parser('list', help='Retrieves a paginated list of either deleted users or all users in a domain')
    parser_list.add_argument('-d', '--domain', help='search user by this domain')
    parser_list.add_argument('-c', '--customer', help='search user by this customerId')
    parser_list.add_argument('-v', '--verbose', action='store_true', help='show all user data')
    parser_list.add_argument('--json', action='store_true', help='output in JSON')
    parser_list.add_argument('--jsonPretty', action='store_true', help='output in pretty JSON')
    parser_list.add_argument('--orderBy', choices=['email', 'familyName', 'givenName'],
                             default='email', help='show all user data')
    parser_list.add_argument('--maxResults', type=int, help='Acceptable values are 1 to 500')
    parser_list.add_argument('-q', '--query', help='search query')
    parser_list.add_argument('-r', '--reverse', action='store_true', help='DESCENDING sort')
    parser_list.add_argument('--showDeleted', action='store_true', help='show deleted user only')
    parser_list.set_defaults(func=list_user)

    #-------------------------------------------------------------------------
    # GET
    #-------------------------------------------------------------------------
    parser_get = subparsers.add_parser('get', help='Retrieves a user')
    parser_get.add_argument('userKey', help='email address')
    parser_get.add_argument('--json', action='store_true', help='output in JSON')
    parser_get.add_argument('--jsonPretty', action='store_true', help='output in pretty JSON')
    parser_get.set_defaults(func=get_user)

    #-------------------------------------------------------------------------
    # INSERT
    #-------------------------------------------------------------------------
    parser_insert = subparsers.add_parser('insert', help='Creates a user')
    parser_insert.add_argument('primaryEmail')
    parser_insert.add_argument('password')
    parser_insert.add_argument('familyName')
    parser_insert.add_argument('givenName')
    parser_insert.add_argument('--changePasswordAtNextLogin', action='store_true',
                              help='set changePasswordAtNextLogin flag True')
    parser_insert.add_argument('--suspended', action='store_true',
                              help='change suspended status')
    parser_insert.add_argument('--orgUnitPath', help='org unit')
    parser_insert.add_argument('-v', '--verbose', action='store_true', help='show created user data')
    parser_insert.add_argument('--json', action='store_true', help='output in JSON')
    parser_insert.add_argument('--jsonPretty', action='store_true', help='output in pretty JSON')
    parser_insert.set_defaults(func=insert_user)

    #-------------------------------------------------------------------------
    # PATCH
    #-------------------------------------------------------------------------
    parser_patch = subparsers.add_parser('patch', help='Updates a user')
    parser_patch.add_argument('userKey')
    parser_patch.add_argument('--orgUnitPath', help='new org unit')
    parser_patch.add_argument('--primaryEmail', help='new email address')
    parser_patch.add_argument('--password', help='new password')
    parser_patch.add_argument('--givenName', help='new givenName')
    parser_patch.add_argument('--familyName', help='new familyName')
    parser_patch.add_argument('--suspended', choices=['true', 'false'],
                              help='change suspended status')
    parser_patch.add_argument('--changePasswordAtNextLogin', choices=['true', 'false'],
                              help='change changePasswordAtNextLogin status')
    parser_patch.add_argument('-v', '--verbose', action='store_true', help='show updated user data')
    parser_patch.add_argument('--json', action='store_true', help='output in JSON')
    parser_patch.add_argument('--jsonPretty', action='store_true', help='output in pretty JSON')
    parser_patch.set_defaults(func=patch_user)

    #-------------------------------------------------------------------------
    # DELETE
    #-------------------------------------------------------------------------
    parser_delete = subparsers.add_parser('delete', help='Deletes a user')
    parser_delete.add_argument('userKey')
    parser_delete.set_defaults(func=delete_user)

    #-------------------------------------------------------------------------
    # SETADMIN
    #-------------------------------------------------------------------------
    parser_setadmin = subparsers.add_parser('setadmin', help='Makes a user a super administrator')
    parser_setadmin.add_argument('userKey')
    parser_setadmin.set_defaults(func=setadmin_user)

    #-------------------------------------------------------------------------
    # UNSETADMIN
    #-------------------------------------------------------------------------
    parser_unsetadmin = subparsers.add_parser('unsetadmin', help='Makes a user a normal user')
    parser_unsetadmin.add_argument('userKey')
    parser_unsetadmin.set_defaults(func=unsetadmin_user)

    #-------------------------------------------------------------------------
    # BULK INSERT
    #-------------------------------------------------------------------------
    parser_bi = subparsers.add_parser('bulkinsert', help='bulk insert')
    parser_bi.add_argument('jsonfile')
    parser_bi.add_argument('-v', '--verbose', action='store_true', help='show created user data')
    parser_bi.add_argument('--json', action='store_true', help='output in JSON')
    parser_bi.add_argument('--jsonPretty', action='store_true', help='output in pretty JSON')
    parser_bi.set_defaults(func=bulk_insert_user)

    args = parser.parse_args()
    
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

    sv = service.users()

    args.func(sv, args)

if __name__ == '__main__':
    sys.stdout = codecs.getwriter('utf_8')(sys.stdout)
    main()
