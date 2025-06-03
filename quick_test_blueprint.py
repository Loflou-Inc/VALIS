from flask import Blueprint

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/memory/<persona_id>')
def get_memory_data(persona_id):
    # Memory API implementation
    pass

# Register blueprint BEFORE catch-all
app.register_blueprint(api)
