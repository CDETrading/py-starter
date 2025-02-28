import os
import yaml
import sys
import asyncio
import logging
from datetime import datetime
import logging.handlers

CONFIG_PATH = "config.yaml"

log_filename = f"logs/py-start-{datetime.now().strftime('%Y-%m-%d')}.log"
os.makedirs("logs", exist_ok=True)  # Ensure logs directory exists

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',  # Include timestamp in logs
    handlers=[
        logging.handlers.RotatingFileHandler(log_filename, maxBytes=100000, backupCount=20),
        logging.StreamHandler(sys.stdout)  # Optional: also log to stdout
    ]
)

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
    logging.info(f"Starting process: {command}")

    while True:
        try:
            exit_code = await process.wait()
            logging.info(f"Process exited with code {exit_code}. Restarting...")
            await asyncio.sleep(config["interval"])  # Non-blocking sleep
            process = await start_process(command)
        except asyncio.CancelledError:
            logging.info("Stopping monitoring...")
            process.terminate()
            await process.wait()
            break
        except KeyboardInterrupt:
            print("Keyboard interrupt. Stopping monitoring...")
            logging.info("Keyboard interrupt. Stopping monitoring...")
            process.terminate()
            await process.wait()
            sys.exit()

async def main(process_name):
    configs = load_configs()
    logging.info(configs)
    config = configs.get(process_name)
    if not config or "command" not in config:
        logging.error("Invalid config file. It must contain a 'command' field.")
        return
    
    await monitor_process(config)

if __name__ == "__main__":
    process_name = sys.argv[1]
    logging.info(process_name)
    asyncio.run(main(process_name))