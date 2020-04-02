import time
import serial
import threading
import sys
import queue


class serialClient:
    
    def __init__(self, app, port, baudrate=9600, parity=serial.PARITY_EVEN, 
                stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1):
        self.app = app
        self.dataready = False
        self.data = None
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            parity=parity,
            stopbits=stopbits,
            bytesize=bytesize,
            timeout=timeout
        )
        self.app.logger.info(f'Attempting open to port {port}')
        try:
            if self.ser.isOpen():
                self.ser.close()
            
            self.ser.open()
            
            self.thread = threading.Thread(target=self.read_from_port, args=())
            self.thread.daemon = True
            self.thread.start()
        except:
            return

    def dataReady(self):
        return self.dataready
        
    def get(self):
        self.dataready = False
        return self.data
        
    def send_data(self, data):
        self.app.logger.info (f'sending {data}')
        return (self.ser.write(str.encode(data+"\r\n")))

    def close(self):
        print ("Closing serial port")
        self.ser.close()
        self.thread.stop()

    def handle_data (self, data):
        print (data, flush=True)
        self.data = data
        self.dataready = True
        
    def read_from_port(self):
        #self.app.logger.info(f"Reading serial from port")
        while True:
            reading = self.ser.readline().decode()
            if (len(reading) > 1):
                self.handle_data(reading)
            else:
                time.sleep(0.1)
        
