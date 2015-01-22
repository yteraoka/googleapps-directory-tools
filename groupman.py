#!/apps/python-2.7/bin/python
# -*- coding: utf-8 -*-

import os
import os.path
import glob
import sys
from apiclient.discovery import build
from apiclient.errors import HttpError
import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client import tools
import argparse
import simplejson as json
import pprint
import codecs
import yaml
import re
from termcolor import colored

from const import *
from utils import *

GROUP_PARAMS = ['name', 'description', 'aliases', 'allowExternalMembers',
                'allowGoogleCommunication',
                'allowWebPosting', 'archiveOnly', 'customReplyTo',
                'includeInGlobalAddressList', 'isArchived',
                'maxMessageBytes', 'membersCanPostAsTheGroup',
                'messageDisplayFont', 'messageModerationLevel',
                'primaryLanguage', 'replyTo',
                'sendMessageDenyNotification', 'showInGroupDirectory',
                'spamModerationLevel', 'whoCanContactOwner',
                'whoCanInvite', 'whoCanJoin', 'whoCanLeaveGroup',
                'whoCanPostMessage', 'whoCanViewGroup',
                'whoCanViewMembership']

class GaService(object):
    def __init__(self, cred_path = CREDENTIALS_PATH):
        storage = Storage(cred_path)
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            sys.exit(1)

        http = httplib2.Http()
        http = credentials.authorize(http)

        sv1 = build('admin', 'directory_v1', http=http)
        sv2 = build('groupssettings', 'v1', http=http)

        self.service = {}
        self.service['group'] = sv1.groups()
        self.service['member'] = sv1.members()
        self.service['settings'] = sv2.groups()

    def group_sv(self):
        return self.service['group']

    def member_sv(self):
        return self.service['member']

    def settings_sv(self):
        return self.service['settings']

    def list_local_groups(self, domain, dir):
        groups = []
        for f in glob.glob("%s/*@%s.yml" % (dir, domain)):
            email = os.path.splitext(os.path.basename(f))[0]
            group_obj = GaGroup()
            group_obj.set_group_key(email)
            groups.append(group_obj)
        return groups

    def list_cloud_groups(self, domain):
        groups = []
        pageToken = None
        while True:
            params = { 'domain': domain }
            if pageToken:
                params['pageToken'] = pageToken
            r = self.service['group'].list(**params).execute()
            if r.has_key('groups'):
                for group in r['groups']:
                    group_obj = GaGroup()
                    group_obj.set_group_key(group['email'])
                    groups.append(group_obj)
            if r.has_key('nextPageToken'):
                pageToken = r['nextPageToken']
            else:
                break

        return groups

