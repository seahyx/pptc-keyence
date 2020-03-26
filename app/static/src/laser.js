const btn_start = document.querySelector('#btn-start');
const laser_modal = document.querySelector('#laser-modal');
const btn_select_cancel = document.querySelector('#btn-select-cancel');
const btn_select_confirm = document.querySelector('#btn-select-confirm');
const td_laser_select = document.querySelector('#td-laser-select');

btn_start.addEventListener('click', () => {
	laser_modal.setAttribute('data-enabled', '');
})

window.addEventListener('click', (event) => {
	if (event.target == laser_modal) {
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

var socketio = io.connect(`http://${document.domain}:${location.port}/laser/api`);

socketio.on('response', function(msg) {
	console.log(`Received data: ${msg.data}`);
});

btn_start.addEventListener('click', () => {
	socketio.emit('start', {data: 'Testing testing 123'});
})

function get_barcode_row(sn) {
	return document.querySelector(`#barcode-${sn} .full-border`);
}