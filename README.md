googleapps-directory-tools
==========================

command line tools for managing google apps users and groups

## Setup

1. Install google-api-python-client and simplejson. `pip install google-api-python-client simplejson`
2. Clone this project
3. Get Client ID from [Google Developer Console](https://console.developers.google.com/)
  1. Create new project of select exists project
  2. Click "Create new Client ID" in Credentials tab
  3. Select "Installed application" and "Other" application type then click "Create Client ID"
  4. Click "Download JSON"
4. Save Downloaded JSON file to `private/client_secret.json`
5. Run `user.py --noauth_local_webserver`
  1. Access displayed URL
  2. Approve request
  3. Copy and pasete the code to terminal
  4. Ignore error message (like unknown command --noauth_local_webserver)
6. Ready. Try get user list. `user.py list your.domain.name`

Tested with Python 2.7.6 only.

## Supported Operations

### Orgunits

https://developers.google.com/admin-sdk/directory/v1/reference/orgunits

```
$ ./orgunit.py -h
usage: orgunit.py [-h] [--auth_host_name AUTH_HOST_NAME]
                  [--noauth_local_webserver]
                  [--auth_host_port [AUTH_HOST_PORT [AUTH_HOST_PORT ...]]]
                  [--logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                  {list,get,insert,patch,delete} ...

positional arguments:
  {list,get,insert,patch,delete}
                        sub command
    list                Retrieves a list of all organization units for an
                        account
    get                 Retrieves an organization unit
    insert              Adds an organization unit
    patch               Updates an organization unit
    delete              Removes an organization unit
```

### Users

https://developers.google.com/admin-sdk/directory/v1/reference/users

```
$ ./user.py -h
usage: user.py [-h] [--auth_host_name AUTH_HOST_NAME]
               [--noauth_local_webserver]
               [--auth_host_port [AUTH_HOST_PORT [AUTH_HOST_PORT ...]]]
               [--logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
               {list,get,insert,patch,delete,setadmin,unsetadmin,bulkinsert}
               ...

positional arguments:
  {list,get,insert,patch,delete,setadmin,unsetadmin,bulkinsert}
                        sub command
    list                Retrieves a paginated list of either deleted users or
                        all users in a domain
    get                 Retrieves a user
    insert              Creates a user
    patch               Updates a user
    delete              Deletes a user
    setadmin            Makes a user a super administrator
    unsetadmin          Makes a user a normal user
    bulkinsert          bulk insert
```

### Users.aliases

https://developers.google.com/admin-sdk/directory/v1/reference/users/aliases

```
$ ./user-alias.py -h
usage: user-alias.py [-h] [--auth_host_name AUTH_HOST_NAME]
                     [--noauth_local_webserver]
                     [--auth_host_port [AUTH_HOST_PORT [AUTH_HOST_PORT ...]]]
                     [--logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                     {list,insert,delete} ...

positional arguments:
  {list,insert,delete}  sub command
    list                Lists all aliases for a user
    insert              Adds an alias
    delete              Removes an alias
```

### Groups

https://developers.google.com/admin-sdk/directory/v1/reference/groups

```
$ ./group.py -h
usage: group.py [-h] [--auth_host_name AUTH_HOST_NAME]
                [--noauth_local_webserver]
                [--auth_host_port [AUTH_HOST_PORT [AUTH_HOST_PORT ...]]]
                [--logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                {list,get,insert,patch,delete,bulkinsert} ...

positional arguments:
  {list,get,insert,patch,delete,bulkinsert}
                        sub command
    list                Retrieves list of groups in a domain
    get                 Retrieves a group's properties
    insert              Creates a group
    patch               Updates a group's properties
    delete              Deletes a group
    bulkinsert          bulk insert
```

### Groups.aliases

https://developers.google.com/admin-sdk/directory/v1/reference/groups/aliases

```
$ ./group-alias.py -h
usage: group-alias.py [-h] [--auth_host_name AUTH_HOST_NAME]
                      [--noauth_local_webserver]
                      [--auth_host_port [AUTH_HOST_PORT [AUTH_HOST_PORT ...]]]
                      [--logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                      {list,insert,delete} ...

positional arguments:
  {list,insert,delete}  sub command
    list                Lists all aliases for a group
    insert              Adds an alias for the group
    delete              Removes an alias
```

### Members

https://developers.google.com/admin-sdk/directory/v1/reference/members

```
$ ./member.py -h
usage: member.py [-h] [--auth_host_name AUTH_HOST_NAME]
                 [--noauth_local_webserver]
                 [--auth_host_port [AUTH_HOST_PORT [AUTH_HOST_PORT ...]]]
                 [--logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                 {list,get,insert,patch,update,delete} ...

positional arguments:
  {list,get,insert,patch,update,delete}
                        sub command
    list                Retrieves list of all members in a group
    get                 Retrieves a group member's properties
    insert              Adds a user to the specified group
    patch               Updates the membership properties of a user in the
                        specified group
    update              Updates the membership of a user in the specified
                        group
    delete              Removes a member from a group
```

### Groups for business

https://developers.google.com/admin-sdk/groups-settings/v1/reference/groups

```
$ ./group-settings.py -h
usage: group-settings.py [-h] [--auth_host_name AUTH_HOST_NAME]
                         [--noauth_local_webserver]
                         [--auth_host_port [AUTH_HOST_PORT [AUTH_HOST_PORT ...]]]
                         [--logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                         {get,patch} ...

positional arguments:
  {get,patch}           sub command
    get                 Retrieves group properties
    patch               Updates group properties
```