class GaGroup(object):
    def __init__(self):
        self.local_dir = '.'
        self.local = {}
        self.cloud = {}
        self.group_key = None

    def set_group_key(self, group_key):
        self.group_key = group_key

    def set_local_dir(self, local_dir):
        self.local_dir = local_dir

    def group_key(self):
        return self.group_key

    def load_cloud(self, sv):
        r = sv.settings_sv().get(groupUniqueId=self.group_key).execute()
        self.cloud = r
        members = self.load_cloud_member(sv)
        self.cloud['members']  = []
        self.cloud['owners']   = []
        self.cloud['managers'] = []
        for member in members:
            if member['role'] == 'MEMBER':
                self.cloud['members'].append(member['email'])
            elif member['role'] == 'MANAGER':
                self.cloud['managers'].append(member['email'])
            elif member['role'] == 'OWNER':
                self.cloud['owners'].append(member['email'])
        self.cloud['members'].sort()
        self.cloud['owners'].sort()
        self.cloud['managers'].sort()
        r = sv.group_sv().get(groupKey=self.group_key).execute()
        if r.has_key('aliases'):
            self.cloud['aliases'] = r['aliases']

    def load_cloud_member(self, sv):
        members = []
        pageToken = None
        while True:
            params = { 'groupKey': self.group_key }
            if pageToken:
                params['pageToken'] = pageToken
            r = sv.member_sv().list(**params).execute()
            if r.has_key('members'):
                for member in r['members']:
                    members.append(member)
            if r.has_key('nextPageToken'):
                pageToken = r['nextPageToken']
            else:
                break
        return members

    def dump_data(self, data, stream):
        stream.write("email: %s\n" % data['email'])
        for key in GROUP_PARAMS:
            if data.has_key(key):
                if key in ['name', 'description']:
                    stream.write("%s: \"%s\"\n" % (key, re.sub(r'"', '\\"', data[key]).encode('utf-8')))
                elif key in ['maxMessageBytes']:
                    stream.write("%s: %s\n" % (key, data[key]))
                elif key in ['aliases']:
                    if len(data[key]):
                        stream.write("%s:\n" % key)
                        for val in data[key]:
                            stream.write("  - %s\n" % val)
                    else:
                        stream.write("%s: []\n" % key)
                else:
                    stream.write("%s: \"%s\"\n" % (key, data[key]))

        if len(data['members']):
            stream.write("members:\n")
            for member in data['members']:
                stream.write("  - %s\n" % member)
        else:
            stream.write("members: []\n")

        if len(data['managers']):
            stream.write("managers:\n")
            for member in data['managers']:
                stream.write("  - %s\n" % member)
        else:
            stream.write("managers: []\n")

        if len(data['owners']):
            stream.write("owners:\n")
            for member in data['owners']:
                stream.write("  - %s\n" % member)
        else:
            stream.write("owners: []\n")

    def dump_cloud(self):
        self.dump_data(self.cloud, sys.stdout)

    def local_file(self):
        file = "%s/%s.yml" % (self.local_dir, self.group_key)
        return file

    def export(self):
        f = open(self.local_file(), 'w')
        self.dump_data(self.cloud, f)
        f.close()

    def load_local(self):
        file = self.local_file()
        if os.path.exists(file):
            self.local = yaml.load(open(file).read().decode('utf-8'))

    def diff(self):
        if not self.local.has_key('name'):
            self.load_local()
        for key in GROUP_PARAMS:
            if self.local.has_key(key) and self.cloud.has_key(key):
                if self.local[key] != self.cloud[key]:
                    print colored("-%s: %s (cloud)" % (key, self.cloud[key]), 'red')
                    print colored("+%s: %s (local)" % (key, self.local[key]), 'green')
            elif self.local.has_key(key):
                    print colored("+%s: %s (local)" % (key, self.local[key]), 'green')
            elif self.cloud.has_key(key):
                    print colored("-%s: %s (cloud)" % (key, self.cloud[key]), 'red')
        for key in ['members', 'managers', 'owners']:
            only_cloud = [x for x in self.cloud[key] if x not in self.local[key]]
            only_local = [x for x in self.local[key] if x not in self.cloud[key]]
            if len(only_cloud):
                print "%s:" % key
                for x in only_cloud:
                    print colored("-  - %s (cloud)" % x, 'red')
                for x in only_local:
                    print colored("+  - %s (local)" % x, 'green')

    def apply(self, sv):
        if not self.local.has_key('name'):
            self.load_local()
        body = {}
        update_keys = []
        for key in GROUP_PARAMS:
            if key not in ['name', 'description', 'aliases']:
                if self.cloud[key] != self.local[key]:
                    body[key] = self.local[key]
        if len(body) > 0:
            r = sv.settings_sv().update(groupUniqueId=self.group_key, body=body).execute()
            print "updated"
        else:
            print "no changes"

    def csv(self):
        if not self.local.has_key('name'):
            self.load_local()
        description = re.sub(r'\s*\[sateraito.*$', '', self.local['description'])
        return '"IU","%s","%s","%s","%s","%s"' % (self.local['email'],
                                                  self.local['name'],
                                                  ','.join(self.local['members']),
                                                  ','.join(self.local['owners']),
                                                  re.sub(r'"', '""', description))

def csv_header():
    return '"command","email","name","members","owners","comment"'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('operation',
                        choices=['show', 'diff', 'export', 'apply', 'csv'],
                        help='operationo')
    parser.add_argument('targets', nargs='+', help='domain or email list')
    parser.add_argument('--dir', help='local data directory', default='.')
    parser.add_argument('--encoding',
                        choices=['utf-8', 'sjis'],
                        help='csv output encoding',
                        default='utf-8')
    args = parser.parse_args()

    sv = GaService()

    groups = []

    for target in args.targets:
        if target.find('@') >= 0:
            g = GaGroup()
            g.set_group_key(target)
            groups.append(g)
        else:
            if args.operation == 'csv':
                groups.extend(sv.list_local_groups(target, args.dir))
            else:
                groups.extend(sv.list_cloud_groups(target))

    if args.operation == 'csv':
        print csv_header()

    for group in groups:
        group.set_local_dir(args.dir)
        if args.operation != 'csv':
            print group.group_key
            group.load_cloud(sv)
        if args.operation == 'show':
            group.dump_cloud()
        elif args.operation == 'export':
            group.export()
        elif args.operation == 'diff':
            group.diff()
        elif args.operation == 'apply':
            group.apply(sv)
        elif args.operation == 'csv':
            print group.csv().encode(args.encoding)

if __name__ == '__main__':
    main()
