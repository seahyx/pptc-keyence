/* Loads nav menu open/close state */

// Returns true/false for open/close
// !! Returns a string !!
let nav_state = localStorage.getItem('nav-open') ? localStorage.getItem('nav-open') : null;

if (nav_state !== null) {
	document.documentElement.setAttribute('data-nav-open', nav_state);
} else {
	nav_state = 'true';
}