const laser_tube_count = 24;
const laser_trough_count = 4;

const DisplayEnum = {
	TUBE: 1,
	TROUGH: 2
}

let current_display = DisplayEnum.TUBE;

const btn_start = document.querySelector('#btn-start');
const laser_modal = document.querySelector('#laser-modal');
const btn_select_cancel = document.querySelector('#btn-select-cancel');
const btn_select_confirm = document.querySelector('#btn-select-confirm');
const td_laser_select = document.querySelector('#td-laser-select');
const in_work_order = document.querySelector('#laser-work-order');
const in_part_number = document.querySelector('#laser-part-number');

window.addEventListener('click', (event) => {
	if (event.target === laser_modal) {
		laser_modal.removeAttribute('data-enabled');
	}
})
btn_select_cancel.addEventListener('click', (event) => {
	laser_modal.removeAttribute('data-enabled');
})
btn_select_confirm.addEventListener('click', (event) => {
	let instrument_selected = document.querySelector('input[type="radio"][name="laser-modal-radio"]:checked');
	if (instrument_selected !== null) {
		td_laser_select.innerText = instrument_selected.value;
	}
	laser_modal.removeAttribute('data-enabled');
})


// SocketIO

var socketio = io.connect(`http://${document.domain}:${location.port}/laser/api`);

btn_start.addEventListener('click', () => {

	if (!in_work_order.value || !in_part_number.value) {
		alert('Please enter the work order and/or part number.');
		return
	}

	laser_modal.setAttribute('data-enabled', '');
	socketio.emit('start', {data: `${in_work_order.value},${in_part_number.value}`})

})

btn_select_confirm.addEventListener('click', () => {
	socketio.emit('confirm', {data: `${in_work_order.value},${in_part_number.value}`});
})

socketio.on('response', function(msg) {
	console.log(`Received data: ${msg.data}`);
});

socketio.on('confirm_data', function(msg) {

	console.log(`Received data from event 'start_data': ${msg.data}`);

	if (current_display === DisplayEnum.TUBE) {

		for (let x = 0; x < laser_tube_count; x++) {

			console.log(`Iterating through tube number ${x + 1}`)
			
			let current_data_count = 1 + (x * 2);
			let display_item = get_tube_display_item(x + 1)
			
			if (msg.data[current_data_count] === '0') {
				
				// 0 means barcode is valid

				console.log(`Status: PASS\nValue: ${msg.data[current_data_count + 1]}`)
				get_barcode_row(x + 1).innerText = msg.data[current_data_count + 1];
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