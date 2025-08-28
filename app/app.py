from flask import Flask

from users.create import create_user
from users.delete import delete_user
from users.move import move_user
from users.search import search_users

from groups.create import create_group
from groups.delete import delete_group
from groups.members import remove_user_from_group
from groups.search import search_groups

app = Flask(__name__)

# User routes
app.add_url_rule('/users', view_func=create_user, methods=['POST'])
app.add_url_rule('/users/<uid>', view_func=delete_user, methods=['DELETE'])
app.add_url_rule('/users/<uid>/move', view_func=move_user, methods=['PUT'])
app.add_url_rule('/users', view_func=search_users, methods=['GET'])

# Group routes
app.add_url_rule('/groups', view_func=create_group, methods=['POST'])
app.add_url_rule('/groups/<group>', view_func=delete_group, methods=['DELETE'])
app.add_url_rule('/groups/<group>/members/<uid>', view_func=remove_user_from_group, methods=['DELETE'],
)
app.add_url_rule('/groups', view_func=search_groups, methods=['GET'])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5034)
