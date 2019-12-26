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

document.querySelector("#button-open").addEventListener('click', () => getHttp('/open-door/'))
document.querySelector("#button-open").addEventListener('click', () => console.log('Button Pressed'))