from configparser import ConfigParser
import csv


class ConfigFile():
	''' Config settings

	Reads from config files which paths are provided in main.cfg
	'''

	def __init__(self, app, filename):

		self.app = app

		app.logger.info('Loading configuration files...')

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
		self.laserEtchQC['WOLength'] = self.laserEtchQCConfig.getint('WORK ORDER', 'Length')
		self.laserEtchQC['PNLength'] = self.laserEtchQCConfig.getint('PART NUMBER', 'Length')
		self.laserEtchQC['PNFile'] = self.laserEtchQCConfig.get('PATH', 'PN Data Lookup')

		app.logger.info(f'Loading Laser Etch QC config: {self.laserEtchQC}')

		self.cartridgeAssemblyQC = []
		self.cartridgeAssemblyQC = {'Prefix': self.cartridgeAssemblyQCConfig.get('PREFIX', 'Allowed Prefixes').split(';')}

		app.logger.info(f'Loading Cartridge Assembly QC config: {self.cartridgeAssemblyQC}')

		# Image files
		self.imageDir = config.get('FILES', 'Display Images Dir')

		# Image filenames
		self.cam1Normal  = config.get('CAM1', 'Normal Image')
		self.cam1Left    = config.get('CAM1', 'Left Image')
		self.cam1Right   = config.get('CAM1', 'Right Image')
		self.cam1Lower   = config.get('CAM1', 'Lower Image')
		self.cam1Upper   = config.get('CAM1', 'Upper Image')
		self.cam1Shape   = config.get('CAM1', 'Shape Image')
		self.cam1Texture = config.get('CAM1', 'Texture Image')

		self.cam2Normal  = config.get('CAM2', 'Normal Image')
		self.cam2Left    = config.get('CAM2', 'Left Image')
		self.cam2Right   = config.get('CAM2', 'Right Image')
		self.cam2Lower   = config.get('CAM2', 'Lower Image')
		self.cam2Upper   = config.get('CAM2', 'Upper Image')
		self.cam2Shape   = config.get('CAM2', 'Shape Image')
		self.cam2Texture = config.get('CAM2', 'Texture Image')