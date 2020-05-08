const btn_start     = document.querySelector('#btn-start');
const loading_modal = document.querySelector('#loading-modal');
const cart_id  		= document.querySelector('#cart-id');
const status_bar    = document.querySelector('#cart-status');

class StatusBarManager {

	constructor(status_bar) {
		this.status_bar = status_bar;
		this.status_text = status_bar.querySelector('p');
	}

	set_text(text) {
		this.status_text.innerText = text;
	}

	reset() {
		this.set_text('');
		this.status_bar.classList.toggle('pass', false);
		this.status_bar.classList.toggle('error', false);
	}

	set_success(success_msg = 'PASS') {
		this.reset();
		this.set_text(success_msg);
		this.status_bar.classList.toggle('pass', true);
	}

	set_fail(error_msg = 'FAIL') {
		this.reset();
		this.set_text(error_msg);
		this.status_bar.classList.toggle('error', true);
	}

	set_neutral(msg = '-') {
		this.reset();
		this.set_text(msg);
	}

}

statusBarManager = new StatusBarManager(status_bar);

// SocketIO

var socketio = io.connect(`http://${document.domain}:${location.port}/cartridge/api`);

// Start button, validate work order/part number
btn_start.addEventListener('click', () => {
	statusBarManager.set_text('Processing')
	loading_modal.setAttribute('data-enabled', '');
	socketio.emit('PLC-serial', 'S');
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
		socketio.emit('PLC-serial', 'G1');
	}
});

socketio.on('get_cartridge_id', function(msg) {
	console.log(`Received data: ${msg.Cart_ID}, Error: ${msg.Error_No}`);
	if (msg.Cart_ID) {
		cart_id.innerHTML = msg.Cart_ID
	}
	if (msg.Error_No == -3){
		loading_modal.removeAttribute('data-enabled');
		statusBarManager.set_fail('FAIL: Exceeded Max Retry')
		alert('Exceeded max retry')
	}
	else if (msg.Error_No == -2)
	{
		loading_modal.removeAttribute('data-enabled');
		statusBarManager.set_fail('FAIL: Invalid Cartridge ID')
		alert('Invalid Cartridge ID')
	}
});

socketio.on('redirect', function(url) {
	console.log(`Redirecting to ${url}`);
	window.location = url;
})

socketio.on('plc-message', function(data) {
	console.log(`PLC sent ${data}`)

	if (data == 'R') { // Start button pressed
		socketio.emit('PLC-serial', 'S')	
	}
	else if (data == 'G1') { // Reach scan position
		socketio.emit('scan-position');
	}
	else if (data == 'G3') {
		socketio.emit('scan-position2')
	} else if (data == 'E') {
		alert('E-STOP PRESSED');
	}
})