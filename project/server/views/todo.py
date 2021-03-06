from flask import Blueprint, request, make_response, jsonify, g
from flask.views import MethodView

from project.server.models import Todo, User, Notification
from project.server import app, db
from project.server.views.decorators import login_required


bp_todo = Blueprint('todo', __name__)


@bp_todo.route('/todo/', methods=['GET'])
@login_required
def get_all_todo():
    todos = Todo.query.filter_by(account_id=g.account_id).all()
    
    responseObject = {
        'status': 'success',
        'message': 'Successfully fetched to-dos',
        'data': [todo.serialize() for todo in todos]
    }
    return make_response(jsonify(responseObject)), 200

@bp_todo.route('/todo/notification/', methods=['POST'])
@login_required
def check_notifications():
    action = request.args.get('action', 'read')
    if action == 'read':
        notifications = Notification.query.filter_by(user_id=g.user_id, seen=False).all()
        for notification in notifications:
            notification.seen = True
            db.session.add(notification)
        db.session.commit()

        responseObject = {
            'status': 'success',
            'message': '{} notifications read.'.format(len(notifications))
        }
        return make_response(jsonify(responseObject)), 200
    else:
        responseObject = {
            'status': 'fail',
            'message': 'No such action defined.'
        }
        return make_response(jsonify(responseObject)), 404

@bp_todo.route('/todo/<id>/', methods=['GET'])
@login_required
def get_todo(id):
    todo = Todo.query.filter_by(id=id, account_id=g.account_id).first()
    
    if todo:
        responseObject = {
            'status': 'success',
            'message': 'Successfully fetched to-do',
            'data': todo.serialize()
        }
        return make_response(jsonify(responseObject)), 200
    else:
        responseObject = {
            'status': 'fail',
            'message': 'No such todo exists'
        }
        return make_response(jsonify(responseObject)), 404

@bp_todo.route('/todo/<id>/', methods=['DELETE'])
@login_required
def delete_todo(id):
    todo = Todo.query.filter_by(id=id, account_id=g.account_id).first()
    
    if todo:
        db.session.delete(todo)
        db.session.commit()
        responseObject = {
            'status': 'success',
            'message': 'To-do deleted successfully'
        }
        return make_response(jsonify(responseObject)), 200
    else:
        responseObject = {
            'status': 'fail',
            'message': 'No such to-do exists'
        }
        return make_response(jsonify(responseObject)), 404

@bp_todo.route('/todo/', methods=['POST'])
@login_required
def create_todo():
    post_data = request.get_json()
    try:
        todo = Todo(account_id=g.account_id, data=post_data)
        if todo.user_id != g.user_id and todo.user_id is not None:
            if not Notification.query.filter_by(account_id=g.account_id, user_id=todo.user_id, seen=False, todo_id=todo.id).first():
                notification = Notification(account_id=g.account_id, user_id=todo.user_id, data={})
                todo.notifications.append(notification)
        db.session.add(todo)
        db.session.commit()
        responseObject = {
                'status': 'success',
                'message': 'Successfully created to-do',
                'data': todo.serialize()
            }
        return make_response(jsonify(responseObject)), 201
    except Exception as e:
        responseObject = {
                'status': 'fail',
                'message': 'Error while creating.',
                'details': str(e)
            }
        return make_response(jsonify(responseObject)), 400

@bp_todo.route('/todo/<id>/', methods=['PUT'])
@login_required
def update_todo(id):
    put_data = request.get_json()
    try:
        todo = Todo.query.get(id)
        todo.update(put_data)
        if todo.user_id != g.user_id and todo.user_id is not None:
            if not Notification.query.filter_by(account_id=g.account_id, user_id=todo.user_id, seen=False, todo_id=todo.id).first():
                notification = Notification(account_id=g.account_id, user_id=todo.user_id, data={})
                todo.notifications.append(notification)
        db.session.add(todo)
        db.session.commit()
        responseObject = {
                'status': 'success',
                'message': 'Successfully updated to-do',
                'data': todo.serialize()
            }
        return make_response(jsonify(responseObject)), 201
    except Exception as e:
        responseObject = {
                'status': 'fail',
                'message': 'Error while updating.',
                'details': str(e)
            }
        return make_response(jsonify(responseObject)), 400