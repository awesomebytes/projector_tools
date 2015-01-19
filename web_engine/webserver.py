#!/usr/bin/python
# Example from http://www.acmesystems.it/python_httpserver
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import urlparse
import cgi
import time
import subprocess

# import liblo
# import dac
# from ILDA import readFrames, readFirstFrame

PORT_NUMBER = 8080

USE_DAC = True


#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):

    def __init__(self, *args):
        print "Initializing my handler"
        BaseHTTPRequestHandler.__init__(self, *args)


    def address_string(self):
        # http://stackoverflow.com/questions/2617615/slow-python-http-server-on-localhost
        # workaround for slow network access (phone)
        host, port = self.client_address[:2]
        #return socket.getfqdn(host) # default, slow, behaviour
        return host


    def get_form_value(self, form, fieldname):
        """Get the form value and return 0 if not filled"""
        retval = None
        if form[fieldname].value == '':
            retval = 0
        else:
            retval = int(form[fieldname].value)
        return retval

    def do_POST(self):
        print "Got a POST"
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })
        filename = form['file'].filename
        if form['x_coord'].value == '':
            x_coord = 0.0
        else:
            x_coord = float(form['x_coord'].value) # FieldStorage('x_coord', None, '10')

        if form['y_coord'].value == '':
            y_coord = 0.0
        else:
            y_coord = float(form['y_coord'].value)

        print "\n\n   Offset coords: x_coord: " + str(x_coord) + " y_coord: " + str(y_coord)

        contourn_r = self.get_form_value(form, "r_color")
        contourn_g = self.get_form_value(form, "g_color")
        contourn_b = self.get_form_value(form, "b_color")

        print "\n\n rgb colors: " + str(contourn_r) + ", " + str(contourn_g) + ", " + str(contourn_b)

        background_color = self.get_form_value(form, "bg_color")

        print "\n\n background color: " + str(background_color)

        kernel_size = self.get_form_value(form, "kernel_size")

        print "\n\n kernel size: " + str(kernel_size)

        time_proj = self.get_form_value(form, "time_proj")

        print "\n\n projection time: " + str(time_proj) + " (s)"

        data = form['file'].file.read()
        print "Saving at: " + curdir + sep + 'uploaded/' + filename
        open(curdir + sep + 'uploaded/' + filename, "wb").write(data)
        self.file_to_stream = curdir + sep + 'uploaded/' + filename

        uploaded_sentence = ""  # Sentence must be empty!! (or js does not work correctly)#"uploaded %s, thanks"%filename
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", len(uploaded_sentence))
        self.end_headers()
        #self.wfile.write(uploaded_sentence) 

        # HERE DO THE CALL TO THE PYTHON FILE WITH ALL THE PARAMETERS
        commandline = ["python", curdir + sep + "projection_script.py", 
            self.file_to_stream,
            str(x_coord), str(y_coord),
            str(contourn_r), str(contourn_g), str(contourn_b),
            str(background_color),
            str(kernel_size),
            str(time_proj)]
        print "Commandline will be:"
        print commandline
        # subprocess.Popen(["python", curdir + sep + "projection_script.py", 
        #    self.file_to_stream,
        #    str(x_coord), str(y_coord),
        #    str(contourn_r), str(contourn_g), str(contourn_b),
        #    str(background_color),
        #    str(kernel_size),
        #    str(time_proj)])


        # OOLD CODE
        # If the file has extension dxf, do translation and convert it
        # if filename.endswith('.dxf') or filename.endswith('.DXF') :
        #     original_filename = curdir + sep + 'uploaded/' + filename
        # if filename.endswith('.DXF'):
        #     ilda_filename = curdir + sep + 'uploaded/' + filename.replace('.DXF', '.ild')
        # elif filename.endswith('.dxf'):
        #     ilda_filename = curdir + sep + 'uploaded/' + filename.replace('.dxf', '.ild')
            
        #     print "Transforming from dxf to ILDA... with fixed parameters 3m 3m (height, side)"
        #     dxf_to_ilda_process = subprocess.Popen([curdir + sep + "LaserBoy_dxf_to_ilda_tool", 
        #                                             original_filename, ilda_filename, 
        #                                             "3", "3", 
        #                                             "20",
        #                                              str(x_coord), str(y_coord)])
        #     dxf_to_ilda_process.wait()
        #     self.file_to_stream = ilda_filename
        # elif filename.endswith('.ilda') or filename.endswith('.ild') or filename.endswith('.ILDA') or filename.endswith('.ILD'):
        #     self.file_to_stream = curdir + sep + 'uploaded/' + filename
        # else:
        #     print "Error, not a file to stream, doing nothing"
        #     return
        # # Execute the script that plays one file
        # if USE_DAC:
        #     print "Streaming file"
        #     subprocess.Popen(["python", curdir + sep + "reproduce_one_frame_ilda.py", self.file_to_stream])
        # else:
        #     print "On debug mode, not streaming file"
    
    #Handler for the GET requests
    def do_GET(self):
        print "Path: " + str(self.path)
        sendReply = False
 
        if self.path=="/":
            mimetype='text/html'
            self.path="/index.html"
            sendReply = True
        if self.path.endswith(".jpg"):
            mimetype='image/jpg'
            sendReply = True
        if self.path.endswith(".png"):
            mimetype='image/png'
            sendReply = True
        if self.path.endswith(".gif"):
            mimetype='image/gif'
            sendReply = True
        if self.path.endswith(".js"):
            mimetype='application/javascript'
            sendReply = True
        if self.path.endswith(".css"):
            mimetype='text/css'
            sendReply = True


        # if  self.path.endswith("stop"):
        #     self.send_response(200)
        #     mimetype='text/html'
        #     self.send_header('Content-type',mimetype)
        #     self.end_headers()
        #     # if USE_DAC:
        #     #     self.dac_obj.stop()
        #     self.wfile.write("Stopped laser projection")
        #     return

        if sendReply == True:
            #Open the static file requested and send it
            print "  Opening: " + str(curdir + sep + self.path)
            f = open(curdir + sep + self.path) 
            print "Sending response 200"
            self.send_response(200)
            print "Sending headers"
            self.send_header('Content-type',mimetype)
            print "Sending end headers"
            self.end_headers()
            print "writting file"
            self.wfile.write(f.read())
            print "Closing"
            f.close()
            print "  Sent file."


        return


# Optinally delete all old dxf ilda and ild files:
#subprocess.Popen(["rm *.dxf *.ilda *.ild"])


def HTTP_handler_with_DAC(*args):
    myHandler(*args)

try:
    #Create a web server and define the handler to manage the
    #incoming request
    server = HTTPServer(('', PORT_NUMBER), HTTP_handler_with_DAC)
    print 'Started httpserver on port ' , PORT_NUMBER
    
    #Wait forever for incoming http requests
    server.serve_forever()

except KeyboardInterrupt:
    print '^C received, shutting down the web server'
    server.socket.close()