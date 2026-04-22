from flask import Flask

def create_app():
    app = Flask(__name__)

    @app.route('/health')
    def health_check():
        return {"ok": True}
    
    return app