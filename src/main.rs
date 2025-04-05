use native_windows_gui as nwg;
use native_windows_derive as nwd;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::Duration;
use winapi::um::winuser::{SendInput, INPUT, INPUT_0, INPUT_MOUSE, MOUSEINPUT, MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP};

#[derive(Default)]
pub struct AutoClicker {
    #[nwg_control(size: (300, 150), position: (300, 300), title: "Auto Clicker")]
    #[nwg_events( OnWindowClose: [AutoClicker::exit] )]
    window: nwg::Window,

    #[nwg_control(text: "Delay (ms):", size: (100, 25), position: (10, 10))]
    delay_label: nwg::Label,

    #[nwg_control(size: (100, 25), position: (120, 10))]
    delay_input: nwg::TextInput,

    #[nwg_control(text: "Start", size: (100, 30), position: (10, 50))]
    #[nwg_events( MousePress(up): [AutoClicker::toggle_clicking] )]
    toggle_button: nwg::Button,

    #[nwg_control(text: "Status: Stopped", size: (280, 25), position: (10, 90))]
    status_label: nwg::Label,
}

impl AutoClicker {
    fn exit(&self) {
        nwg::stop_thread_dispatch();
    }

    fn toggle_clicking(&self) {
        // TODO: Implement toggle functionality
    }

    fn perform_click() {
        unsafe {
            let mut input: INPUT = std::mem::zeroed();
            input.u.type_ = INPUT_MOUSE;
            input.u.mi = INPUT_0 {
                mouse: MOUSEINPUT {
                    dx: 0,
                    dy: 0,
                    mouseData: 0,
                    dwFlags: MOUSEEVENTF_LEFTDOWN | MOUSEEVENTF_LEFTUP,
                    time: 0,
                    dwExtraInfo: 0,
                }
            };
            SendInput(1, &mut input as *mut INPUT, std::mem::size_of::<INPUT>() as i32);
        }
    }
}

impl nwd::NwgUi for AutoClicker {
    fn init_ui(&mut self) -> Result<(), nwg::NwgError> {
        nwg::Window::builder()
            .size((300, 150))
            .position((300, 300))
            .title("Auto Clicker")
            .build(&mut self.window)?;

        nwg::Label::builder()
            .text("Delay (ms):")
            .size((100, 25))
            .position((10, 10))
            .build(&mut self.delay_label)?;

        nwg::TextInput::builder()
            .size((100, 25))
            .position((120, 10))
            .build(&mut self.delay_input)?;

        nwg::Button::builder()
            .text("Start")
            .size((100, 30))
            .position((10, 50))
            .build(&mut self.toggle_button)?;

        nwg::Label::builder()
            .text("Status: Stopped")
            .size((280, 25))
            .position((10, 90))
            .build(&mut self.status_label)?;

        Ok(())
    }
}

fn main() {
    nwg::init().expect("Failed to init Native Windows GUI");
    nwg::Font::set_global_family("Segoe UI").expect("Failed to set default font");
    
    let app = AutoClicker::build_ui(Default::default()).expect("Failed to build UI");
    nwg::dispatch_thread_events();
}
