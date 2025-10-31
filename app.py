from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from flask_cors import CORS


app = Flask(__name__)

DATABASE_NAME = 'tasks.db'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

db = SQLAlchemy(app)
CORS(app, supports_credentials=True, resources={r"/*" : {'origins': '*'}})

ma = Marshmallow(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    description = db.Column(db.String(200))
    completed = db.Column(db.Boolean, default = False)
    
    
class TaskSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        
task_schema = TaskSchema()
tasks_schema = TaskSchema(many = True)

# ... your other app setup and model definitions ...
# --- NEW FUNCTION TO SAFELY CREATE DB ---
def initialize_database(app):
    """Initializes the database by checking if the file exists."""
    # This path resolves to the file inside the /instance folder
    db_path = os.path.join(app.instance_path, DATABASE_NAME)
    # Only run create_all() if the file does not exist
    if not os.path.exists(db_path):
    # We need the app context to run database commands
        with app.app_context():
            # Ensure the instance directory exists before calling create_all
            # This handles creating the 'instance' folder if needed
            os.makedirs(app.instance_path, exist_ok=True)
            db.create_all()
            print("--- INFO: Database tables created for the first time! ---")
    else:
        print("--- INFO: Database already exists. Skipping table creation. ---")
    # --- EXECUTION BLOCK ---



@app.route('/api/tasks', methods=['POST'])
def create_task():
    print(request.get_json())
    data = request.get_json()
    
    title = data.get('title')
    description = data.get('description')
    completed = data.get('completed')
    if not title:
        return {'error': 'Title is required'}, 400
    new_task = Task(title=title, description=description, completed=completed)
    db.session.add(new_task)
    db.session.commit()
    return task_schema.jsonify(new_task), 201



@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return tasks_schema.jsonify(tasks)

    



@app.route('/api/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    task = Task.query.get_or_404(id)
    task.title = request.json.get('title', task.title)
    task.description = request.json.get('description', task.description)
    task.completed = request.json.get('completed', task.completed)
    db.session.commit()
    return task_schema.jsonify(task)


@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message' : 'Task deleted successfully.'})
    

if __name__ == '__main__':
    initialize_database(app)
    app.run(debug=True)

