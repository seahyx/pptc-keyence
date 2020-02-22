/* Provide functionality for nav menu toggle button */
/* Saves menu toggle state (open/close) */

// Checkbox element
const nav_toggle = document.querySelector('#nav-toggle');

// Save toggle state
function toggleNav(e) {
	let checked = e.target.checked;
	
	// Value will be converted to string!
	localStorage.setItem('nav-open', checked);
	
	// Change theme
	document.documentElement.setAttribute('data-nav-open', checked);
}

// Load toggle state
nav_toggle.checked = nav_state === 'true' ? true : false;

// Attach listener to toggle
nav_toggle.addEventListener('change', toggleNav, false);
