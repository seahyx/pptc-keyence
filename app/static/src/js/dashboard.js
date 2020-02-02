
let btns_remove = document.getElementsByClassName('btn-js-remove');
let btns_reset = document.getElementsByClassName('btn-js-reset');

for (let i = 0; i < btns_remove.length; i++) {
	btns_remove[i].addEventListener('click', () => {
		window.location.href = window.location.pathname +'?' + 'rmId=' + btns_remove[i].id;
	});
	btns_reset[i].addEventListener('click', () => {
		window.location.href = window.location.pathname + 'change-pass/' + btns_reset[i].id;
	});
}