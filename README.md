# Bird Camera Detection
Detect bird on camera, checks if image is blurred, and save valid images.

## Commands
```bash
# Env
sudo apt install python3-venv
python3 -m venv .venv
source .venv/bin/activate

# Packages
uv sync

# Run
uv run python main.py --display --verbose
uv run python test.py
uv run python gallery.py
```

## Forward from WSL
```cmd
netsh interface portproxy show v4tov4
netsh interface portproxy add v4tov4 listenport=5001 listenaddress=0.0.0.0 connectport=5000 connectaddress=172.26.248.204
```
