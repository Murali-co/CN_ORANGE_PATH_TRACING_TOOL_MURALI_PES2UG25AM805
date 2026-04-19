import os
wsgi_path = os.path.expanduser("~/ryu_venv/lib/python3.10/site-packages/ryu/app/wsgi.py")
with open(wsgi_path, "r") as f:
    content = f.read()
content = content.replace("from eventlet.wsgi import ALREADY_HANDLED", "ALREADY_HANDLED = object()")
with open(wsgi_path, "w") as f:
    f.write(content)
print("Patched wsgi.py")
