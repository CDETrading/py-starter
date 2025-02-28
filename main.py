import subprocess
import time
import os
import yaml
import sys
import asyncio
CONFIG_PATH = "config.yaml"

def load_configs():
    """Load configuration from a JSON file."""
    if not os.path.exists(CONFIG_PATH):
        print(f"Config file {CONFIG_PATH} not found.")
        return None
    
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

async def start_process(command):
    """Start a process asynchronously and return the subprocess object."""
    print(f"Starting process: {command}")
    return await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

async def monitor_process(config):
    """Monitor the process asynchronously and restart if it dies."""
    command = config["command"]
    process = await start_process(command)
    
    while True:
        try:
            exit_code = await process.wait()
            print(f"Process exited with code {exit_code}. Restarting...")
            await asyncio.sleep(config["interval"])  # Non-blocking sleep
            process = await start_process(command)
        except asyncio.CancelledError:
            print("Stopping monitoring...")
            process.terminate()
            await process.wait()
            break

async def main(process_name):
    configs = load_configs()
    print(configs)
    config = configs.get(process_name)
    if not config or "command" not in config:
        print("Invalid config file. It must contain a 'command' field.")
        return
    
    await monitor_process(config)

if __name__ == "__main__":
    process_name = sys.argv[1]
    print(process_name)
    asyncio.run(main(process_name))