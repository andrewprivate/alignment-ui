use nokhwa::pixel_format::RgbFormat;
use nokhwa::utils::{CameraIndex, RequestedFormat, RequestedFormatType};
use nokhwa::{nokhwa_initialize, CallbackCamera, Camera};
use pyo3::prelude::*;
use std::net::TcpListener;
use std::io::{Cursor, Write};

fn server_loop(listener: TcpListener) {
    nokhwa_initialize(|granted| {
        println!("Granted: {:?}", granted);
    });

    // first camera in system
    let index = CameraIndex::Index(0); 
    // request the absolute highest resolution CameraFormat that can be decoded to RGB.
    let requested = RequestedFormat::new::<RgbFormat>(RequestedFormatType::AbsoluteHighestFrameRate);
    // make the camera
    let mut camera = CallbackCamera::new(index, requested, |_buffer| {

    }).unwrap();

    // let mut camera = Camera::new(index, requested).unwrap();
    camera.open_stream().unwrap();


    let mut buf: Vec<u8> = Vec::new();
    loop {
        let (mut stream, _) = listener.accept().expect("Failed to accept connection");
        
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
            let frame = camera.poll_frame().expect("Failed to get frame");
            let decoded = frame.decode_image::<RgbFormat>().unwrap();
            
            buf.clear();
            decoded.write_to(&mut Cursor::new(&mut buf), image::ImageFormat::Jpeg).unwrap();

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