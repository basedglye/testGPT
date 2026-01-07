from accessibility_overlay.config import load_config
from accessibility_overlay.overlay import OverlayApp


def main() -> None:
    config = load_config()
    app = OverlayApp(config)
    app.start()


if __name__ == "__main__":
    main()
