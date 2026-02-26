import traceback
import sys

try:
    from app.api.v1.api import api_router
    print("SUCCESS: api_router imported")
except Exception as e:
    print("FAILED:")
    traceback.print_exc()
    sys.exit(1)
