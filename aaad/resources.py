from flask import Flask, jsonify
from flask_restful import reqparse, Resource, abort
from flask_login import login_required
from webargs import fields
from webargs.flaskparser import use_args

from authorizers import FileAuthorizer
from quotas import Quotas
from validators import Validator

class Users(Resource):
    get_args = {
        'startswith': fields.Str(required=False)
    }
    @use_args(get_args)
    def get(self, args):
        file_authorizer = FileAuthorizer().instance
        users = file_authorizer.get_user_list('user')
        startswith = args.get('startswith')
        if not startswith:
            return jsonify(users)
        filtered_users = []
        for user in users:
            if user.startswith(startswith):
                filtered_users.append(user)
        return jsonify(filtered_users)

class Groups(Resource):
    def get(self):
        file_authorizer = FileAuthorizer().instance
        groups = file_authorizer.get_user_list('group')
        return jsonify(groups)

class CanActAsUsers(Resource):
    get_args = {
        'contains': fields.Str(required=False)
    }
    @use_args(get_args)
    @login_required
    def get(self, args, user):
        file_authorizer = FileAuthorizer().instance
        actas_users = file_authorizer.get_canactas_list(user)
        contains = args.get('contains')
        if not contains:
            return jsonify(actas_users)
        filtered_users = []
        for actas_user in actas_users:
            if contains in actas_user:
                filtered_users.append(actas_user)
        return jsonify(filtered_users)

class QuotaBuckets(Resource):
    get_args = {
        'getAlloc': fields.Boolean(required=False)
    }
    @use_args(get_args)
    #@login_required
    def get(self, args, bucket=None):
        ret_data = None
        if bucket:
            ret_data = Quotas().instance.get_quota_for_bucket(bucket)
            if ret_data and args and args['getAlloc']:
                ret_data.update(Quotas().instance.get_task_allocation(bucket))
        else:
            ret_data = Quotas().instance.get_buckets()
            if args and args['getAlloc']:
                for item in buckets:
                    item.update(ret_data.update(Quotas().instance.get_task_allocation(bucket)))
        if not ret_data:
            abort(404)
        return jsonify(ret_data)
