from flask.ext.script import Manager, Server
from flask.ext.migrate import Migrate, MigrateCommand

from main import app, db, User, Record

migrate = Migrate(app, db)

# used to initialize Flask Script
manager = Manager(app)

# server is the same as a normal development server, so teh make_shell_conext creates a shell that can be run within the context of the app
manager.add_command("server", Server())
manager.add_command('db', MigrateCommand)

@manager.shell
def make_shell_conext():
    return dict(app=app, db=db, User=User, Record=Record)

if __name__ == "__main__":
    manager.run()
