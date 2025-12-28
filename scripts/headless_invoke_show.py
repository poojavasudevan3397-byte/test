"""
Headless tester: stub Streamlit and call a page `show()` for dry-run verification.
Run from project root with the virtualenv Python.
"""
import sys
import types
from pathlib import Path

# Ensure project root on path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Create a minimal stub module for streamlit
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

# UI functions used by pages - implement minimal behavior
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

# Insert into sys.modules so `import streamlit` yields our stub
sys.modules['streamlit'] = stub

# Now import and call the page
try:
    from Cricbuzz.pages import crud_operations
    print("Imported crud_operations")
    if hasattr(crud_operations, 'show'):
        print("Calling crud_operations.show()")
        try:
            crud_operations.show()
            print("show() executed successfully")
        except Exception as e:
            print("show() raised:", repr(e))
    else:
        print("crud_operations has no show()")
except Exception as exc:
    print("Import or execution failed:", repr(exc))
    import traceback
    traceback.print_exc()

print("Headless run complete")
