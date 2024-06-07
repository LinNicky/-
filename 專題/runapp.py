import os
from test import app
import flask_excel
from flask import Flask,send_file,make_response

if __name__ == '__main__':
    app.debug = True
    host = os.environ.get('IP', '0.0.0.0')
    port = int(os.environ.get('PORT', 8080))
    app.run(host=host, port=port)

server=Flask(__name__)
if __name__=='__main__':
    flask_excel.init_excel(server)
    server.run(host='0.0.0.0',post=1234,debug=True,threaded=True)