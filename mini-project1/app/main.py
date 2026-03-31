"""
Todo API - Flask Application
A simple REST API for managing todo items
"""

from flask import Flask, jsonify, request
from datetime import datetime
from business_logic import TodoManager
import os


app = Flask(__name__)
todo_manager = TodoManager()

# Configuration
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False') == 'True'


@app.route('/', methods=['GET'])
def home():
    """Welcome endpoint"""
    return jsonify({
        "message": "Welcome to Todo API",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "This message",
            "GET /health": "Health check",
            "GET /api/todos": "List all todos",
            "POST /api/todos": "Create a new todo",
            "GET /api/todos/<id>": "Get a specific todo",
            "PUT /api/todos/<id>": "Update a todo",
            "DELETE /api/todos/<id>": "Delete a todo"
        }
    }), 200


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "todo-api"
    }), 200


@app.route('/api/todos', methods=['GET'])
def get_todos():
    """Get all todos"""
    try:
        todos = todo_manager.get_all_todos()
        return jsonify({
            "success": True,
            "count": len(todos),
            "data": todos
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """Get a specific todo by ID"""
    try:
        todo = todo_manager.get_todo(todo_id)
        if todo:
            return jsonify({
                "success": True,
                "data": todo
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Todo not found"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/todos', methods=['POST'])
def create_todo():
    """Create a new todo"""
    try:
        data = request.get_json(silent=True)
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        title = data.get('title')
        if not title:
            return jsonify({
                "success": False,
                "error": "Title is required"
            }), 400
        
        description = data.get('description', '')
        todo = todo_manager.create_todo(title, description)
        
        return jsonify({
            "success": True,
            "message": "Todo created successfully",
            "data": todo
        }), 201
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update a todo"""
    try:
        data = request.get_json(silent=True)
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        todo = todo_manager.update_todo(
            todo_id,
            title=data.get('title'),
            description=data.get('description'),
            completed=data.get('completed')
        )
        
        if todo:
            return jsonify({
                "success": True,
                "message": "Todo updated successfully",
                "data": todo
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Todo not found"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a todo"""
    try:
        success = todo_manager.delete_todo(todo_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Todo deleted successfully"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Todo not found"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


if __name__ == '__main__':
    # Run the application
    # In production, use a proper WSGI server like gunicorn
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
