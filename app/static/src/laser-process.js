const laser_tube_count = 24;
const laser_trough_count = 4;

const RackTypeEnum = {
	TUBE: 1,
	TROUGH: 2
}

const btn_done             = document.querySelector('#btn-done');
const laser_modal          = document.querySelector('#laser-modal');
const btn_select_cancel    = document.querySelector('#btn-select-cancel');
const btn_select_confirm   = document.querySelector('#btn-select-confirm');
const in_work_order        = document.querySelector('#laser-work-order');
const in_part_number       = document.querySelector('#laser-part-number');
const laser_rack_id        = document.querySelector('#laser-rack-id');

const laser_tube_display   = document.querySelector('#laser-tube-display');
const laser_trough_display = document.querySelector('#laser-trough-display');
const laser_tube_barcode   = document.querySelector('#laser-tube-barcode');
const laser_trough_barcode = document.querySelector('#laser-trough-barcode');


window.addEventListener('click', (event) => {
	if (event.target === laser_modal) {
		laser_modal.removeAttribute('data-enabled');
	}
});

btn_select_cancel.addEventListener('click', (event) => {
	laser_modal.removeAttribute('data-enabled');
});


// Initialization

data    = Globals.data;
rack_type = Globals.rack_type;

console.log(`data: ${data},\nrack_id: ${rack_type}`);

// Set rack type
switch_rack_type(rack_type);

// Load data
if (data !== null) {

	// Tube display
	if (rack_type === RackTypeEnum.TUBE) {

		for (let x = 0; x < laser_tube_count; x++) {
	
			console.log(`Iterating through tube number ${x + 1}`)
			
			// Position of data in the data array which are in pairs of 2, excluding the first arbitrary element
			let current_data_count = 1 + (x * 2);

			// Element reference for the tube display
			let display_element = get_tube_display_item(x + 1)
			
			if (data[current_data_count] === '0') {
				
				// 0 means barcode is valid
	
				console.log(`Status: PASS\nValue: ${data[current_data_count + 1]}`)
				get_tube_barcode_row(x + 1).innerText = data[current_data_count + 1];
				display_element.classList.toggle('error', false)
				display_element.classList.toggle('pass', true)
	
			} else {
	
				// 1 means barcode is invalid
				
				console.log(`Status: FAIL`)
				get_tube_barcode_row(x + 1).innerText = '';
				display_element.classList.toggle('pass', false)
				display_element.classList.toggle('error', true)
	
			}
	
		}
	
		// Trough display
	} else if (rack_type === RackTypeEnum.TROUGH) {

		for (let x = 0; x < laser_trough_count; x++) {
	
			console.log(`Iterating through trough number ${x + 1}`)
			
			// Position of data in the data array which are in pairs of 2, excluding the first arbitrary element
			let current_data_count = 1 + (x * 2);

			// Element reference for the trough display
			let display_element = get_trough_display_item(x + 1)
			
			if (data[current_data_count] === '0') {
				
				// 0 means barcode is valid
	
				console.log(`Status: PASS\nValue: ${data[current_data_count + 1]}`)
				get_trough_barcode_row(x + 1).innerText = data[current_data_count + 1];
				display_element.classList.toggle('error', false)
				display_element.classList.toggle('pass', true)
	
			} else {
	
				// 1 means barcode is invalid
				
				console.log(`Status: FAIL`)
				get_trough_barcode_row(x + 1).innerText = '';
				display_element.classList.toggle('pass', false)
				display_element.classList.toggle('error', true)
	
			}
	
		}
		
	}

}



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