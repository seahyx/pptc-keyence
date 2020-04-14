const laser_tube_count = 24;
const laser_trough_count = 4;

const RackTypeEnum = {
	TUBE: 1,
	TROUGH: 2
}

class StatusBarManager {

	constructor(status_bar) {
		this.status_bar = status_bar;
		this.status_text = status_bar.querySelector('p');
	}

	set_text(text) {
		this.status_text.innerText = text;
	}

	reset() {
		this.set_text('')
		this.status_bar.classList.toggle('pass', false);
		this.status_bar.classList.toggle('error', false);
	}

	set_success(success_msg = 'SUCCESS') {
		this.reset()
		this.set_text(success_msg);
		this.status_bar.classList.toggle('pass', true);
	}

	set_fail(error_msg = 'FAIL') {
		this.reset()
		this.set_text(error_msg);
		this.status_bar.classList.toggle('error', true);
	}

	set_neutral(msg = '-') {
		this.reset()
		this.set_text(msg);
	}

}

const status_bar           = document.querySelector('#laser-status');

const btn_done             = document.querySelector('#btn-done');
const in_work_order        = document.querySelector('#laser-work-order');
const in_part_number       = document.querySelector('#laser-part-number');
const laser_rack_id        = document.querySelector('#laser-rack-id');

const laser_tube_display   = document.querySelector('#laser-tube-display');
const laser_trough_display = document.querySelector('#laser-trough-display');
const laser_tube_barcode   = document.querySelector('#laser-tube-barcode');
const laser_trough_barcode = document.querySelector('#laser-trough-barcode');

// Done button

btn_done.addEventListener('click', () => {
	let confirmation = confirm('Are you sure you want to finish?');

	if (confirmation) {
		window.location = Globals.done_url;
	}

});


// Initialization

statusBarManager = new StatusBarManager(status_bar);

load_data(Globals.data, Globals.rack_type, statusBarManager);


// SocketIO

var socketio = io.connect(`http://${document.domain}:${location.port}/laser/api`);

// Responses

socketio.on('alert', function(msg) {
	console.log(`Received alert: ${msg}`);
	alert(msg);
});

socketio.on('response', function(msg) {
	console.log(`Received data: ${msg}`);
});

socketio.on('redirect', function(url) {
	console.log(`Redirecting to ${url}`);
	window.location = url;
})



// Functions

function load_data(data, rack_type, statusBarManager) {

	// Debugging purposes
	console.log(`data: ${data},\nrack_id: ${rack_type}`);
	
	// Set status to neutral first (reset)
	statusBarManager.set_neutral();

	// Set rack type
	switch_rack_type(rack_type);

	// Load data, != checks against null and undefined
	if (data != null && rack_type != null) {

		// Set default status to success
		statusBarManager.set_success();

		if (rack_type === RackTypeEnum.TUBE) {

			// Tube display/barcode

			for (let x = 0; x < laser_tube_count; x++) {
				
				// Position of data in the data array which are in pairs of 2, excluding the first arbitrary element
				let current_data_count = 1 + (x * 2);

				// Element reference for the tube display
				let display_element = get_tube_display_item(x + 1)
				
				if (data[current_data_count] === '0') {
					
					// 0 means barcode is valid

					get_tube_barcode_row(x + 1).innerText = data[current_data_count + 1];
					display_element.classList.toggle('error', false)
					display_element.classList.toggle('pass', true)
		
					console.log(`Tube number: ${x + 1}\nStatus: PASS\nValue: ${data[current_data_count + 1]}`)
		
				} else {
		
					// 1 means barcode is invalid

					get_tube_barcode_row(x + 1).innerText = data[current_data_count + 1];
					display_element.classList.toggle('pass', false)
					display_element.classList.toggle('error', true)

					// Display fail in status bar
					statusBarManager.set_fail();
					
					console.log(`Tube number: ${x + 1}\nStatus: FAIL`)
		
				}
		
			}
		} else if (rack_type === RackTypeEnum.TROUGH) {
		
			// Trough display/barcode

			for (let x = 0; x < laser_trough_count; x++) {
				
				// Position of data in the data array which are in pairs of 2, excluding the first arbitrary element
				let current_data_count = 1 + (x * 2);

				// Element reference for the trough display
				let display_element = get_trough_display_item(x + 1)
				
				if (data[current_data_count] === '0') {
					
					// 0 means barcode is valid

					get_trough_barcode_row(x + 1).innerText = data[current_data_count + 1];
					display_element.classList.toggle('error', false)
					display_element.classList.toggle('pass', true)
		
					console.log(`Trough number: ${x + 1}\nStatus: PASS\nValue: ${data[current_data_count + 1]}`)
		
				} else {
		
					// 1 means barcode is invalid

					get_trough_barcode_row(x + 1).innerText = '';
					display_element.classList.toggle('pass', false)
					display_element.classList.toggle('error', true)

					// Display fail in status bar
					statusBarManager.set_fail();
					
					console.log(`Trough number: ${x + 1}\nStatus: FAIL`)
		
				}
		
			}
			
		} else {

			// Invalid rack type error handling

			console.log(`Rack type is invalid, rack_type: ${rack_type}`);
			statusBarManager.set_fail('ERROR: INVALID RACK TYPE');

		}

	} else {

		// Error handling

		if (rack_type != null) {

			// No data
	
			console.log('No data received, nothing displayed');
			statusBarManager.set_fail('ERROR: NO DATA RECEIVED');

		} else if (data != null) {
			
			// No rack type
	
			console.log('No rack type received, nothing displayed');
			statusBarManager.set_fail('ERROR: NO RACK TYPE RECEIVED');

		} else {

			// No data and rack type
	
			console.log('No data and rack type received, nothing displayed');
			statusBarManager.set_fail('ERROR: NO DATA OR RACK TYPE RECEIVED');
		}

	}
	
}

function switch_rack_type(rack_type) {

	if (rack_type === RackTypeEnum.TUBE) {

		laser_tube_display.classList.toggle('hidden', false)
		laser_tube_barcode.classList.toggle('hidden', false)
		
		laser_trough_display.classList.toggle('hidden', true)
		laser_trough_barcode.classList.toggle('hidden', true)

	} else if (rack_type === RackTypeEnum.TROUGH) {

		laser_tube_display.classList.toggle('hidden', true)
		laser_tube_barcode.classList.toggle('hidden', true)
		
		laser_trough_display.classList.toggle('hidden', false)
		laser_trough_barcode.classList.toggle('hidden', false)
		
	}

}

function get_tube_display_item(sn) {
	return laser_tube_display.querySelector(`.gr-laser-item.i${sn}`);
}

function get_trough_display_item(sn) {
	return laser_trough_display.querySelector(`.gr-laser-item.i${sn}`);
}

function get_tube_barcode_row(sn) {
	return laser_tube_barcode.querySelector(`#barcode-${sn} .full-border`);
}

function get_trough_barcode_row(sn) {
	return laser_trough_barcode.querySelector(`#barcode-${sn} .full-border`);
}