from flask.ext.script import Manager, Server
from main import app

# used to initialize Flask Script
manager = Manager(app)

# server is the same as a normal development server, so teh make_shell_conext creates a shell that can be run within the context of the app
manager.add_command("server", Server())

@manager.shell
def make_shell_conext():
    return dict(app=app)

if __name__ == "__main__":
    manager.run()
