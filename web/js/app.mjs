const eel = window.eel;

eel.say_hello_py("Javascript")

eel.expose(start_video_feed);
function start_video_feed(port) {
    document.getElementById("video-feed").src = `http://127.0.0.1:${port}`
}