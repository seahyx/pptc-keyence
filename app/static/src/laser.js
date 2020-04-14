const btn_start          = document.querySelector('#btn-start');
const laser_modal        = document.querySelector('#laser-modal');
const btn_select_cancel  = document.querySelector('#btn-select-cancel');
const btn_select_confirm = document.querySelector('#btn-select-confirm');
const in_work_order      = document.querySelector('#laser-work-order');
const in_part_number     = document.querySelector('#laser-part-number');

window.addEventListener('click', (event) => {
	if (event.target === laser_modal) {
		laser_modal.removeAttribute('data-enabled');
	}
});

btn_select_cancel.addEventListener('click', (event) => {
	laser_modal.removeAttribute('data-enabled');
});

// Validate part number data

var invalidChars = [
	'-',
	'+',
	'e',
];

in_part_number.addEventListener('input', () => {
	in_part_number.value = in_part_number.value.replace(/[e\+\-]/gi, '');
});

in_part_number.addEventListener('keydown', (e) => {
	if (invalidChars.includes(e.key)) {
		e.preventDefault();
	}
});

in_part_number.addEventListener('change', () => {
	if (in_part_number.value.length < Globals.in_part_number_min_len) {
		alert('Part number is invalid, please try again');
		return
	}
	// socketio.emit('partnumber', in_part_number.value);
})


// SocketIO

let socketio = io.connect(`http://${document.domain}:${location.port}/laser/api`);

// Start button, validate work order/part number
btn_start.addEventListener('click', () => {

	if (!in_work_order.value || !in_part_number.value) {
		alert('Please enter the work order and/or part number.');
		return
	}

	laser_modal.setAttribute('data-enabled', '');
	socketio.emit('start', in_work_order.value, in_part_number.value)

});


// Confirm button
btn_select_confirm.addEventListener('click', () => {

	// Change laser instrument selected
	let instrument_selected = document.querySelector('input[type="radio"][name="laser-modal-radio"]:checked');

	if (instrument_selected === null) {

		// No instrument selected (error!)
		alert('Please select a laser instrument!')
		return;

	}
	
	// Hide Modal
	laser_modal.removeAttribute('data-enabled');

	// Send data to server
	socketio.emit('confirm', in_work_order.value, in_part_number.value, instrument_selected.value);

});


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