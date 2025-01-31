# Bird Camera Detection
Detect bird on camera, checks if image is blurred, and save valid images.

## Aider Instructions:
- Update main.py: Add timestamp logs between calls.
- Extract variables ESP32_CAMERA_URL and SAVE_DIR and BLUR_THRESHOLD and CAPTURE_INTERVAL to outer .env file with default values.
- Add cli argument for count of checks. If not passed - run infinitely.
- Rename "--count" to "--checks".
- Rewrite check loop to not sleep if it was last check.
- Extract `datetime.now().strftime('%Y-%m-%d %H:%M:%S')}` blocks to separate function `timestamp()`.
- Extract `print(f"[{timestamp()}] .. )` parts to separate function `print_timed()`.
- Add "--display" boolean argument. If passed, create Window where captured image displayed, proportional resized with WIDTH=400. Update window content every check loop run.
- Extract display size width 800px to const "DISPLAY_WIDTH".
- Update DISPLAY_WIDTH const to be read from .env with default value.
- Resize Display window with DISPLAY_WIDTH also.
- Create analysis.py: Extract `contains_bird` and `is_blurred` to `analysis.py` file and link method from there.
- Update analysis.py: Add block `__name__ = "main"` with test `is_blurred` and `contains_bird` over local image "test.jpg".
- Update main.py: Add "--verbose" bool argument, when not passed print only success detection part of logs. When passed - write all logs al was before.
- Move "if args.verbose" checks to argument of print_timed.
- Rename `print_timed()` to `log()` and it usages.
- Make "Ctrl+C" keys to stop application work without errors.
- Update analysis.py: when run locally and if "test.jpg" not found - read "test_images" folder and run checks on every of them.
- Create test.py: Extract test functionality from `analysis.py` and add it to `test.py` as methods that are run locally.
- Update test.py: Colorize output for bird found false or true, to be green or red.
- Update test.py: Print in red for blurry detection true, and green for blurry false.

## Commands
```bash
uv run python main.py --display --verbose
uv run python test.py
uv run python gallery.py
```

## Forward from WSL
```cmd
netsh interface portproxy add v4tov4 listenport=5001 listenaddress=0.0.0.0 connectport=5000 connectaddress=172.26.248.204
```
