"""
Headless tester for `player_stats.show()` — stub Streamlit and run show().
Run from project root with the virtualenv Python.
"""
import sys
from pathlib import Path
import types

# Ensure project root on path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Minimal streamlit stub
class DummyCM:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False
    def __call__(self, *a, **k):
        return None
    def __getattr__(self, name):
        return lambda *a, **k: None

import types
stub = types.ModuleType("streamlit")

def _noop(*a, **k):
    print("[st]", a, k)
    return None

stub.markdown = _noop
stub.form = lambda *a, **k: DummyCM()
stub.form_submit_button = lambda *a, **k: False
stub.text_input = lambda *a, **k: ""
stub.selectbox = lambda *a, **k: (a[1] if len(a) > 1 else None)
stub.radio = lambda *a, **k: (a[1] if len(a) > 1 else None)
stub.tabs = lambda labels: [DummyCM() for _ in labels]
stub.number_input = lambda *a, **k: 0
stub.button = lambda *a, **k: False
stub.dataframe = lambda *a, **k: print("[st] dataframe called")
stub.metric = lambda *a, **k: print("[st] metric", a)
stub.info = lambda *a, **k: print("[st] info", a)
stub.success = lambda *a, **k: print("[st] success", a)
stub.warning = lambda *a, **k: print("[st] warning", a)
stub.columns = lambda n: tuple(DummyCM() for _ in range(n))
stub.download_button = lambda *a, **k: print("[st] download_button")
stub.rerun = lambda *a, **k: None

sys.modules['streamlit'] = stub

# Import and run player_stats.show()
try:
    from Cricbuzz.pages import player_stats
    print("Imported player_stats")
    if hasattr(player_stats, 'show'):
        print("Calling player_stats.show()")
        try:
            player_stats.show()
            print("player_stats.show() executed successfully")
        except Exception as e:
            print("player_stats.show() raised:", repr(e))
    else:
        print("player_stats has no show()")
except Exception as exc:
    print("Import or execution failed:", repr(exc))
    import traceback
    traceback.print_exc()

print("Headless player_stats run complete")
