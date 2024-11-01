#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use tauri::Manager;
use std::process::{Command, Stdio, Output};
use std::io::{BufRead, BufReader, Write};

fn log_output(output: &Output) -> String {
    // Helper function to log and format command output
    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);
    
    println!("Command Execution Details:");
    println!("STDOUT: {}", stdout);
    println!("STDERR: {}", stderr);
    println!("Exit Status: {}", output.status);

    format!(
        "STDOUT:\n{}\n\nSTDERR:\n{}\n\nExit Status: {}",
        stdout, stderr, output.status
    )
}


#[tauri::command]
fn interactive_login(email: String, password: String) -> Result<String, String> {
    use std::process::{Command, Stdio};
    use std::io::{Write, BufReader, BufRead};

    println!("Starting interactive login");

    let mut process = Command::new("bylexa")
        .arg("login")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to spawn process: {}", e))?;

    {
        let stdin = process.stdin.as_mut().ok_or("Failed to open stdin")?;
        // Write email and password to stdin
        stdin.write_all(format!("{}\n{}\n", email, password).as_bytes())
            .map_err(|e| format!("Failed to write to stdin: {}", e))?;
    }

    let output = process.wait_with_output()
        .map_err(|e| format!("Failed to wait on process: {}", e))?;

    if output.status.success() {
        let stdout = String::from_utf8_lossy(&output.stdout).to_string();
        println!("Login successful: {}", stdout);
        Ok(stdout)
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr).to_string();
        println!("Login failed: {}", stderr);
        Err(stderr)
    }
}


#[tauri::command]
fn interactive_start() -> Result<String, String> {
    use std::process::{Command, Stdio};

    println!("Starting bylexa client");

    let mut process = Command::new("bylexa")
        .arg("start")
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to start bylexa client: {}", e))?;

    // Optionally, read output if necessary
    let output = process.wait_with_output()
        .map_err(|e| format!("Failed to wait on process: {}", e))?;

    if output.status.success() {
        let stdout = String::from_utf8_lossy(&output.stdout).to_string();
        println!("Bylexa client started: {}", stdout);
        Ok(stdout)
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr).to_string();
        println!("Failed to start bylexa client: {}", stderr);
        Err(stderr)
    }
}


#[tauri::command]
fn execute_command(command_type: String) -> Result<String, String> {
    println!("Attempting to execute command: bylexa {}", command_type);

    // Attempt direct output capture
    match Command::new("bylexa")
        .arg(command_type.clone())
        .output() 
    {
        Ok(output) => {
            println!("Command executed successfully");
            Ok(log_output(&output))
        },
        Err(e) => {
            eprintln!("Failed to execute bylexa {}: {}", command_type, e);
            Err(format!("Failed to execute bylexa {}: {}", command_type, e))
        }
    }
}

#[tauri::command]
fn start_interactive_shell() -> Result<String, String> {
    println!("Attempting to start interactive shell");

    match Command::new("bylexa")
        .arg("shell")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn() 
    {
        Ok(mut process) => {
            // Generate a unique session identifier
            let session_id = format!("session_{}", process.id());
            
            println!("Interactive shell started with session ID: {}", session_id);

            // Optional: Immediately read any initial output
            if let Some(stdout) = process.stdout.take() {
                let reader = BufReader::new(stdout);
                for line in reader.lines() {
                    if let Ok(line) = line {
                        println!("Shell initial output: {}", line);
                    }
                }
            }

            Ok(session_id)
        },
        Err(e) => {
            eprintln!("Failed to start interactive shell: {}", e);
            Err(format!("Failed to start interactive shell: {}", e))
        }
    }
}

#[tauri::command]
fn send_shell_input(session_id: String, input: String) -> Result<String, String> {
    println!("Attempting to send input to shell session: {}", session_id);

    // Verify the exact subcommands supported by bylexa
    match Command::new("bylexa")
        .args(&[input.clone()]) // Try passing input directly without 'execute'
        .output() 
    {
        Ok(output) => {
            if output.status.success() {
                println!("Shell input sent successfully");
                Ok(log_output(&output))
            } else {
                let error_msg = String::from_utf8_lossy(&output.stderr);
                Err(format!("Command failed: {}", error_msg))
            }
        },
        Err(e) => {
            eprintln!("Failed to send shell input: {}", e);
            Err(format!("Failed to send shell input: {}", e))
        }
    }
}

fn main() {
    // Set up logging to ensure we can see print statements
    #[cfg(debug_assertions)]
    {
        std::env::set_var("RUST_BACKTRACE", "1");
    }

    println!("Initializing Tauri application");

    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            interactive_login,
            interactive_start,
            execute_command,
            start_interactive_shell,
            send_shell_input
        ])
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            println!("Tauri application setup complete");
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
} 