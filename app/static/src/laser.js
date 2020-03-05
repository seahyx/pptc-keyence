const btn_start = document.getElementById('btn-start');
const laser_modal = document.getElementById('laser-modal');
const btn_select_cancel = document.getElementById('btn-select-cancel');
const btn_select_confirm = document.getElementById('btn-select-confirm');
const td_laser_select = document.getElementById('td-laser-select');

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