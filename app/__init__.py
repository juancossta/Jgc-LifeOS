import os
from flask import Flask, render_template
from app.config import config_by_name
from app.extensions import db, migrate, login_manager, csrf


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_by_name[config_name])

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.dashboard.routes import dashboard_bp
    from app.blueprints.fe.routes import fe_bp
    from app.blueprints.projetos.routes import projetos_bp
    from app.blueprints.financeiro.routes import financeiro_bp
    from app.blueprints.estudos.routes import estudos_bp
    from app.blueprints.metas.routes import metas_bp
    from app.blueprints.saude.routes import saude_bp
    from app.blueprints.humor.routes import humor_bp
    from app.blueprints.pureza.routes import pureza_bp
    from app.blueprints.jogos.routes import jogos_bp
    from app.blueprints.historico.routes import historico_bp
    from app.blueprints.perfil.routes import perfil_bp
    from app.blueprints.cron.routes import cron_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(fe_bp, url_prefix="/fe")
    app.register_blueprint(projetos_bp, url_prefix="/projetos")
    app.register_blueprint(financeiro_bp, url_prefix="/financeiro")
    app.register_blueprint(estudos_bp, url_prefix="/estudos")
    app.register_blueprint(metas_bp, url_prefix="/metas")
    app.register_blueprint(saude_bp, url_prefix="/saude")
    app.register_blueprint(humor_bp, url_prefix="/humor")
    app.register_blueprint(pureza_bp, url_prefix="/pureza")
    app.register_blueprint(jogos_bp, url_prefix="/jogos")
    app.register_blueprint(historico_bp, url_prefix="/historico")
    app.register_blueprint(perfil_bp, url_prefix="/perfil")
    app.register_blueprint(cron_bp)

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    @app.context_processor
    def inject_globals():
        from datetime import date
        return {"hoje": date.today()}

    return app
