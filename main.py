from app import create_app
from flask_migrate import MigrateCommand, Manager


app = create_app('develop')

print(app.url_map)
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=80, reloader=True)
