const btn_start           = document.querySelector('#btn-start');
const cartridge_modal_select  = document.querySelector('#cartridge-modal');
const cartridge_modal_loading = document.querySelector('#cartridge-loading');
const rack_id           = document.querySelector('#rack-id');

// SocketIO

var socketio = io.connect(`http://${document.domain}:${location.port}/cartridge/api`);

window.addEventListener('click', (event) => {
	if (event.target === cartridge_modal_select) {
		cartridge_modal_select.removeAttribute('data-enabled');
	}
});


// Start button, validate work order/part number
btn_start.addEventListener('click', () => {

	//cartridge_modal_loading.setAttribute('data-enabled', '');
	socketio.emit('PLC-serial', 'S')	
});

// Responses

socketio.on('alert', function(msg) {
	console.log(`Received alert: ${msg}`);
	alert(msg);
});

socketio.on('response', function(msg) {
	console.log(`Received message: ${msg}`);
});


socketio.on('connect', function(msg) {
	console.log(`Received data: ${msg}`);
	if (msg) {
		socketio.emit('PLC-serial', 'G1')	
	}
});

socketio.on('get_rack_id', function(msg) {
	console.log(`Received data: ${msg}`);
	if (msg) {
		rack_id.innerHTML = msg
	}
});

socketio.on('redirect', function(url) {
	console.log(`Redirecting to ${url}`);
	window.location = url;
})

socketio.on('plc-message', function(data) {
	//let msg = data.data;
	console.log(`PLC sent ${data}`)

	if (data == 'R') { // Start button pressed

		//cartridge_modal_loading.setAttribute('data-enabled', '');
		socketio.emit('PLC-serial', 'S')	
	}
	else if (data == 'G1') { // Reach scan position
		socketio.emit('scan-position');
	}
	else if (data == 'G3') {
		socketio.emit('scan-position2')
	}
})