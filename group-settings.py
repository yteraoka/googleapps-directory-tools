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
    print "email:                       %s" % resource['email']
    print "name:                        %s" % resource['name']
    print "description:                 %s" % resource['description']
    print "allowExternalMembers:        %s" % resource['allowExternalMembers']
    print "allowGoogleCommunication:    %s" % resource['allowGoogleCommunication']
    print "allowWebPosting:             %s" % resource['allowWebPosting']
    print "archiveOnly:                 %s" % resource['archiveOnly']
    print "customReplyTo:               %s" % resource['customReplyTo']
    #print "defaultMessageDenyNotificationText: %s" % resource['defaultMessageDenyNotificationText']
    print "includeInGlobalAddressList:  %s" % resource['includeInGlobalAddressList']
    print "isArchived:                  %s" % resource['isArchived']
    print "kind:                        %s" % resource['kind']
    print "maxMessageBytes:             %s" % resource['maxMessageBytes']
    print "membersCanPostAsTheGroup:    %s" % resource['membersCanPostAsTheGroup']
    print "messageDisplayFont:          %s" % resource['messageDisplayFont']
    print "messageModerationLevel:      %s" % resource['messageModerationLevel']
    print "replyTo:                     %s" % resource['replyTo']
    print "sendMessageDenyNotification: %s" % resource['sendMessageDenyNotification']
    print "showInGroupDirectory:        %s" % resource['showInGroupDirectory']
    print "spamModerationLevel:         %s" % resource['spamModerationLevel']
    print "whoCanContactOwner:          %s" % resource['whoCanContactOwner']
    print "whoCanInvite:                %s" % resource['whoCanInvite']
    print "whoCanJoin:                  %s" % resource['whoCanJoin']
    print "whoCanLeaveGroup:            %s" % resource['whoCanLeaveGroup']
    print "whoCanPostMessage:           %s" % resource['whoCanPostMessage']
    print "whoCanViewGroup:             %s" % resource['whoCanViewGroup']
    print "whoCanViewMembership:        %s" % resource['whoCanViewMembership']


