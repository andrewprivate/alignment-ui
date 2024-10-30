import { Controller } from "./ui/Controller.js";

const eel = window.eel;

window.controller = new Controller();
const element = window.controller.getElement();
document.body.appendChild(element); // Append the controller's UI to the body

element.style.width = '100%'; // Set the width of the controller's UI
element.style.height = '100%'; // Set the height of the controller's UI

eel.say_hello_py("Javascript")

eel.expose(start_video_feed);
function start_video_feed(port) {
    document.getElementById("video-feed").src = `http://127.0.0.1:${port}`
}

eel.expose(add_log_entry);
function add_log_entry(type, ...messages) {
    window.controller.logTray.addEntry(type, ...messages);
}

eel.expose(add_point);
function add_point(x, y, z) {
    window.controller.controlsWidget.addPoint(x, y, z);
}