// Clock

display_time();

function display_load() {
	let refresh = 1000; // Refresh rate in milliseconds
	mytime = setTimeout('display_time()', refresh);
}

function display_time() {
	let date = new Date();
	let formatted_date = `${date.toLocaleTimeString()} - ${date.toLocaleDateString()}`;
	document.getElementsByClassName('time')[0].innerHTML = formatted_date;
	display_load();
}