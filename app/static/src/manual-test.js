const laser_tube_count = 24, laser_trough_count = 4;

const RackTypeEnum = {
	CARTRIDGE: 0,
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
const manual_pos_g1				= document.querySelector('#pos-g1');
const manual_pos_g3				= document.querySelector('#pos-g3');
const manual_btn_apply_g1		= document.querySelector('#btn-apply-g1')
const manual_btn_apply_g3		= document.querySelector('#btn-apply-g3')

// Laser Etch QC
const manual_btn_laser_pos_1   = document.querySelector('#btn-laser-move-pos-1');
const manual_pos_g2			   = document.querySelector('#pos-g2');
const manual_btn_apply_g2		= document.querySelector('#btn-apply-g2')
const manual_btn_laser_read_1D = document.querySelector('#btn-laser-read-1D');
const manual_btn_laser_read_2D_tube   = document.querySelector('#btn-laser-read-2D-tube');
const manual_btn_laser_read_2D_trough = document.querySelector('#btn-laser-read-2D-trough');

// SocketIO
var socketio = io.connect(`http://${document.domain}:${location.port}/manual/api`);

// Clear button
btn_clear.addEventListener('click', () => {
	//window.location = Globals.done_url;
	// to check
	clear_data()
});

manual_btn_init.addEventListener('click',() => {
	console.log('Initialization')
	socketio.emit('PLC-serial', 'H');
});

manual_btn_home_pos.addEventListener('click',() => {
	console.log('Home position')
	socketio.emit('PLC-serial', 'GB');
});

manual_btn_cart_pos_1.addEventListener('click',() => {
	console.log('Cartridge pos 1')
	socketio.emit('PLC-serial', 'G1');
	socketio.emit('PLC-serial', 'S');
});

manual_btn_cart_pos_2.addEventListener('click',() => {
	console.log('Cartridge pos 2')
	socketio.emit('PLC-serial', 'G3');
	socketio.emit('PLC-serial', 'S');
});

manual_btn_cart_read_1D.addEventListener('click',() => {
	console.log('Cartridge read 1D barcode')
	socketio.emit('1D-barcode')
});

manual_btn_cart_read_2D.addEventListener('click',() => {
	console.log('Cartridge read 2D barcode')
	socketio.emit('2D-barcode', RackTypeEnum.CARTRIDGE)
});

manual_btn_laser_pos_1.addEventListener('click',() => {
	console.log('Laser pos 1')
	socketio.emit('PLC-serial', 'G2');
	socketio.emit('PLC-serial', 'S');
});

manual_btn_laser_read_1D.addEventListener('click',() => {
	console.log('Laser read 1D barcode')
	socketio.emit('1D-barcode')
});

manual_btn_laser_read_2D_tube.addEventListener('click',() => {
	console.log('Laser read 2D barcode (tube)')
	socketio.emit('2D-barcode', RackTypeEnum.TUBE)
});

manual_btn_laser_read_2D_trough.addEventListener('click',() => {
	console.log('Laser read 2D barcode (trough)')
	socketio.emit('2D-barcode', RackTypeEnum.TROUGH)
});

manual_btn_apply_g1.addEventListener('click',() => {
	console.log('Apply Pos G1')
	socketio.emit('write-pos', 'S1'+manual_pos_g1.value)
});

manual_btn_apply_g2.addEventListener('click',() => {
	console.log('Apply Pos G2')
	socketio.emit('write-pos', 'S2'+manual_pos_g2.value)
});

manual_btn_apply_g3.addEventListener('click',() => {
	console.log('Apply Pos G3')
	socketio.emit('write-pos', 'S3'+manual_pos_g3.value)
});

// Initialization

imageStateManager = new ImageStateManager(manual_image_container);

// Functions
function clear_data() {
	console.log('Clear data')
	manual_rack_id.innerText = '';
	manual_work_order.innerText = '';
	data = [0,'',0,'',0,'',0,'',0,'',0,'',0,'',0,'',0,'',0,'',0,'',0,'',0,'',0,'',0,'',0,'',0,'',0,'',0,'',0,'',0,'',0,'',0,'',0,'',0,''];
	load_data(data, RackTypeEnum.TUBE);
}

function load_data(data, rack_type) {

	// Debugging purposes
	console.log(`data: ${data},\nrack_id: ${rack_type}`);

	// Load data, != checks against null and undefined
	let cnt = 0;
	if (data != null && rack_type != null) {

		if (rack_type == RackTypeEnum.TUBE) cnt = 24;
		else if (rack_type == RackTypeEnum.TROUGH) cnt = 4;
		else cnt = 21;

		// Tube display/barcode

		for (let x = 0, y = 1; x < cnt; x++, y++) {

			// Position of data in the data array which are in pairs of 2
			let current_data_count = (x * 2);
			if (rack_type == 0 && y == 3) y++

			get_barcode_row(y).innerText = data[current_data_count + 1];
			console.log(`Tube number: ${x + 1}, Value: ${data[current_data_count + 1]}`);

		}
	}

}

function get_barcode_row(sn) {
	return manual_tube_barcode.querySelector(`#barcode-${sn} .barcode`);
}

// Responses

socketio.on('position', function(msg) {
	console.log(`Received data: ${msg}`);
	if (msg.substring(0,2) == 'P1') {
		manual_pos_g1.value = msg.substring(2,5);
	}
	else if (msg.substring(0,2) == 'P2') {
		manual_pos_g2.value = msg.substring(2,5);
	}
	else {
		manual_pos_g3.value = msg.substring(2,5);
	}
});

socketio.on('response', function(msg) {
	console.log(`Received data: ${msg}`);
});

socketio.on('1D-barcode', function(rack_id, work_order) {
	manual_rack_id.innerText = rack_id;
	manual_work_order.innerText = work_order;
	console.log(`1D barcode ${rack_id}, ${work_order}`);
})


socketio.on('2D-barcode', function(rack_type, items) {
	console.log(`2D barcode ${rack_type} ${items}`);
	load_data(items, rack_type)
	imageStateManager.update_img()
})
