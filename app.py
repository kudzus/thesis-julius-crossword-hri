from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from threading import Event
import socket
import logging
import os

# -------- shared "snapshot is fresh" flag --------------------------
state_ready = Event()          # main.py will import this

# ---------- crossword‐state holder ---------------------------------
class GameStateCrossword:
    def __init__(self):
        self.across = {}
        self.down = {}
        self.current_cell = {'row': None, 'col': None, 'dir': None}
        self.clue_context = {'direction': None, 'clueLabel': None}

    def update_grid(self, across, down):
        self.across, self.down = across, down

    def update_cell(self, row, col, dir):
        self.current_cell = {'row': row, 'col': col, 'dir': dir}

    def update_clue_context(self, direction, clueLabel):
        self.clue_context = {'direction': direction, 'clueLabel': clueLabel}

    def serialize(self):
        return {
            'across': self.across,
            'down': self.down,
            'current_cell': self.current_cell,
            'clue_context': self.clue_context,
        }

# -------------------------------------------------------------------
game_state = GameStateCrossword()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# -------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("crossword_a.html")

@app.route("/game-state")
def get_game_state():
    return jsonify(game_state.serialize())

# -------- receive full snapshot ------------------------------------
@socketio.on("game_state")
def handle_game_state(data):
    # update the in‐memory model
    game_state.update_grid(data['across'], data['down'])
    cc = data['current_cell']
    game_state.update_cell(cc['row'], cc['col'], cc['dir'])
    clue = data['clue_context']
    game_state.update_clue_context(clue['direction'], clue['clueLabel'])

    # tell main.py a fresh snapshot is ready
    state_ready.set()

# -------------------------------------------------------------------
def _find_free_port(start: int = 5006, end: int = 5100) -> int:
    """
    Pick an available port between `start` and `end`. If none found, raises OSError.
    """
    for port in range(start, end + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("0.0.0.0", port))
            sock.close()
            return port
        except OSError:
            sock.close()
            continue
    raise OSError(f"No free port in range {start}-{end}")

# Choose one at import time
try:
    SERVER_PORT = _find_free_port(5006, 5100)
except OSError:
    # Fallback if 5006–5100 are all busy; let the OS pick a random ephemeral port
    tmp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tmp.bind(("0.0.0.0", 0))
    SERVER_PORT = tmp.getsockname()[1]
    tmp.close()

def get_server_links() -> list[str]:
    """
    Return the two URLs clients can use to connect:
      - localhost (127.0.0.1)
      - LAN IP
    """
    # Find local LAN IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        lan_ip = s.getsockname()[0]
    except Exception:
        lan_ip = "127.0.0.1"
    finally:
        s.close()

    return [
        f"http://127.0.0.1:{SERVER_PORT}",
        f"http://{lan_ip}:{SERVER_PORT}"
    ]

def run():
    # Disable Flask's “Running on …” banner by setting this environment var:
    os_environ = dict(os.environ)
    os_environ["FLASK_RUN_FROM_CLI"] = "false"
    # Silence Flask‐werkzeug's logger entirely
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    # Run Socket.IO on the chosen port
    socketio.run(app,
                 host="0.0.0.0",
                 port=SERVER_PORT,
                 debug=False,
                 use_reloader=False)  # disable reloader to avoid duplicate threads

if __name__ == "__main__":
    run()
    get_server_links()
