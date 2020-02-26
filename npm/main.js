const {app, BrowserWindow} = require('electron');
const {PythonShell} = require('python-shell');
let rq = require('request-promise');

let mainAddr = 'http://localhost:5000/';

function startUp() {

	console.log('Starting server...');

	PythonShell.run('../app.py', null, function(err) {
		if (err) throw err;

		console.log('Server closed!');
	});

	loadSite();

};

function loadSite() {
	rq(mainAddr)
	.then(function(htmlString) {
		console.log('Server started!');
		console.log('Creating window...');
		createWindow();
	})
	.catch(function(err) {
		console.log('waiting for the server start...');
		console.log(err);
		loadSite();
	});
}

function createWindow () {

	window = new BrowserWindow({width: 800, height: 600, show: false});

	// Load the index page of the flask in local server
	window.loadURL(mainAddr);

	// ready the window with load url and show
	window.once('ready-to-show', () => {
		window.show();
		console.log('Window created!');
	});

}

app.on('ready', startUp)

app.on('window-all-closed', () => {
	// On macOS it is common for applications and their menu bar
	// to stay active until the user quits explicitly with Cmd + Q
	if (process.platform !== 'darwin') {
		app.quit()
	}
})