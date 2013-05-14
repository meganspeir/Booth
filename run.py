#!flask/bin/python
from capture import app
from config import HOST, PORT

app.run(HOST, PORT)
