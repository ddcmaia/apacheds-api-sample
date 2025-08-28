# Flask AD CRUD API

This application exposes a simple CRUD over an ApacheDS server.

## Example commands

### User operations

#### Create user
```bash
curl -X POST http://localhost:5034/users \
  -H 'Content-Type: application/json' \
  -d '{"uid":"user1","cn":"User One","sn":"One"}'
```

#### Delete user
```bash
curl -X DELETE http://localhost:5034/users/user1
```

#### Move user between groups
```bash
curl -X PUT http://localhost:5034/users/user7/move \
  -H 'Content-Type: application/json' \
  -d '{"from":"GU_AUDITORS","to":"GG_ADMINS"}'
```

#### Search users
```bash
curl "http://localhost:5034/users?q=(uid=user1)"
```

### Group operations

#### Create group
```bash
curl -X POST http://localhost:5034/groups \
  -H 'Content-Type: application/json' \
  -d '{"cn":"GG_TEST","members":["uid=user1,ou=HeadOffice,ou=GROUP - Users,dc=people,dc=example,dc=com"],"owner":"user1"}'
```

#### Delete group
```bash
curl -X DELETE http://localhost:5034/groups/GG_TEST
```

#### Remove user from a group
```bash
curl -X DELETE "http://localhost:5034/groups/GG_TEST/members/user1?delete_empty_group=true"
```

#### Search groups
```bash
curl "http://localhost:5034/groups?q=(cn=GG_*)"
```

