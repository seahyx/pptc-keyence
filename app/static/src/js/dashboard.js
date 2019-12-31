
let btns_remove = document.getElementsByClassName('button-remove');
let btns_reset = document.getElementsByClassName('button-reset');

for (let i = 0; i < btns_remove.length; i++) {
    btns_remove[i].addEventListener('click', () => {
		window.location.href = window.location.pathname +'?' + 'rmId=' + btns_remove[i].id.toString();
	});
}
