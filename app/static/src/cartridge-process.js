const cartridge_count = 21

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

const status_bar             = document.querySelector('#cart-status');

const btn_done               = document.querySelector('#btn-done');
const td_cart_id             = document.querySelector('#cart-id');

const tb_cart_barcode        = document.querySelector('#cart-barcode');
const cart_display_container = document.querySelector('#cart-display-container');

const cart_image_cam1        = document.querySelector('#cart-img-cam1');
const cart_image_cam2        = document.querySelector('#cart-img-cam2');

// Done button

btn_done.addEventListener('click', () => {
	Globals.is_done = true;
	window.location = Globals.done_url;
});


// Initialization

statusBarManager = new StatusBarManager(status_bar);

load_data(Globals.error_no, Globals.data, statusBarManager);

cart_image_cam1.setAttribute('src', Globals.img_urls[0]);
cart_image_cam2.setAttribute('src', Globals.img_urls[1]);


// SocketIO

var socketio = io.connect(`http://${document.domain}:${location.port}/cartridge/api`);

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

function load_data(error_no, data, statusBarManager) {

	// Debugging purposes
	console.log(`data: ${data}, error no: ${error_no}`);
	
	// Set status to neutral first (reset)
	statusBarManager.set_neutral();

	// Load data, != checks against null and undefined
	if (error_no == 0 || error_no < -3) {

		// Set default status
		if (error_no == 0){
			statusBarManager.set_success();
		}
		else if (error_no == -4){
			statusBarManager.set_fail('FAIL: Invalid cartridge ID');
		}
		else {
			statusBarManager.set_fail('FAIL: Correct error then rescan');
		}

		for (let x = 0, barcode_num = 1; x < cartridge_count; x++, barcode_num++) {

			// Skip no. 3
			if (barcode_num === 3) barcode_num++;

			// Position of data in the data array which are in 3 in a set
			let current_data_count = (x * 3);

			// Element reference for the tube display
			let display_element = get_display_item(barcode_num);
			
			if (data[current_data_count] === '0') {
				
				// 0 means barcode is valid

				get_mask_row(barcode_num).innerText = data[current_data_count+1];
				get_barcode_row(barcode_num).innerText = data[current_data_count + 2];
				display_element.classList.toggle('error', false);
				display_element.classList.toggle('pass', true);
	
				console.log(`Tube number: ${x + 1}\nStatus: PASS\nValue: ${data[current_data_count + 1]}`);
	
			} else {
	
				// 1 means barcode is invalid

				get_mask_row(barcode_num).innerText = data[current_data_count+1];
				get_barcode_row(barcode_num).innerText = data[current_data_count + 2];
				display_element.classList.toggle('pass', false);
				display_element.classList.toggle('error', true);

				// Display fail in status bar
				console.log(`Tube number: ${x + 1}\nStatus: FAIL`);
	
			}
	
		}
	} else if (error_no == -2) {
		console.log('Invalid cartridge ID');
		statusBarManager.set_fail('FAIL: Invalid cartridge ID');
	} else {
		console.log('Cartridge ID exceeded retry');
		statusBarManager.set_fail('FAIL: Cartridge ID exceeded retry');
	}
	
}

function get_display_item(sn) {
	return cart_display_container.querySelector(`.gr-cart-item.i${sn}`);
}

function get_mask_row(sn) {
	return tb_cart_barcode.querySelector(`#barcode-${sn} .mask`);
}

function get_barcode_row(sn) {
	return tb_cart_barcode.querySelector(`#barcode-${sn} .barcode`);
}


/* Redirect Hook */

window.onbeforeunload = (e) => {

	if (Globals.error_no == 0 || Globals.error_no < -3) {
	/* Do any cleaning up here */
		console.log('Move cartridge images')
		socketio.emit('move_images');
	}

};
