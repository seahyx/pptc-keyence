from configparser import ConfigParser
import csv


class ConfigFile():
	''' Config settings
	
	Reads from config files which paths are provided in main.cfg
	'''

	def __init__(self, filename):
		
		# Load configuration files
		config = ConfigParser()
		config.read(filename)

		# Vision System TCP Server
		self.VISION_TCP_ADDR    = config.get('VISION SYSTEM', 'TCP Addr', fallback='localhost')
		self.VISION_TCP_PORT    = config.getint('VISION SYSTEM', 'TCP Port', fallback=8500)

		# Barcode Reader Serial port
		self.BARCODE_PORT       = config.get('BARCODE READER', 'Port')
		self.BARCODE_BAUDRATE   = config.getint('BARCODE READER', 'Baudrate')
		self.BARCODE_PARITY     = config.get('BARCODE READER', 'Parity')
		self.BARCODE_BYTESIZE   = config.getint('BARCODE READER', 'Bytesize')
		self.BARCODE_STOPBITS   = config.getint('BARCODE READER', 'Stopbits')

		# PLC Serial port
		self.PLC_PORT           = config.get('PLC', 'Port')
		self.PLC_BAUDRATE       = config.getint('PLC', 'Baudrate')
		self.PLC_PARITY         = config.get('PLC', 'Parity')
		self.PLC_BYTESIZE       = config.getint('PLC', 'Bytesize')
		self.PLC_STOPBITS       = config.getint('PLC', 'Stopbits')

		# Cartridge Assembly QC and Laser Etch QC config files
		cartridgeAssemblyQCFile = config.get('FILES', 'Cartridge Assembly QC File')
		laserEtchQCFile         = config.get('FILES', 'Laser Etch QC File')
		
		self.laserEtchQCConfig = ConfigParser()
		self.laserEtchQCConfig.read(laserEtchQCFile)

		self.cartridgeAssemblyQCConfig = ConfigParser()
		self.cartridgeAssemblyQCConfig.read(cartridgeAssemblyQCFile)

		self.laserEtchQC = []
		self.laserEtchQC = {'Prefix': self.laserEtchQCConfig.get('PREFIX', 'Allowed Prefixes').split(';')}
		self.laserEtchQC['Instrument'] = self.laserEtchQCConfig.get('LASER INSTRUMENT', 'Instrument').split(';')
		print(self.laserEtchQC)

		self.cartridgeAssemblyQC = []
		self.cartridgeAssemblyQC = {'Prefix': self.cartridgeAssemblyQCConfig.get('PREFIX', 'Allowed Prefixes').split(';')}
		print(self.cartridgeAssemblyQC)