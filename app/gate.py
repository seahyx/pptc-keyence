from threading import Thread
import time

import wiringpi

# Wiring pi setup
wiringpi.wiringPiSetup()

wiringpi.pinMode(4, 1)


# Creates a singleton class to manage remote control operations
class GateManager:
	__instance = None
	@staticmethod 
	def getInstance():
		if GateManager.__instance == None:
			GateManager()
			return GateManager.__instance
	def __init__(self):
		if GateManager.__instance != None:
			raise Exception("This class is a singleton!")
		else:
			GateManager.__instance = self
	# End of singleton class constructor
	
	# Variables to prevent multiple signals to the remote control
	gate_time_to_free = 0
	
	def gate_time_left_to_free(self):
		return round((self.gate_time_to_free - time.time()), 3)
	
	def gate_free(self):
		return self.gate_time_left_to_free() < 0

	def set_gate_busy(self, duration):
		self.gate_time_to_free = time.time() + duration

	# Gate opening manager
	def open_gate(self, args):
		if args == 2:
			thread = Thread(target=self.open_once)
			thread.start()
		elif args == 3:
			thread = Thread(target=self.open_slightly, args=(6,))
			thread.start()
		elif args == 4:
			thread = Thread(target=self.open_and_hold, args=(6,10,))
			thread.start()

	# Gate opening mechanism
	def open_once(self):
		self.trigger_gate()
	
	def open_slightly(self, open_duration):
		self.trigger_gate()
		self.set_gate_busy(open_duration)
		time.sleep(open_duration)
		self.trigger_gate()

	def open_and_hold(self, open_duration, hold_duration):
		self.open_slightly(open_duration)
		self.set_gate_busy(hold_duration)
		time.sleep(hold_duration)
		self.trigger_gate()

	def trigger_gate(self):
		wiringpi.digitalWrite(4, 1)
		print('Trigger down')
		self.set_gate_busy(1.2)
		time.sleep(1.0)
		wiringpi.digitalWrite(4, 0)
		print('Trigger up')
