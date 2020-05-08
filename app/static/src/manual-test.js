const laser_tube_count = 24, laser_trough_count = 4;

const RackTypeEnum = {
	TUBE: 1,
	TROUGH: 2
}

class ImageStateManager {

	constructor(container) {

		// Image container
		this.container = container;

		// Obtain components
		this.zoom_container = container.querySelector('.zoom-container');
		this.img         = this.zoom_container.querySelector('.display-img');
		this.zoom_lens   = this.zoom_container.querySelector('.zoom-lens');
		this.zoom_result = this.zoom_container.querySelector('.zoom-result');
		this.next        = container.querySelector('#btn-next');
		this.prev        = container.querySelector('#btn-prev');
		this.title       = container.querySelector('#image-title');
		this.count       = container.querySelector('#image-count');

		// Default image index
		this.current_image_index = 0;

		// Set listeners to the buttons
		this.next.addEventListener('click', () => {
			this.set_next_img();
		})

		this.prev.addEventListener('click', () => {
			this.set_prev_img();
		})

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
			this.zoom_result.classList.toggle('activated', true);
		});

		this.zoom_result.addEventListener('click', () => {
			this.zoom_result.classList.toggle('activated', false);
		});


		// Update image, title, count, and button
		this.update_everything();

	}

	set_next_img() {
		if (this.current_image_index < Globals.img_urls.length - 1) {
			this.current_image_index++;

			this.update_everything();
		}
	}

	set_prev_img() {
		if (this.current_image_index > 0) {
			this.current_image_index--;

			this.update_everything();
		}
	}

	update_everything() {
		this.update_img();
		this.update_zoom();
		this.update_text();
		this.update_button_attr();
	}

	update_img() {
		this.img.setAttribute('src', Globals.img_urls[this.current_image_index]);
	}

	update_zoom() {
		this.lens_ratio = this.img.width / this.zoom_lens.offsetHeight;

		this.zoom_result.style.backgroundImage = 'url("' + Globals.img_urls[this.current_image_index] + '")';
		this.zoom_result.style.backgroundSize = (this.img.width * this.lens_ratio) + 'px ' + (this.img.height * this.lens_ratio) + 'px';
	}

	update_text() {
		this.title.innerText = Globals.img_titles[this.current_image_index];

		this.count.innerText = `${this.current_image_index + 1} / ${Globals.img_urls.length}`;
	}

	update_button_attr() {
		this.prev.toggleAttribute('disabled', this.current_image_index <= 0);
		this.next.toggleAttribute('disabled', this.current_image_index >= Globals.img_urls.length - 1);
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

const btn_clear                = document.querySelector('#btn-clear');
const manual_work_order        = document.querySelector('#manual-work-order');
const manual_rack_id           = document.querySelector('#manual-id');

const manual_tube_barcode      = document.querySelector('#manual-tube-barcode');

const manual_image_container   = document.querySelector('#manual-img-container');

// Main
const manual_btn_init          = document.querySelector('#btn-initialization');
const manual_btn_home_pos      = document.querySelector('#btn-home-pos');

// Cartridge Assembly QC
const manual_btn_cart_pos_1    = document.querySelector('#btn-cart-move-pos-1');
const manual_btn_cart_read_1D  = document.querySelector('#btn-cart-read-1D');
const manual_btn_cart_pos_2    = document.querySelector('#btn-cart-move-pos-2');
const manual_btn_cart_read_2D  = document.querySelector('#btn-cart-read-2D');

// Laser Etch QC
const manual_btn_laser_pos_1   = document.querySelector('#btn-laser-move-pos-1');
const manual_btn_laser_read_1D = document.querySelector('#btn-laser-read-1D');
const manual_btn_laser_pos_2   = document.querySelector('#btn-laser-move-pos-2');
const manual_btn_laser_read_2D = document.querySelector('#btn-laser-read-2D');



// Done button

btn_clear.addEventListener('click', () => {
	window.location = Globals.done_url;
	// to check
});


// Initialization

imageStateManager = new ImageStateManager(manual_image_container);

// load_data(Globals.data, Globals.rack_type);


// SocketIO
var socketio = io.connect(`http://${document.domain}:${location.port}/manual/api`);

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

function load_data(data, rack_type) {

	// Debugging purposes
	console.log(`data: ${data},\nrack_id: ${rack_type}`);

	// Load data, != checks against null and undefined
	if (data != null && rack_type != null) {

		if (rack_type === RackTypeEnum.TUBE) {

			// Tube display/barcode

			for (let x = 0; x < laser_tube_count; x++) {

				// Position of data in the data array which are in pairs of 2
				let current_data_count = (x * 2);

				// Element reference for the tube display
				let display_element = get_display_item(x + 1);

				if (data[current_data_count] === '0') {

					// 0 means barcode is valid

					get_barcode_row(x + 1).innerText = data[current_data_count + 1];
					display_element.classList.toggle('error', false);
					display_element.classList.toggle('pass', true);

					console.log(`Tube number: ${x + 1}\nStatus: PASS\nValue: ${data[current_data_count + 1]}`);

				} else {

					// 1 means barcode is invalid

					get_barcode_row(x + 1).innerText = data[current_data_count + 1];
					display_element.classList.toggle('pass', false);
					display_element.classList.toggle('error', true);

					// Display fail in status bar
					statusBarManager.set_fail('FAIL - Correct error then rescan');
					console.log(`Tube number: ${x + 1}\nStatus: FAIL`);

				}

			}
		}
	}

}

function get_barcode_row(sn) {
	return laser_tube_barcode.querySelector(`#barcode-${sn} .barcode`);
}
