from app.views import app
import os
import sys
from dotenv import load_dotenv


available_commands = ("runserver",)

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in available_commands:
        print(
            "\nWrong command, please use a rightful command following this",
            " typo:\tpython manage.py <COMMAND>\n\nList of available",
            "commands :\n" + "\n".join(available_commands),
        )
    else:
        load_dotenv()
        # Launch app
        debug = os.environ.get("FLASK_ENV", "production") == "development"
        port = int(os.environ.get("PORT", 5000))
        app.secret_key = os.urandom(12)
        app.run(host='0.0.0.0', port=port, debug=debug)
