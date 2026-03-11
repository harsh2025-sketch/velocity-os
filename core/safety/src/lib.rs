//! VELOCITY A-OS: THE AMYGDALA (Rust Edition)
//! Role: Pre-Trade Risk Engine (Safety Gatekeeper)
//! Optimization: Zero-Copy String Inspection via FFI

use std::ffi::CStr;
use std::os::raw::{c_char, c_int};

const MAX_MOUSE_SPEED: i32 = 2000;

#[no_mangle]
pub extern "C" fn check_command_safety(cmd_ptr: *const c_char) -> c_int {
    if cmd_ptr.is_null() { return 0; }

    let c_str = unsafe { CStr::from_ptr(cmd_ptr) };
    let cmd_str = match c_str.to_str() {
        Ok(s) => s,
        Err(_) => return 0,
    };

    const FORBIDDEN: [&str; 5] = ["rm -rf", ":(){ :|:& };:", "mkfs", "format", "dd if="];
    for danger in FORBIDDEN {
        if cmd_str.contains(danger) {
            println!("[AMYGDALA] THREAT BLOCKED: {}", danger);
            return 0;
        }
    }
    1
}

#[no_mangle]
pub extern "C" fn check_motor_safety(dx: c_int, dy: c_int) -> c_int {
    if dx.abs() > MAX_MOUSE_SPEED || dy.abs() > MAX_MOUSE_SPEED {
        println!("[AMYGDALA] MOTOR SURGE (dx:{}, dy:{}). BLOCKED.", dx, dy);
        return 0;
    }
    1
}
