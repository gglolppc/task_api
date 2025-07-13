from flask import Blueprint, request, jsonify, g
from db.models import Task
from utils.data_validation import TaskValidator, TaskUpdateModel
from utils.token_check import token_check
from pydantic import ValidationError
from datetime import datetime, timezone
from errors.exceptions import APIError
import logging
tasks = Blueprint('tasks', __name__)

@tasks.route('/add_task', methods=['POST'])
@token_check
def add_task():
    data = request.get_json(silent=True)
    if not data:
        raise APIError('No input data', status_code=400)
    try:
        task = TaskValidator(title=data.get('title'),
                             description=data.get('description'),
                             status=data.get('status'),
                             priority=data.get('priority'),
                             deadline=data.get('deadline'))
        if task.deadline < datetime.now(timezone.utc):
            raise APIError('Deadline must be greater than now', status_code=400)
        s = g.db
        new_task = Task(title=task.title,
                        description=task.description,
                        status=task.status or 'pending',
                        created_at=datetime.now(timezone.utc),
                        deadline=task.deadline,
                        priority=task.priority or 'low',
                        user_id = g.user_id)
        s.add(new_task)
        logging.info(f'User {g.user_id} added new task')
    except ValidationError as e:
        return jsonify({'Error': str(e)}), 400
    return jsonify({'message':'Task added'}), 201

@tasks.route('/get_tasks', methods=['GET'])
@token_check
def get_tasks():
    s = g.db
    query = s.query(Task).filter_by(user_id=g.user_id)
    total = query.count()

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page - 1) * per_page
    total_pages = (total + per_page - 1) // per_page if per_page else 1

    status = request.args.get('status', '').lower()
    priority = request.args.get('priority', '').lower()

    allowed_statuses = {'pending', 'done', 'failed'}
    allowed_priorities = {'low', 'medium', 'high'}

    if status:
        if status not in allowed_statuses:
            raise APIError('Invalid task status', status_code=400)
        query = query.filter(Task.status == status)

    if priority:
        if priority not in allowed_priorities:
            raise APIError('Invalid task priority', status_code=400)
        query = query.filter(Task.priority == priority)
    if page and per_page:
        query = query.offset(offset).limit(per_page)
    result = query.all()

    return jsonify({
        'tasks': [task.to_dict() for task in result],
        'filtered tasks': len(result),
        'total tasks': total,
        'page': page,
        'total pages': total_pages,
    }), 200

@tasks.route('/<int:task_id>', methods=['PUT'])
@token_check
def update_task(task_id):
    data = request.get_json(silent=True)
    if not data:
        raise APIError('No input data', status_code=400)
    s = g.db
    task = s.query(Task).filter_by(id=task_id, user_id= g.user_id).first()
    if not task:
        raise APIError('Task not found', status_code=404)
    try:
        task_data = TaskUpdateModel(**data)
        for key, value in task_data.model_dump(exclude_unset=True).items():
            setattr(task, key, value)
        return jsonify({'message':'Task updated'}), 200
    except ValidationError as e:
        return jsonify({'Error': str(e)}), 400

@tasks.route('/<int:task_id>', methods=['DELETE'])
@token_check
def delete_task(task_id):
    s = g.db
    task = s.query(Task).filter_by(id=task_id, user_id= g.user_id).first()
    if not task:
        raise APIError('Task not found', status_code=404)
    s.delete(task)
    return jsonify({'message':'Task deleted'}), 200