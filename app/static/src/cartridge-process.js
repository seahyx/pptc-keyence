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

class ImageZoomManager {

	constructor(container, default_image_index) {

		// Image container
		this.container = container;

		// Obtain components
    this.zoom_container = container.querySelector('.zoom-container');
    this.img            = this.zoom_container.querySelector('.display-img');
    this.zoom_lens      = this.zoom_container.querySelector('.zoom-lens');
    this.zoom_result    = this.zoom_container.querySelector('.zoom-result');

		// Default image index
		this.current_image_index = default_image_index;

		/* Execute a function when someone moves the cursor over the image, or the lens: */
		this.zoom_lens.addEventListener('mousemove', (mouse_event) => {
			this.on_move_lens(mouse_event);
		});

		this.img.addEventListener('mousemove', (mouse_event) => {
			this.on_move_lens(mouse_event);
		});

		/* And also for touch screens: */
		this.zoom_lens.addEventListener('touchmove', (mouse_event) => {
			this.on_move_lens(mouse_event);
		});

		this.img.addEventListener('touchmove', (mouse_event) => {
			this.on_move_lens(mouse_event);
		});


		// Zoom in and zoom out
		this.zoom_lens.addEventListener('click', () => {
			this.update_everything();
			this.zoom_result.classList.toggle('activated', true);
		});

		this.zoom_result.addEventListener('click', () => {
			this.update_everything();
			this.zoom_result.classList.toggle('activated', false);
		});


		// Update image, title, count, and button
		this.update_everything();

	}

	update_everything() {
		this.update_img();
		this.update_zoom();
	}

	update_img() {
		this.img.setAttribute('src', Globals.img_urls[this.current_image_index]);
	}

	update_zoom() {
		this.lens_ratio = this.img.height / this.zoom_lens.offsetHeight;

		this.zoom_result.style.backgroundImage = 'url("' + Globals.img_urls[this.current_image_index] + '")';
		this.zoom_result.style.backgroundSize = (this.img.width * this.lens_ratio) + 'px ' + (this.img.height * this.lens_ratio) + 'px';
	}

	on_move_lens(mouse_event) {

		let cursor_pos, lens_x, lens_y;

		/* Update background image if it has yet to load correctly */
		if (this.lens_ratio == 0) {
			this.update_zoom();
		}

		/* Get the cursor's x and y positions: */
		cursor_pos = this.get_cursor_pos(mouse_event);

		/* Calculate the position of the lens: */
		lens_x = cursor_pos.x - (this.zoom_lens.offsetWidth / 2);
		lens_y = cursor_pos.y - (this.zoom_lens.offsetHeight / 2);

		/* Prevent the lens from being positioned outside the image: */
		if (lens_x > this.img.width - this.zoom_lens.offsetWidth) {lens_x = this.img.width - this.zoom_lens.offsetWidth;}
		if (lens_x < 0) {lens_x = 0;}
		if (lens_y > this.img.height - this.zoom_lens.offsetHeight) {lens_y = this.img.height - this.zoom_lens.offsetHeight;}
		if (lens_y < 0) {lens_y = 0;}

		/* Set the position of the lens: */
		this.zoom_lens.style.left = (lens_x + this.img.offsetLeft) + 'px';
		this.zoom_lens.style.top = (lens_y + this.img.offsetTop) + 'px';

		/* Display what the lens 'sees': */
		this.zoom_result.style.backgroundPosition = '-' + (lens_x * this.lens_ratio) + 'px -' + (lens_y * this.lens_ratio) + 'px';

	}

	get_cursor_pos(mouse_event) {

		let img_dom_rect, relative_x = 0, relative_y = 0;

		/* Get the x and y positions of the image: */
		img_dom_rect = this.img.getBoundingClientRect();

		/* Calculate the cursor's x and y coordinates, relative to the image: */
		relative_x = mouse_event.pageX - img_dom_rect.left;
		relative_y = mouse_event.pageY - img_dom_rect.top;

		/* Consider any page scrolling: */
		relative_x = relative_x - window.pageXOffset;
		relative_y = relative_y - window.pageYOffset;

		return {x: relative_x, y: relative_y};

	}

}

const status_bar                 = document.querySelector('#cart-status');

const btn_done                   = document.querySelector('#btn-done');
const td_cart_id                 = document.querySelector('#cart-id');

const tb_cart_barcode            = document.querySelector('#cart-barcode');
const cart_display_container     = document.querySelector('#cart-display-container');

const cart_image_container_cam1 = document.querySelector('#cart-img-container-cam1');
const cart_image_container_cam2 = document.querySelector('#cart-img-container-cam2');

// Done button

btn_done.addEventListener('click', () => {
	Globals.is_done = true;
	window.location = Globals.done_url;
});


// Initialization

statusBarManager = new StatusBarManager(status_bar);

imageZoomManager_1 = new ImageZoomManager(cart_image_container_cam1, 0);
imageZoomManager_2 = new ImageZoomManager(cart_image_container_cam2, 1);

load_data(Globals.error_no, Globals.data, statusBarManager);


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
