// Clock

display_time();

function display_load() {
	let refresh = 1000; // Refresh rate in milliseconds
	mytime = setTimeout('display_time()', refresh);
}

function display_time() {
	let date = new Date();
	let formatted_date = `${date.toLocaleTimeString()} - ${date.toLocaleDateString()}`;
	document.getElementById('time').innerHTML = formatted_date;
	display_load();
}


// Navbar open/close state

function getHttp(url) {
    return new Promise((resolve) => {
        let xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function () {
            if (this.readyState === 4 && this.status === 200) {
                resolve(this.responseText);
            }
        };
        xhttp.open("GET", url);
        xhttp.send();
    });
}

let nav_btn = document.getElementById('nav-btn');
nav_btn.addEventListener('change', () => {
	// If checked, navbar is closed
	if (nav_btn.checked) {
		getHttp('/navbar/closed')
    } else {
		getHttp('/navbar/open')
    }
});