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
                       source='mail-sendas-setting')
    return client

def list_sendas(args):
    client = login(args)
    setting = client.RetrieveSendAs(username=args.user)

    for entry in setting.entry:
        print "Name: %s" % entry.name
        print "Address: %s" % entry.address
        if entry.make_default is None:
            print "isDefault: false"
        else:
            print "isDefault: true"
        print "Reply-To: %s" % entry.reply_to
        print ""

def set_sendas(args):
    client = login(args)

    options = {}

    if args.replyTo is not None:
        options['replyTo'] = args.replyTo

    if args.makeDefault == True:
        options['makeDefault'] = 'true'
    else:
        options['makeDefault'] = 'false'

    setting = client.CreateSendAs(args.user, args.name, args.address, **options)

    print setting


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--admin')
    parser.add_argument('-p', '--password')
    parser.add_argument('-d', '--domain')
    subparsers = parser.add_subparsers(help='sub command')

    parser_list = subparsers.add_parser('list', help='Retrieveing All send-as Settings')
    parser_list.add_argument('user', help='username or email address')
    parser_list.set_defaults(func=list_sendas)

    parser_set = subparsers.add_parser('set', help='Create or Update send-as Setting')
    parser_set.add_argument('user', help='username or email address')
    parser_set.add_argument('name', help='"From" text')
    parser_set.add_argument('address', help='from email address')
    parser_set.add_argument('--replyTo')
    parser_set.add_argument('--makeDefault', action='store_true', default=False)
    parser_set.set_defaults(func=set_sendas)

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
