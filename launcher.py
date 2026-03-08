import threading
import webview
from app import app

def run_flask():
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    webview.create_window(
        "AI PSHA ASHA",
        "http://127.0.0.1:5000",
        width=1100,
        height=750,
        resizable=True,
    )
    webview.start()