# Flask AD CRUD API

This application exposes a simple CRUD over an ApacheDS server.

Actions are logged to `audit.log`. If the `ENABLE_AUDIT_BUCKET` flag is set to `true` and `AUDIT_BUCKET` is defined with valid credentials, the log file is uploaded to the specified Google Cloud Storage bucket after each action.

## Example commands

### User operations

#### Create user
```bash
curl -X POST http://localhost:5034/users \
  -H 'Content-Type: application/json' \
  -d '{"uid":"user1","cn":"User One","sn":"One"}'
```

#### Deactivate user
Removes the user from all groups, marks the entry with `accountStatus=inactive`
and moves it to a dedicated `Desativados` OU instead of deleting it.
```bash
curl -X DELETE http://localhost:5034/users/user1
```

#### Move user between groups
```bash
curl -X PUT http://localhost:5034/users/user7/move \
  -H 'Content-Type: application/json' \
  -d '{"from":"GG_Auditors","to":"GG_Admins"}'
```
Moving a user out of a group also removes them as the group's owner. Ownership is reassigned to the parent group's owner so that the departing user becomes only a member of the new group. A group owner can never be outside the group they own.

#### Search users
```bash
curl "http://localhost:5034/users?q=(uid=user1)"
```

### Group operations

#### Create group
```bash
curl -X POST http://localhost:5034/groups \
  -H 'Content-Type: application/json' \
  -d '{"cn":"GG_Test","members":["uid=user1,ou=Matriz,ou=OrgUsers,dc=people,dc=example,dc=com"],"owner":"user1","parent":"GG_Engineering"}'
```

#### Delete group
```bash
curl -X DELETE http://localhost:5034/groups/GG_Test
```

#### Remove user from a group
```bash
curl -X DELETE "http://localhost:5034/groups/GG_Test/members/user1?delete_empty_group=true"
```

#### Set group owner
```bash
curl -X PUT http://localhost:5034/groups/GG_Test/owner/user2
```

#### Search groups
```bash
curl "http://localhost:5034/groups?q=(cn=GG_*)"
```

