function getHttp(url) {
	return new Promise((resolve) => {
		let xhttp = new XMLHttpRequest()
	
		xhttp.onreadystatechange = function() {
			if (this.readyState === 4 && this.status === 200) {
			resolve(this.responseText)
			}
		}
	
		xhttp.open("GET", url)
		xhttp.send();
	})
}

let btn_open = document.querySelector("#btn-open");
let btn_open_hold = document.querySelector("#btn-open-hold");
btn_open.addEventListener('click', () => getHttp('/open-door/'))
btn_open.addEventListener('click', () => console.log('Button Pressed'))
btn_open_hold.addEventListener('click', () => getHttp('/open-door/'))
btn_open_hold.addEventListener('click', () => console.log('Button Pressed'))