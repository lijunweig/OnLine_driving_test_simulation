import os
from flask_migrate import Migrate, MigrateCommand
from flask.ext.script import Manager, Shell
from app import create_app, db
from app.models import User, Permission, \
    Question_type, Role, Answer_paper, Question
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)
manager = Manager(app)
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Permission=Permission, Question_type=Question_type,
                Role=Role, Answer_paper=Answer_paper, Question=Question)


@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    #manager.run()
    app.run()