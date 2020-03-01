import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import ast

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

#@app.after_request
#def after_request(response):
#    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
#    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE,OPTIONS')
#    return response

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
# get_drinks public endpoint, it will return the list of drinks in drink.short() format.

    try:
        drinks = Drink.query.all()
    except:
        # processing error.
        abort(422)
    formatted_drinks = []
    for d in drinks:
       formatted_drinks.append(d.short())

    return jsonify({'success': True,
		    'drinks': formatted_drinks})  
   
'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
# get_drinks_detail endpoint, it will return the list of drinks in drink.long() format.
    try:
        drinks = Drink.query.all()
    except:
        # processing error.
        abort(422)
    formatted_drinks = []
    for d in drinks:
        formatted_drinks.append(d.long())
    return jsonify({'success': True,
		'drinks': formatted_drinks})

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
# post drinks endpoint, it will return an array containing the only drink posted in drink.long() format.
    body = request.get_json()

    #print(body)
    if not body:
        # bad request
        abort(400)
    title = body.get('title')
    if not title:
        # bad request
        abort(400)
    recipe = json.dumps(body.get('recipe', []))
    # correct the scenario when the input is just a dict not array of dict
    eval_type = ast.literal_eval(recipe)
    if isinstance(eval_type, dict):
        recipe = [eval_type]
        recipe = json.dumps(recipe)
    try:
        d = Drink(title=title, recipe=recipe)
        d.insert()
    except:
        # processing error.
        abort(422)
    d = Drink.query.filter(Drink.title == title).one_or_none()
    return jsonify({'success': True,
                'drinks': [d.long()]})

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload, drink_id):
# patch drink endpoint, it will return an array containing the only drink in drink.long() data format.

    body = request.get_json()
    if not body:
        abort(400)

    #print(f'Patch: {body}')
    recipe = json.dumps(body.get('recipe', []))
    try:
        d = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if d:
            d.recipe = recipe
            d.update()
        else:
            # drink id not found in database.
            abort(404)
    except:
        # processing error.
        abort(422)
    
    d = Drink.query.filter(Drink.id == drink_id).one_or_none()
    #print(d.long())
    return jsonify({'success': True,
                'drinks': [d.long()]})

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, drink_id):
# delete drinks endpoint, it deletes the specific drink and return the id of it. 

    try:
        d = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if d:
            d.delete()
        else:
            # the input drink id not found in the database.
            abort(404)
    except:
        # processing error.
        abort(422)
    return jsonify({'success': True,
            'delete': drink_id})

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(400)
def resource_not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 400,
                    "message": "bad request"
                    }), 400

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
                    "success": False,
                    "error": error.status_code,
                    "message": error.error['description']
                    }), error.status_code