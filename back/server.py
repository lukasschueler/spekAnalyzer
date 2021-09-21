import sys
sys.path.insert(1, '/home/lukas/hiwi/project/reactplots/back')
from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
import socketserver
import pickle
import json
import cgi
import time
import os
from tools import Tools
from encoder import NumpyEncoder


# Python server that connects frontend and backend
class Server(SimpleHTTPRequestHandler):
    
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
    def do_HEAD(self):
        self._set_headers()
        
    def do_GET(self):
        if self.path == '/':
            self.path = '/build'
        
        return SimpleHTTPRequestHandler.do_GET(self)

        # super().do_GET()
            

    # POST echoes the message adding a JSON field
    def do_POST(self):
        
        ctype, pdict = cgi.parse_header(self.headers['Content-type'])

        
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return
            
        # read the message and convert it into a python dictionary
        length = int(self.headers['Content-length'])
        message = json.loads(self.rfile.read(length))

    
    
        if self.path == "/uploadData":
            self._set_headers()
            

            startRow = message["startRow"]
            xRow = message["xRow"]
            yRow = message["yRow"]
            
            data = message["data"]
            processed = message["calibrated"]
            coefficients = message["coefficients"]
            
            
           
            x,y =  Tools.processTXTContent(self,data, startRow, xRow, yRow)
            if processed:
                x = Tools.applyCoefficients(self, x, coefficients)
            # result = Tools.wrap(self,x,y)
            
            package = {"x":x,"y":y}
            output = json.dumps(package, cls=NumpyEncoder)

            # output = json.dumps(package)
            self.wfile.write(output.encode())
            
        elif self.path == "/processReference":
            self._set_headers()
            
            data = message["data"]
            reference = message["reference"]
            
            x, transmissionY, absorptionY = Tools.returnTransAndAbsorp(self, data, reference)
            
            
            package = [x,transmissionY, absorptionY]
            
            output = json.dumps(package, cls=NumpyEncoder)
            self.wfile.write(output.encode())
        
                        
        elif self.path == "/calculateConcentration":
            self._set_headers()
            
            concentrations = message["concentrationValues"]
            absorptionValues = message["absorptionValues"]
            
            linearConcentration = Tools.calculateConcentration(self, concentrations, absorptionValues)
            
            
            package = linearConcentration
            
            output = json.dumps(package, cls=NumpyEncoder)
            self.wfile.write(output.encode())
                        
                        
        elif self.path == "/getCalibration":
            self._set_headers()
            data = message["data"]
            regressionValues = message["regressionValues"]
            
            coefficients =  Tools.getCoefficients(self, regressionValues)
            x, y = Tools.unWrap(self, data)
            newx = Tools.applyCoefficients(self, x, coefficients)
            result = Tools.wrap(self,newx,y)
            
            package = {"result": result, "coefficients": coefficients}
            output = json.dumps(package, cls=NumpyEncoder)
            self.wfile.write(output.encode())
        
        elif self.path == "/calibrate":
            self._set_headers()
            
            data = message["data"]
            coefficients = message["coefficients"]
            
            x, y = Tools.unWrap(self, data)
            newx =  Tools.applyCoefficients(self, x, coefficients)
            result = Tools.wrap(self, newx, y)
            
            package = result
            output = json.dumps(package)
            self.wfile.write(output.encode())
            
        elif self.path =="/smoothData":
            self._set_headers()
            
            data = message["data"]
            windowSize = int(message["windowSize"])
            degree = int(message["degree"])
            
            smoothedData = Tools.cleanData(self, data, windowSize, degree)
            output = json.dumps(smoothedData)
            self.wfile.write(output.encode())
            
        
        elif self.path == "/normalizeData":
            self._set_headers()
            
            data = message["data"]
            
            normalizedData = Tools.normalize(self, data)
            output = json.dumps(normalizedData)
            self.wfile.write(output.encode())


            
        elif self.path == "/nullrefData":
            self._set_headers()
            
            data = message["data"]
            reference = message["nullReference"]

            
            
            normalizedData = Tools.normalize(self,reference)
            output = json.dumps(normalizedData)
            self.wfile.write(output.encode())
            
        elif self.path == "/markMaxima":
            self._set_headers()
            
            data = message["data"]
            
            maxima = Tools.getMaxima(self, data)
            output = json.dumps(maxima)
            self.wfile.write(output.encode())

                        
            
def run(server_class=HTTPServer, handler_class=Server, port=8008):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    
    
    try:
        print (time.asctime(), "Server Starts - %s:%s" % (server_address, port))
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
        httpd.server_close()    
    print()
    print (time.asctime(), "Server Stops - %s:%s" % (server_address, port))
    
    
    
if __name__ == "__main__":
    from sys import argv
    
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
        
        
        
        
        
