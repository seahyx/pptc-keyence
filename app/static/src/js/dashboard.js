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
let btns_remove = document.getElementsByClassName('button-remove');
let btns_edit = document.getElementsByClassName('button-edit');
for (let i = 0; i < btns_remove.length; i++) {
    const url = new URLSearchParams();
    url.set('rmId', i.toString());
    btns_remove[i].addEventListener('click', () => {
        getHttp('/dashboard/?' + url.toString());
    });
}
