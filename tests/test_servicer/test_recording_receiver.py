"""Tests for the recording receiver."""

import tempfile
import threading
import time
import unittest
from pathlib import Path

import requests
import uvicorn

from tcode_api.servicer.recording_receiver import RecordingReceiver


class TestResolveDestination(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name).resolve()
        self.receiver = RecordingReceiver(self.root)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_simple_path(self) -> None:
        dest = self.receiver.resolve_destination("/robot1/CAM_POS_X.mp4")
        self.assertEqual(dest, self.root / "robot1" / "CAM_POS_X.mp4")

    def test_suffix_is_enforced(self) -> None:
        dest = self.receiver.resolve_destination("/clip.bin")
        self.assertEqual(dest, self.root / "clip.mp4")

    def test_missing_suffix_is_added(self) -> None:
        dest = self.receiver.resolve_destination("/robot1/clip")
        self.assertEqual(dest, self.root / "robot1" / "clip.mp4")

    def test_empty_and_directory_paths_rejected(self) -> None:
        self.assertIsNone(self.receiver.resolve_destination("/"))
        self.assertIsNone(self.receiver.resolve_destination(""))
        self.assertIsNone(self.receiver.resolve_destination("/robot1/"))

    def test_traversal_escape_rejected(self) -> None:
        self.assertIsNone(self.receiver.resolve_destination("/../outside.mp4"))
        self.assertIsNone(self.receiver.resolve_destination("/a/../../outside.mp4"))


class TestOpenUnique(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name).resolve()
        self.receiver = RecordingReceiver(self.root)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _open(self, name: str) -> Path:
        out, dest = self.receiver.open_unique(self.root / name)
        out.close()
        return dest

    def test_existing_file_never_overwritten(self) -> None:
        self.assertEqual(self._open("clip.mp4"), self.root / "clip.mp4")
        self.assertEqual(self._open("clip.mp4"), self.root / "clip-1.mp4")
        self.assertEqual(self._open("clip.mp4"), self.root / "clip-2.mp4")

    def test_hyphenated_name_kept_intact(self) -> None:
        self.assertEqual(self._open("my-clip.mp4"), self.root / "my-clip.mp4")
        self.assertEqual(self._open("my-clip.mp4"), self.root / "my-clip-1.mp4")

    def test_creates_parent_directories(self) -> None:
        dest = self._open("a/b/clip.mp4")
        self.assertEqual(dest, self.root / "a" / "b" / "clip.mp4")
        self.assertTrue(dest.exists())


class TestReceiverServer(unittest.TestCase):
    """Round-trips against a live uvicorn instance on an ephemeral port."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls._tmp.name).resolve()
        cls.receiver = RecordingReceiver(cls.root)
        config = uvicorn.Config(cls.receiver.app, host="127.0.0.1", port=0, log_level="error")
        cls.server = uvicorn.Server(config)
        cls.thread = threading.Thread(target=cls.server.run, daemon=True)
        cls.thread.start()
        deadline = time.monotonic() + 10
        while not cls.server.started:
            if time.monotonic() > deadline:
                raise RuntimeError("uvicorn failed to start within 10 s")
            time.sleep(0.01)
        cls.base = "http://127.0.0.1:{}".format(cls.server.servers[0].sockets[0].getsockname()[1])

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.should_exit = True
        cls.thread.join(timeout=5)
        cls._tmp.cleanup()

    def test_put_with_content_length(self) -> None:
        payload = b"x" * 200_000
        response = requests.put(f"{self.base}/robot1/CAM_POS_X.mp4", data=payload, timeout=5)
        self.assertEqual(response.status_code, 201)
        self.assertEqual((self.root / "robot1" / "CAM_POS_X.mp4").read_bytes(), payload)

    def test_put_chunked(self) -> None:
        chunks = [b"a" * 1000, b"b" * 1000, b"c" * 17]
        response = requests.put(f"{self.base}/chunked.mp4", data=iter(chunks), timeout=5)
        self.assertEqual(response.status_code, 201)
        self.assertEqual((self.root / "chunked.mp4").read_bytes(), b"".join(chunks))

    def test_post_works_too(self) -> None:
        response = requests.post(f"{self.base}/posted.mp4", data=b"hello", timeout=5)
        self.assertEqual(response.status_code, 201)
        self.assertEqual((self.root / "posted.mp4").read_bytes(), b"hello")

    def test_second_upload_gets_new_name(self) -> None:
        requests.put(f"{self.base}/dup.mp4", data=b"first", timeout=5)
        requests.put(f"{self.base}/dup.mp4", data=b"second", timeout=5)
        self.assertEqual((self.root / "dup.mp4").read_bytes(), b"first")
        self.assertEqual((self.root / "dup-1.mp4").read_bytes(), b"second")

    def test_bad_path_rejected(self) -> None:
        response = requests.put(f"{self.base}/", data=b"x", timeout=5)
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
