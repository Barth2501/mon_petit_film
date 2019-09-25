from server import app
import os
import sys

available_commands = 'runserver'

if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] != 'runserver':
        print('\nWrong command, please use a rightful command following this typo :\tpython manage.py <COMMAND>\n\nList of available commands :\n' + available_commands)
    else:
        # Development mode - TO BE REMOVED
        app.env = 'development'
        # Bind to PORT if defined, otherwise default to 5000.
        port = int(os.environ.get('PORT', 5000))
        app.run(host='localhost', port=port, debug=True)
