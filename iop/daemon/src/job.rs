//! Execute an arbitrary program with file-backed I/O and a separate control pipe.
use serde_json::{json, Value};
use std::{fs::File, io, process::Stdio, time::Duration};
use tokio::{
    io::{AsyncBufReadExt, BufReader},
    process::Command,
    time,
};

fn text<'a>(value: &'a Value, key: &str) -> Result<&'a str, io::Error> {
    value[key]
        .as_str()
        .ok_or_else(|| io::Error::new(io::ErrorKind::InvalidInput, format!("Missing {key}")))
}

pub async fn run() -> Result<(), Box<dyn std::error::Error>> {
    let mut requests = BufReader::new(tokio::io::stdin()).lines();
    let Some(line) = requests.next_line().await? else {
        return Ok(());
    };
    let request: Value = serde_json::from_str(&line)?;
    let p = &request["params"];
    let args = p["command"]
        .as_array()
        .ok_or("command must be an argument array")?;
    let argv: Vec<&str> = args
        .iter()
        .map(|v| v.as_str().ok_or("command arguments must be strings"))
        .collect::<Result<_, _>>()?;
    if argv.is_empty() {
        return Err("command must contain an executable".into());
    }
    let mut command = Command::new(argv[0]);
    command
        .args(&argv[1..])
        .current_dir(text(p, "cwd")?)
        .stdin(match p["stdin"].as_str() {
            Some(path) => Stdio::from(File::open(path)?),
            None => Stdio::null(),
        })
        .stdout(Stdio::from(File::create(text(p, "stdout")?)?))
        .stderr(Stdio::from(File::create(text(p, "stderr")?)?))
        .kill_on_drop(true);
    if let Some(values) = p["env"].as_object() {
        for (key, value) in values {
            command.env(
                key,
                value.as_str().ok_or("environment values must be strings")?,
            );
        }
    }
    #[cfg(unix)]
    {
        command.process_group(0);
    }
    #[cfg(windows)]
    {
        command.creation_flags(0x00000200);
    }
    let timeout = p["timeout"].as_f64().unwrap_or(0.0);
    if !timeout.is_finite() || timeout < 0.0 {
        return Err("timeout must be nonnegative".into());
    }
    let mut child = match command.spawn() {
        Ok(child) => child,
        Err(error) => {
            super::emit(&json!({"id":request["id"], "error":error.to_string()})).await?;
            return Ok(());
        }
    };
    let pid = child.id().unwrap();
    #[cfg(windows)]
    let tree = super::process_tree::Tree::attach(&child)?;
    let result = async {
        super::emit(&json!({"id":request["id"],"event":"started","pid":pid})).await?;
        let timer = time::sleep(Duration::from_secs_f64(if timeout > 0.0 { timeout } else { 86400.0 }));
        tokio::pin!(timer);
        let response = loop {
            tokio::select! {
                status = child.wait() => {
                    let status = status?;
                    break json!({"id":request["id"],"result":{"exit_code":status.code().unwrap_or(-1)}});
                }
                message = requests.next_line() => {
                    let Some(line) = message? else { return Ok(()); };
                    let message: Value = serde_json::from_str(&line)?;
                    if message["method"] == "cancel" && message["params"]["id"] == request["id"] {
                        super::stop(&mut child).await;
                        break json!({"id":request["id"],"cancelled":true,"result":{"exit_code":-1}});
                    }
                }
                _ = &mut timer, if timeout > 0.0 => {
                    super::stop(&mut child).await;
                    break json!({"id":request["id"],"error":"Program exceeded its configured duration","result":{"exit_code":-1}});
                }
            }
        };
        // A completed program must not leave descendants using its files or devices.
        #[cfg(unix)] unsafe { libc::kill(-(pid as i32), libc::SIGKILL); }
        #[cfg(windows)] drop(tree);
        super::emit(&response).await?;
        Ok::<(), Box<dyn std::error::Error>>(())
    }.await;
    super::stop(&mut child).await;
    result
}
