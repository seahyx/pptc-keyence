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

		# Audit trail path
		self.AUDIT_TRAIL_DIR = config.get('FILES', 'Audit Trail Dir')


		# Cartridge Assembly QC and Laser Etch QC config files
		cartridge_assembly_QC_file = config.get('FILES', 'Cartridge Assembly QC File')
		laser_etch_QC_file         = config.get('FILES', 'Laser Etch QC File')

		self.laser_etch_QC_config = ConfigParser()
		self.laser_etch_QC_config.read(laser_etch_QC_file)

		self.cartridge_assembly_QC_config = ConfigParser()
		self.cartridge_assembly_QC_config.read(cartridge_assembly_QC_file)

		self.laser_etch_QC 					= []
		self.laser_etch_QC 					= {'Prefix': self.laser_etch_QC_config.get('PREFIX', 'Allowed Prefixes').split(';')}
		self.laser_etch_QC['Instrument'] 	= self.laser_etch_QC_config.get('LASER INSTRUMENT', 'Instrument').split(';')
		self.laser_etch_QC['WOLength'] 		= self.laser_etch_QC_config.getint('WORK ORDER', 'Length')
		self.laser_etch_QC['PNLength'] 		= self.laser_etch_QC_config.getint('PART NUMBER', 'Length')
		self.laser_etch_QC['PNFile'] 		= self.laser_etch_QC_config.get('PATH', 'PN Data Lookup')
		self.laser_etch_QC['LogFile'] 		= self.laser_etch_QC_config.get('PATH', 'Log File')
		self.laser_etch_QC['ImageDir'] 		= self.laser_etch_QC_config.get('PATH', 'Image Dir')

		# app.logger.info(f'Loading Laser Etch QC config: {self.laser_etch_QC}')

		self.cartridge_assembly_QC = []
		self.cartridge_assembly_QC = {'Prefix': self.cartridge_assembly_QC_config.get('PREFIX', 'Allowed Prefixes').split(';')}
		self.cartridge_assembly_QC['LogFile'] 		= self.cartridge_assembly_QC_config.get('PATH', 'Log File')
		self.cartridge_assembly_QC['ImageDir'] 		= self.cartridge_assembly_QC_config.get('PATH', 'Image Dir')
		self.cartridge_assembly_QC['Max Retry'] 		= self.cartridge_assembly_QC_config.getint('GENERAL', 'Max Retry')

		# app.logger.info(f'Loading Cartridge Assembly QC config: {self.cartridge_assembly_QC}')

		# Image files
		self.VISION_IMAGE_DIR = config.get('FILES', 'Vision Image Dir')

		# Image filenames
		self.VISION_IMAGE = {
			'CAM1': {
				'NORMAL'  : config.get('CAM1', 'Normal Image'),
				'LEFT'    : config.get('CAM1', 'Left Image'),
				'RIGHT'   : config.get('CAM1', 'Right Image'),
				'LOWER'   : config.get('CAM1', 'Lower Image'),
				'UPPER'   : config.get('CAM1', 'Upper Image'),
				'SHAPE'   : config.get('CAM1', 'Shape Image'),
				'TEXTURE' : config.get('CAM1', 'Texture Image')
			},
			'CAM2': {
				'NORMAL'  : config.get('CAM2', 'Normal Image'),
				'LEFT'    : config.get('CAM2', 'Left Image'),
				'RIGHT'   : config.get('CAM2', 'Right Image'),
				'LOWER'   : config.get('CAM2', 'Lower Image'),
				'UPPER'   : config.get('CAM2', 'Upper Image'),
				'SHAPE'   : config.get('CAM2', 'Shape Image'),
				'TEXTURE' : config.get('CAM2', 'Texture Image')
			}
		}
