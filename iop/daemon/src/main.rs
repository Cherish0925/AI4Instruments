//! Own one SDK process, forward its messages, and terminate it on timeout or EOF.
use serde_json::{json, Value};
use std::{env, io, process::Stdio, time::Duration};
use tokio::{
    io::{AsyncBufReadExt, AsyncWriteExt, BufReader},
    process::{Child, Command},
    time::{self, Instant},
};
mod job;
mod process_tree;

pub(crate) async fn emit(value: &Value) -> io::Result<()> {
    let mut output = tokio::io::stdout();
    output.write_all(format!("{value}\n").as_bytes()).await?;
    output.flush().await
}
pub(crate) async fn stop(child: &mut Child) {
    if let Some(id) = child.id() {
        #[cfg(unix)]
        unsafe {
            libc::kill(-(id as i32), libc::SIGKILL);
        }
        #[cfg(windows)]
        {
            let _ = Command::new("taskkill")
                .args(["/PID", &id.to_string(), "/T", "/F"])
                .stdout(Stdio::null())
                .stderr(Stdio::null())
                .status()
                .await;
        }
    }
    let _ = child.kill().await;
    let _ = child.wait().await;
}

#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut args: Vec<String> = env::args().skip(1).collect();
    if args == ["--version"] {
        println!("iop-execd {}", env!("CARGO_PKG_VERSION"));
        return Ok(());
    }
    if args == ["--job"] {
        return job::run().await;
    }
    let mut timeout = 300.0_f64;
    if args.first().map(String::as_str) == Some("--timeout") && args.len() >= 2 {
        timeout = args[1].parse()?;
        args.drain(0..2);
    }
    if args.first().map(String::as_str) == Some("--") {
        args.remove(0);
    }
    if args.is_empty() || !timeout.is_finite() || timeout <= 0.0 {
        return Err("Usage: iop-execd [--timeout seconds] -- program [arguments]".into());
    }
    let mut command = Command::new(&args[0]);
    command
        .args(&args[1..])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::inherit())
        .kill_on_drop(true);
    #[cfg(unix)]
    {
        command.process_group(0);
    }
    #[cfg(windows)]
    {
        command.creation_flags(0x00000200);
    }
    let mut child = command.spawn()?;
    #[cfg(windows)]
    let _tree = process_tree::Tree::attach(&child)?;
    let mut input = child.stdin.take().unwrap();
    let mut responses = BufReader::new(child.stdout.take().unwrap()).lines();
    let mut requests = BufReader::new(tokio::io::stdin()).lines();
    let mut pending: Option<Value> = None;
    let timer = time::sleep(Duration::from_secs_f64(timeout));
    tokio::pin!(timer);
    let outcome: Result<(), Box<dyn std::error::Error>> = async {
        loop {
            tokio::select! {
                line = requests.next_line() => {
                    let Some(line) = line? else { break; };
                    let message: Value = serde_json::from_str(&line)?;
                    let cancel = message["method"] == "cancel";
                    let duration = message["timeout_s"].as_f64().unwrap_or(timeout);
                    if !duration.is_finite() || duration <= 0.0 || duration > 31_536_000.0 {
                        emit(&json!({"id":message["id"],"error":"Timeout must be positive and at most one year"})).await?;
                        continue;
                    }
                    if !cancel {
                        if pending.is_some() {
                            emit(&json!({"id":message["id"],"error":"Worker is executing an operation"})).await?;
                            continue;
                        }
                        pending = Some(message["id"].clone());
                        timer.as_mut().reset(Instant::now() + Duration::from_secs_f64(duration));
                    } else if pending.is_some() {
                        let deadline = timer.deadline().min(Instant::now() + Duration::from_secs_f64(duration));
                        timer.as_mut().reset(deadline);
                    }
                    input.write_all(format!("{message}\n").as_bytes()).await?;
                    input.flush().await?;
                }
                line = responses.next_line() => {
                    let Some(line) = line? else {
                        if let Some(id) = pending.take() {
                            emit(&json!({"id":id,"error":"Driver process exited before returning a result","outcome_unknown":true})).await?;
                        }
                        break;
                    };
                    let response: Value = serde_json::from_str(&line)?;
                    if pending.as_ref() != Some(&response["id"]) {
                        return Err("Driver response does not match the active operation".into());
                    }
                    if response.get("event").is_none() {
                        pending = None;
                    }
                    emit(&response).await?;
                }
                _ = &mut timer, if pending.is_some() => {
                    emit(&json!({"id":pending.take(),"error":"Driver response timed out","outcome_unknown":true})).await?;
                    break;
                }
            }
        }
        Ok(())
    }.await;
    stop(&mut child).await;
    outcome
}
