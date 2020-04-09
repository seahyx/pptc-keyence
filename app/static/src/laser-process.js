const laser_tube_count = 24;
const laser_trough_count = 4;

const DisplayEnum = {
	TUBE: 1,
	TROUGH: 2
}

let current_display = DisplayEnum.TUBE;

const btn_done            = document.querySelector('#btn-done');
const laser_modal         = document.querySelector('#laser-modal');
const btn_select_cancel   = document.querySelector('#btn-select-cancel');
const btn_select_confirm  = document.querySelector('#btn-select-confirm');
const in_work_order       = document.querySelector('#laser-work-order');
const in_part_number      = document.querySelector('#laser-part-number');
const laser_rack_id       = document.querySelector('#laser-rack-id');

window.addEventListener('click', (event) => {
	if (event.target === laser_modal) {
		laser_modal.removeAttribute('data-enabled');
	}
});

btn_select_cancel.addEventListener('click', (event) => {
	laser_modal.removeAttribute('data-enabled');
});


// SocketIO

var socketio = io.connect(`http://${document.domain}:${location.port}/laser/api`);

// Init

socketio.emit('process-loaded')

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

socketio.on('process-init', function(data) {

	console.log(`Received data from event 'confirm_data': ${data}`);

	if (current_display === DisplayEnum.TUBE) {

		for (let x = 0; x < laser_tube_count; x++) {

			console.log(`Iterating through tube number ${x + 1}`)
			
			let current_data_count = 1 + (x * 2);
			let display_item = get_tube_display_item(x + 1)
			
			if (data[current_data_count] === '0') {
				
				// 0 means barcode is valid

				console.log(`Status: PASS\nValue: ${data[current_data_count + 1]}`)
				get_barcode_row(x + 1).innerText = data[current_data_count + 1];
				display_item.classList.toggle('error', false)
				display_item.classList.toggle('pass', true)

			} else {

				// 1 means barcode is invalid
				
				console.log(`Status: FAIL`)
				get_barcode_row(x + 1).innerText = '';
				display_item.classList.toggle('pass', false)
				display_item.classList.toggle('error', true)

			}

		}

	}

});

function get_barcode_row(sn) {
	return document.querySelector(`#barcode-${sn} .full-border`);
}

function get_tube_display_item(sn) {
	return document.querySelector(`.laser-tube .laser-underlay .gr-laser-item.i${sn}`);
}

function get_trough_display_item(sn) {
	return document.querySelector(`.laser-trough .laser-underlay .gr-laser-item.i${sn}`);
}