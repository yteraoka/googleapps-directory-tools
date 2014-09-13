#!/usr/bin/env python

import os
import sys
import gdata.apps.emailsettings.client
import argparse
import getpass

def login(args):
    client = gdata.apps.emailsettings.client.EmailSettingsClient(domain=args.domain)
    client.ClientLogin(email=args.admin,
                       password=args.password,
                       source='mail-forward-setting')
    return client

def get_forward(args):
    client = login(args)
    setting = client.RetrieveForwarding(username=args.user)

    if setting.enable == 'true':
        print "%s,%s,%s,%s" % (args.user, setting.enable, setting.action, setting.forward_to)
    else:
        print "%s,%s,," % (args.user, setting.enable)

def set_forward(args):
    client = login(args)
    if args.enable == 'true':
        enable = True
        setting = client.UpdateForwarding(username=args.user,
                                      enable=enable,
                                      forward_to=args.forward_to,
                                      action=args.action)
        if setting.enable == 'true':
            print "%s,%s,%s,%s" % (args.user, setting.enable, setting.action, setting.forward_to)
        else:
            print "%s,%s,," % (args.user, setting.enable)
    else:
        enable = False
        setting = client.UpdateForwarding(username=args.user,
                                      enable=enable)
        if setting.enable == 'true':
            print "%s,%s,%s,%s" % (args.user, setting.enable, setting.action, setting.forward_to)
        else:
            print "%s,%s,," % (args.user, setting.enable)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--admin')
    parser.add_argument('-p', '--password')
    parser.add_argument('-d', '--domain')
    subparsers = parser.add_subparsers(help='sub command')

    parser_get = subparsers.add_parser('get', help='Retrieveing Forwarding Settings')
    parser_get.add_argument('user', help='username or email address')
    parser_get.set_defaults(func=get_forward)

    parser_set = subparsers.add_parser('set', help='Updating Forwarding Setting')
    parser_set.add_argument('-e', '--enable', choices=['true', 'false'], required=True)
    parser_set.add_argument('user', help='username or email address')
    parser_set.add_argument('-f', '--forward_to', help='email address')
    parser_set.add_argument('-a', '--action', choices=['KEEP', 'DELETE', 'MARK_READ'])
    parser_set.set_defaults(func=set_forward)

    args = parser.parse_args()

    if args.admin is None:
        if 'GA_ADMIN_EMAIL' in os.environ:
            args.admin = os.environ['GA_ADMIN_EMAIL']
        else:
            print "--admin parameter or GA_ADMIN_EMAIL environment is required"
            sys.exit(1)

    if args.password is None:
        if 'GA_ADMIN_PASSWORD' in os.environ:
            args.password = os.environ['GA_ADMIN_PASSWORD']
        else:
            args.password = getpass.getpass('Password of %s: ' % args.admin)

    if args.domain is None:
        args.domain = args.admin.split('@')[1]

    args.func(args)

main()
