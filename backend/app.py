def create_app():

    from initialize_app.create_app import CreateAPP, SQLALCHEMY_DB
    from initialize_app.register_bluprints import register_blueprints
    from tools.register_tools import register_all_tools

    app = CreateAPP.get_instance().initialize_flask_app()

    # Import routes to register them with the app
    register_blueprints(app=app)
    register_all_tools(app=app)
    
    # Create database tables within app context
    with app.app_context():
        SQLALCHEMY_DB.create_all()
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run()