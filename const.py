import os

SCOPES = [
    'https://www.googleapis.com/auth/admin.directory.user',
    'https://www.googleapis.com/auth/admin.directory.user.alias',
    'https://www.googleapis.com/auth/admin.directory.group',
    'https://www.googleapis.com/auth/admin.directory.group.member',
    'https://www.googleapis.com/auth/admin.directory.orgunit',
    'https://www.googleapis.com/auth/apps.groups.settings',
    'https://www.googleapis.com/auth/calendar'
]
if os.getenv('CLIENT_SECRETS'):
    CLIENT_SECRETS = os.getenv('CLIENT_SECRETS')
else:
    CLIENT_SECRETS = 'private/client_secret.json'

if os.getenv('CREDENTIALS_PATH'):
    CREDENTIALS_PATH = os.getenv('CREDENTIALS_PATH')
else:
    CREDENTIALS_PATH = 'private/credential.dat'

MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the APIs Console <https://code.google.com/apis/console>.

""" % os.path.join(os.path.dirname(__file__), CLIENT_SECRETS)
