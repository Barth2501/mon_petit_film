from server import app
import os
import sys
from dotenv import load_dotenv

available_commands = ('runserver',)

if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] != 'runserver':
        print('\nWrong command, please use a rightful command following this',
              ' typo:\tpython manage.py <COMMAND>\n\nList of available',
              'commands :\n' + '\n'.join(available_commands))
    else:
        load_dotenv()
        debug = os.environ.get('FLASK_ENV', 'production') == 'development'
        # Bind to PORT if defined, otherwise default to 5000.
        port = int(os.environ.get('PORT', 5000))
        app.run(host='localhost', port=port, debug=debug)
