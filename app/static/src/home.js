// SocketIO
var socketio = io.connect(`http://${document.domain}:${location.port}/home/api`);

// Responses
socketio.on('connect', function(msg) {
	if (msg) {
		console.log(`Received data: ${msg}`);
	}

});

socketio.on('response', function(msg) {
	console.log(`Received data: ${msg}`);
});

socketio.on('redirect', function(url) {
	console.log(`Redirecting to ${url}`);
	window.location = url;
})

socketio.on('plc-message', function(data) {
	//let msg = data.data;
	console.log(`PLC sent ${data}`)

	if (data == 'E') { // Start button pressed
		alert('E-STOP PRESSED');
	} else if (data == 'H0') { // Reach scan position
		console.log('Home position')
	}

});