use pyo3::prelude::*;
use opencv::{
    core::{Mat, Vector}, imgcodecs, prelude::*, videoio,
};

use std::net::TcpListener;
use std::io::Write;

fn server_loop(listener: TcpListener) {
    let mut cam = videoio::VideoCapture::new(0, videoio::CAP_ANY).expect("Failed to get video capture");
    cam.set(videoio::CAP_PROP_FPS, 60.0).expect("Failed to set FPS");
    let mut frame = Mat::default();
    let mut buf = Vector::new();
    
    loop {
        let (mut stream, _) = listener.accept().expect("Failed to accept connection");
        
        cam.read(&mut frame).expect("Failed to capture frame");
        buf.clear();
        let _ = imgcodecs::imencode(".jpg", &frame, &mut buf, &Vector::new());

        let response = format!(
            "HTTP/1.1 200 OK\r\nContent-Type: multipart/x-mixed-replace; boundary=frame\r\n\r\n"
        );

        let res = stream.write_all(response.as_bytes());
        if res.is_err() {
            continue;
        }

        let mut last_time = std::time::Instant::now();
        let mut last_display = std::time::Instant::now();
        loop {
            cam.read(&mut frame).expect("Failed to capture frame");
            buf.clear();
            let _ = imgcodecs::imencode(".jpg", &frame, &mut buf, &Vector::new());

            let image_data = format!(
                "--frame\r\nContent-Type: image/jpeg\r\nContent-Length: {}\r\n\r\n",
                buf.len()
            );

            let mut res = stream.write_all(image_data.as_bytes());
            if res.is_err() {
                break;
            }

            res = stream.write_all(buf.as_slice());
            if res.is_err() {
                break;
            }

            res = stream.write_all(b"\r\n");
            if res.is_err() {
                break;
            }

            res = stream.flush();
            if res.is_err() {
                break;
            }

            let now = std::time::Instant::now();
            if now.duration_since(last_display).as_secs() > 1 {
                
                // Print fps
                let fps = 1.0 / (now.duration_since(last_time).as_secs_f64());
                println!("FPS: {}", fps);
                last_display = now;
            }
            last_time = now;
        }
    }
}

#[pyfunction]
pub fn start() -> u16 {
    let listener = TcpListener::bind("127.0.0.1:0").expect("Failed to bind to port");
    let port = listener.local_addr().unwrap().port();
    println!("Server listening on port {}", port);

    // run in a separate thread
    std::thread::spawn(move || {
        server_loop(listener);
    });

    port
}

#[pymodule]
fn pictestingrs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(start, m)?)
}