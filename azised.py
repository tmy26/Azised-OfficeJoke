import hashlib
import random
import subprocess
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

ROTATION_TIME = 4 * 60 * 60
RETRY_TIME = 5 * 60
APP_DIR = Path.home() / ".azised"
CACHE_DIR = APP_DIR / "cache"

image_urls = [
    "https://cdn4.focus.bg/fakti/photos/16x9/776/azis-az-ne-se-strahuvam-ot-evroto-ako-ima-referendum-za-evroto-shte-glasuvam-za-1.webp",
    "https://cdn-images.dzcdn.net/images/artist/14c4c15b12f84dac9bd84f77cc1c1e40/1900x1900-000000-80-0-0.jpg",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSK4QcP3qMfouk4g93edmRLI2Af-mVXuRLP_w&s",
    "https://i.id24.bg/i/1182382.jpg",
]


def set_wallpaper(image_path: str) -> None:
    """
    Set the macOS desktop wallpaper for every desktop on every screen.

    Requires an absolute path; AppleScript silently ignores relative paths.
    """
    absolute_path = Path(image_path).expanduser().resolve()
    if not absolute_path.is_file():
        raise FileNotFoundError(absolute_path)

    script = '''
    on run argv
        set imagePath to item 1 of argv
        tell application "System Events"
            set theDesktops to every desktop
            repeat with d in theDesktops
                set picture of d to POSIX file imagePath
            end repeat
        end tell
    end run
    '''
    subprocess.run(["osascript", "-e", script, str(absolute_path)], check=True)


def _image_file_path(image_url: str) -> Path:
    suffix = Path(urlparse(image_url).path).suffix or ".jpg"
    digest = hashlib.sha256(image_url.encode("utf-8")).hexdigest()[:16]
    return CACHE_DIR / f"{digest}{suffix}"


def download_images() -> list[str]:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    file_names: list[str] = []

    for image_url in image_urls:
        file_path = _image_file_path(image_url)
        if file_path.exists():
            file_names.append(str(file_path))
            continue

        try:
            urllib.request.urlretrieve(image_url, file_path)
        except Exception as exc:
            print(f"Failed to download {image_url}: {exc}", flush=True)
            continue

        file_names.append(str(file_path))

    return file_names


def picture_to_set(file_names: list[str]) -> None:
    if file_names:
        set_wallpaper(random.choice(file_names))


def main() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    file_names = download_images()
    while True:
        if not file_names:
            print("No images available; retrying later.", flush=True)
            time.sleep(RETRY_TIME)
            continue

        picture_to_set(file_names)
        time.sleep(ROTATION_TIME)


if __name__ == "__main__":
    main()
