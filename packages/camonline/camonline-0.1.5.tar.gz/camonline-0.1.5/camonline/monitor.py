import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Union

import cv2 as cv

from camonline.camera import Camera, CameraManager
from camonline.config import Config, Configuable
from camonline.log import logger


class RotateMonitor(Configuable):
    default_config = {
        "camera": {
            "device": 0,
        },
        "storage": {
            "record_dir": "~/.camonline/storage",
            "resolution": [640, 480],
            "fourcc": "PIM1",
            "suffix": ".mkv",
            "days": 30,
            "hours": 1,
        },
    }

    def __init__(self, config: Optional[Union[Config, Dict[str, Any]]] = None, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.camera: Camera = CameraManager.get_or_create(self.config.camera.device)
        self.record_dir.mkdir(parents=True, exist_ok=True)
        self.start_day = datetime.now().strftime("%Y-%m-%d")
        self.shutdown_event = threading.Event()

        self._attatch_func = None
        self._shutdown_callback = None

        self._start_datetime = None
        self._thread = None
        self._clean_thread = None
        self._rotate_thread = None

        self._fps = None

    @property
    def record_dir(self) -> Path:
        return Path(self.config.storage.record_dir).expanduser().absolute()

    @property
    def current_record_file(self) -> Path:
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        current = now.strftime("%H-%M-%S")
        if not (self.record_dir / today).exists():
            (self.record_dir / today).mkdir(parents=True, exist_ok=True)
        return (self.record_dir / today / current).with_suffix(self.config.storage.suffix)

    @property
    def fps(self):
        if not self._fps:
            self._fps = self.config.storage.fps or self.camera.fps
        return self._fps

    def attatch(self):
        self._start_datetime = datetime.now()
        fourcc = cv.VideoWriter_fourcc(*self.config.storage.fourcc)
        out = cv.VideoWriter(
            self.current_record_file.as_posix(),
            fourcc,
            self.fps,
            self.config.storage.resolution or self.camera.resolution,
        )

        def _(frame):
            out.write(frame)

        logger.info(f"Attatch to {self.current_record_file}")
        self._attatch_func = _
        self.camera.add_callback(_)

        def _close():
            out.release()

        self._shutdown_callback = _close

    def reattatch(self):
        logger.info("Reattatch triggerd")
        if self._attatch_func:
            self.camera.remove_callback(self._attatch_func)
        if self._shutdown_callback:
            self._shutdown_callback()
        self.attatch()

    def start(self):
        self.shutdown_event.clear()
        self.attatch()

        def _():
            while not self.shutdown_event.is_set():
                self.camera.poll()
                self.shutdown_event.wait(1 / self.fps)

        def _clean():
            while not self.shutdown_event.is_set():
                today = datetime.now()
                to_remove = today - timedelta(days=self.config.storage.days)
                to_remove_dir = self.record_dir / to_remove.strftime("%Y-%m-%d")
                if to_remove_dir.exists():
                    logger.info(
                        f"Delete {self.config.storage.days} days before record:{to_remove_dir}"
                    )
                    for file in to_remove_dir.iterdir():
                        file.unlink(missing_ok=True)
                    to_remove_dir.rmdir()
                else:
                    logger.debug(f"{to_remove_dir} not exists, skip delete.")

                self.shutdown_event.wait(600)

        def _rorate():
            while not self.shutdown_event.is_set():
                now = datetime.now()
                logger.info(f"Recoring video for {now - self._start_datetime}")
                if now - self._start_datetime > timedelta(hours=self.config.storage.hours):
                    self._start_datetime = now
                    logger.info("Rotate vedio file")
                    self.reattatch()
                self.shutdown_event.wait(60)

        self._thread = threading.Thread(target=_)
        self._thread.start()

        self._clean_thread = threading.Thread(target=_clean)
        self._clean_thread.start()

        self._rotate_thread = threading.Thread(target=_rorate)
        self._rotate_thread.start()

    def shutdown(self):
        self.shutdown_event.set()
        self._thread.join()
        self._rotate_thread.join()

        self.camera.remove_callback(self._attatch_func)

        self._shutdown_callback()
        self._shutdown_callback = None

        self._attatch_func = None
        self._thread = None
        self._rotate_thread = None


if __name__ == "__main__":
    from pathlib import Path

    from camonline.config import ConfigLoader

    _HERE = Path(__file__).parent
    config_loader = ConfigLoader(_HERE / "static" / "config.toml")

    monitor = RotateMonitor(config_loader.load_config())
    monitor.start()
    input()
    monitor.shutdown()