def main(argv):
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    subparsers = parser.add_subparsers(help='sub command')

    #-------------------------------------------------------------------------
    # GET
    #-------------------------------------------------------------------------
    parser_get = subparsers.add_parser('get', help='Retrieves group properties')
    parser_get.add_argument('groupUniqueId', help='group email address')
    parser_get.add_argument('--json', action='store_true', help='output in JSON')
    parser_get.add_argument('--jsonPretty', action='store_true', help='output in pretty JSON')

    #-------------------------------------------------------------------------
    # PATCH
    #-------------------------------------------------------------------------
    parser_patch = subparsers.add_parser('patch', help='Updates group properties')
    parser_patch.add_argument('groupUniqueId', help='group email address')
    parser_patch.add_argument('--whoCanInvite',
                              choices=['ALL_MANAGERS_CAN_INVITE', 'ALL_MEMBERS_CAN_INVITE'])
    parser_patch.add_argument('--whoCanJoin',
                              choices=['ANYONE_CAN_JOIN',
                                       'ALL_IN_DOMAIN_CAN_JOIN',
                                       'INVITED_CAN_JOIN',
                                       'CAN_REQUEST_TO_JOIN'])
    parser_patch.add_argument('--whoCanPostMessage',
                              choices=['ALL_IN_DOMAIN_CAN_POST',
                                       'ALL_MANAGERS_CAN_POST',
                                       'ALL_MEMBERS_CAN_POST',
                                       'ANYONE_CAN_POST',
                                       'NONE_CAN_POST'])
    parser_patch.add_argument('--whoCanViewGroup',
                              choices=['ALL_IN_DOMAIN_CAN_VIEW',
                                       'ALL_MANAGERS_CAN_VIEW',
                                       'ALL_MEMBERS_CAN_VIEW',
                                       'ANYONE_CAN_VIEW'])
    parser_patch.add_argument('--whoCanViewMembership',
                              choices=['ALL_IN_DOMAIN_CAN_VIEW',
                                       'ALL_MANAGERS_CAN_VIEW',
                                       'ALL_MEMBERS_CAN_VIEW'])
    parser_patch.add_argument('--messageModerationLevel',
                              choices=['MODERATE_ALL_MESSAGES',
                                       'MODERATE_NON_MEMBERS',
                                       'MODERATE_NEW_MEMBERS',
                                       'MODERATE_NONE'])
    parser_patch.add_argument('--spamModerationLevel',
                              choices=['ALLOW',
                                       'MODERATE',
                                       'SILENTLY_MODERATE',
                                       'REJECT'])
    parser_patch.add_argument('--whoCanLeaveGroup',
                              choices=['ALL_MANAGERS_CAN_LEAVE',
                                       'ALL_MEMBERS_CAN_LEAVE'])
    parser_patch.add_argument('--whoCanContactOwner',
                              choices=['ALL_IN_DOMAIN_CAN_CONTACT',
                                       'ALL_MANAGERS_CAN_CONTACT',
                                       'ALL_MEMBERS_CAN_CONTACT',
                                       'ANYONE_CAN_CONTACT'])
    parser_patch.add_argument('--messageDisplayFont',
                              choices=['DEFAULT_FONT', 'FIXED_WIDTH_FONT'])
    parser_patch.add_argument('--replyTo',
                              choices=['REPLY_TO_CUSTOM',
                                       'REPLY_TO_SENDER',
                                       'REPLY_TO_LIST',
                                       'REPLY_TO_OWNER',
                                       'REPLY_TO_IGNORE',
                                       'REPLY_TO_MANAGERS'])
    parser_patch.add_argument('--membersCanPostAsTheGroup', choices=['true', 'false'])
    parser_patch.add_argument('--includeInGlobalAddressList', choices=['true', 'false'])
    parser_patch.add_argument('--customReplyTo', help='Reply-To header (REPLY_TO_CUSTOM)')
    parser_patch.add_argument('--sendMessageDenyNotification', choices=['true', 'false'])
    parser_patch.add_argument('--defaultMessageDenyNotificationText')
    parser_patch.add_argument('--showInGroupDirectory', choices=['true', 'false'])
    parser_patch.add_argument('--allowGoogleCommunication', choices=['true', 'false'])
    parser_patch.add_argument('--allowExternalMembers', choices=['true', 'false'])
    parser_patch.add_argument('--allowWebPosting', choices=['true', 'false'])
    parser_patch.add_argument('--primaryLanguage', choices=['ja', 'en-US'])
    parser_patch.add_argument('--maxMessageBytes', type=int)
    parser_patch.add_argument('--isArchived', choices=['true', 'false'])
    parser_patch.add_argument('--archiveOnly', choices=['true', 'false'])
    parser_patch.add_argument('--json', action='store_true', help='output in JSON')
    parser_patch.add_argument('--jsonPretty', action='store_true', help='output in pretty JSON')

    args = parser.parse_args(argv[1:])

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

    service = build('groupssettings', 'v1', http=http)

    sv = service.groups()

    command = argv[1]

    if command == "get":
        r = sv.get(groupUniqueId=args.groupUniqueId).execute()
        if args.jsonPretty:
            print to_pretty_json(r)
        elif args.json:
            print to_json(r)
        else:
            show_resource(r)
    elif command == "patch":
        body = {}
        if args.whoCanInvite:
            body['whoCanInvite'] = args.whoCanInvite
        if args.whoCanJoin:
            body['whoCanJoin'] = args.whoCanJoin
        if args.whoCanPostMessage:
            body['whoCanPostMessage'] = args.whoCanPostMessage
        if args.whoCanViewGroup:
            body['whoCanViewGroup'] = args.whoCanViewGroup
        if args.whoCanViewMembership:
            body['whoCanViewMembership'] = args.whoCanViewMembership
        if args.messageModerationLevel:
            body['messageModerationLevel'] = args.messageModerationLevel
        if args.spamModerationLevel:
            body['spamModerationLevel'] = args.spamModerationLevel
        if args.whoCanLeaveGroup:
            body['whoCanLeaveGroup'] = args.whoCanLeaveGroup
        if args.whoCanContactOwner:
            body['whoCanContactOwner'] = args.whoCanContactOwner
        if args.messageDisplayFont:
            body['messageDisplayFont'] = args.messageDisplayFont
        if args.replyTo:
            body['replyTo'] = args.replyTo
        if args.membersCanPostAsTheGroup:
            body['membersCanPostAsTheGroup'] = args.membersCanPostAsTheGroup
        if args.includeInGlobalAddressList:
            body['includeInGlobalAddressList'] = args.includeInGlobalAddressList
        if args.customReplyTo:
            body['customReplyTo'] = args.customReplyTo
        if args.sendMessageDenyNotification:
            body['sendMessageDenyNotification'] = args.sendMessageDenyNotification
        if args.defaultMessageDenyNotificationText:
            body['defaultMessageDenyNotificationText'] = args.defaultMessageDenyNotificationText
        if args.showInGroupDirectory:
            body['showInGroupDirectory'] = args.showInGroupDirectory
        if args.allowGoogleCommunication:
            body['allowGoogleCommunication'] = args.allowGoogleCommunication
        if args.allowExternalMembers:
            body['allowExternalMembers'] = args.allowExternalMembers
        if args.allowWebPosting:
            body['allowWebPosting'] = args.allowWebPosting
        if args.primaryLanguage:
            body['primaryLanguage'] = args.primaryLanguage
        if args.maxMessageBytes:
            body['maxMessageBytes'] = args.maxMessageBytes
        if args.isArchived:
            body['isArchived'] = args.isArchived
        if args.archiveOnly:
            body['archiveOnly'] = args.archiveOnly
        if len(body) > 0:
            r = sv.update(groupUniqueId=args.groupUniqueId, body=body).execute()
            if args.jsonPretty:
                print to_pretty_json(r)
            elif args.json:
                print to_json(r)
            else:
                show_resource(r)
        else:
            print "no update column"
            return

if __name__ == '__main__':
    main(sys.argv)
