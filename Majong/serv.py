from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import TileDetector
import io
from PIL import Image

HOST = '192.168.1.5'
PORT = 8080
FILE_PREFIX = '.'
class JSONRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes('Hi', 'utf-8'))

    def do_POST(self):
        self.send_response(200)
        #self.data_string = self.rfile.read(int(self.headers['Content-Length']))
        self.end_headers()

        data = self.rfile.read(int(self.headers['Content-Length']))

        f = open('TestImage.jpg', 'wb')
        f.write(data)
        f.close()
        tile = CardDetector.start(f.name)
        for i in range(len(tile)):
            self.wfile.write(bytes(tile[i] + ',', 'utf-8'))
        self.wfile.write(bytes('&', 'utf-8'))
        img = Image.open('found.jpg')
        imgByteArr = io.BytesIO()
        img.save(imgByteArr, format = 'JPEG')
        imgByteArr = imgByteArr.getvalue()
        self.wfile.write(imgByteArr)

print('Starting server')
server = HTTPServer((HOST,PORT), JSONRequestHandler)
server.serve_forever()
