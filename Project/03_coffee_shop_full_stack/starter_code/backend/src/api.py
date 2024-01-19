import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES


@app.route('/drinks')
def drinks():
    """
    returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
        or appropriate status code indicating reason for failure
    """
    try:
        drinks = [drink.short() for drink in Drink.query.all()]
        return jsonify({'success': True,
                        'drinks': drinks})
    except BaseException:
        abort(422)


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def drinks_details():
    """
    returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
        or appropriate status code indicating reason for failure

    it should require the 'get:drinks-detail' permission
    """
    try:
        drinks = [drink.long() for drink in Drink.query.all()]
        return jsonify({'success': True,
                        'drinks': drinks})
    except BaseException:
        abort(422)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_new_drink():
    """
    returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure

    it should create a new row in the drinks table
    it should require the 'post:drinks' permission
    it should contain the drink.long() data representation
    """
    try:
        body = request.get_json()
        title = body.get("title", None)
        recipe = body.get("recipe", None)
        new_drink = Drink(title=title, recipe=json.dumps(recipe))
        new_drink.insert()
        return jsonify({'success': True,
                        'drinks': new_drink.long()})
    except BaseException:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(drink_id):
    """
    returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure

    Keyword arguments:
    drink_id -- the existing drink id

    it should respond with a 404 error if <id> is not found
    it should update the corresponding row for <id>
    it should require the 'patch:drinks' permission
    it should contain the drink.long() data representation
    """
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if(drink is None):
            abort(404)
        body = request.get_json()
        title = body.get("title", None)
        recipe = body.get("recipe", None)
        if(title is not None):
            drink.title = title
        if(recipe is not None):
            drink.recipe = json.dumps(recipe)
        drink.update()

        return jsonify({'success': True,
                        'drinks': [drink.long()]})
    except BaseException:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(drink_id):
    """
    returns status code 200 and json {"success": True, "delete": id}
        where id is the id of the deleted record
        or appropriate status code indicating reason for failure

    Keyword arguments:
    drink_id -- the existing drink id

    it should respond with a 404 error if <id> is not found
    it should delete the corresponding row for <id>
    it should require the 'delete:drinks' permission
    """
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if(drink is None):
            abort(404)
        
        drink.delete()

        return jsonify({'success': True,
                        'delete': drink_id})
    except BaseException:
        abort(422)

# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(AuthError)
def handle_auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), error.status_code
