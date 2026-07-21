"""Receiver for robot camera remote recordings.

The counterpart of trilo-cam's ``POST /cameras/{name}/remote-recording/start``:
the robot streams a fragmented MP4 over HTTP PUT/POST and this server writes it
to disk as it arrives, so large recordings live on the fleet controller instead
of the robot's limited storage.
"""

from pathlib import Path
from typing import BinaryIO

import anyio.to_thread
import fastapi
import plac  # type: ignore [import-untyped]
import uvicorn
from fastapi import FastAPI, Request
from starlette.requests import ClientDisconnect

RECORDING_RECEIVER_DEFAULT_PORT = 8096


class RecordingReceiver:
    """Accepts streamed recordings from robot cameras and writes them to disk.

    Start a remote recording pointing at this server, e.g.::

        POST http://<rcm>:8095/api/v1/cameras/CAM_POS_X/remote-recording/start
        {"url": "http://<fleet-controller>:8096/robot1/CAM_POS_X.mp4",
         "max_duration_s": 600}

    The request path becomes the file path under ``root`` (sanitized, ``.mp4``
    enforced, existing files never overwritten). Because the body is a
    fragmented MP4 written incrementally, a recording interrupted mid-stream
    still leaves a playable file prefix.

    :param root: Directory recordings are written into.
    """

    def __init__(self, root: Path | str):
        self.root = Path(root).resolve()
        self.app = FastAPI()

        @self.app.put("/{_:path}")
        @self.app.post("/{_:path}")
        async def _(request: Request) -> fastapi.Response:
            candidate = self.resolve_destination(request.url.path)
            if candidate is None:
                return fastapi.responses.JSONResponse(
                    status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                    content={"detail": "invalid recording path"},
                )
            total = 0
            try:
                out, dest = await anyio.to_thread.run_sync(self.open_unique, candidate)
            except OSError as exc:
                return _write_failure(candidate, exc)
            try:
                async for chunk in request.stream():
                    await anyio.to_thread.run_sync(out.write, chunk)
                    total += len(chunk)
            except ClientDisconnect:
                # A dropped sender is expected; the fMP4 prefix stays playable.
                print(f"{dest}: connection ended early after {total} bytes")
            except OSError as exc:
                return _write_failure(dest, exc)
            finally:
                await anyio.to_thread.run_sync(out.close)
            print(f"{dest} <- {total} bytes")
            return fastapi.Response(status_code=fastapi.status.HTTP_201_CREATED)

    def resolve_destination(self, url_path: str) -> Path | None:
        """Map a request URL path to a destination file under ``root``.

        Returns None when the path is empty, points at a directory, or escapes
        ``root``. The ``.mp4`` suffix is enforced. The returned path is a
        candidate only — :meth:`open_unique` performs the collision-free create.

        :param url_path: The path component of the request URL.
        """
        raw = url_path.lstrip("/")
        if not raw or raw.endswith("/"):
            return None
        try:
            rel = Path(raw).with_suffix(".mp4")
        except ValueError:
            return None
        dest = (self.root / rel).resolve()
        if not dest.is_relative_to(self.root) or dest == self.root:
            return None
        return dest

    def open_unique(self, dest: Path) -> tuple[BinaryIO, Path]:
        """Atomically create and open a new file at ``dest`` for writing.

        An existing file is never overwritten: on collision a ``-N`` suffix is
        appended and the create retried (``O_EXCL``, so concurrent uploads to
        the same path each get their own file).

        :param dest: The candidate path from :meth:`resolve_destination`.
        """
        dest.parent.mkdir(parents=True, exist_ok=True)
        base = dest
        counter = 1
        while True:
            try:
                return open(dest, "xb"), dest
            except FileExistsError:
                dest = base.with_name(f"{base.stem}-{counter}{base.suffix}")
                counter += 1

    def serve(self, host: str = "0.0.0.0", port: int = RECORDING_RECEIVER_DEFAULT_PORT):
        self.root.mkdir(parents=True, exist_ok=True)
        print(f"recording receiver on :{port} -> {self.root}")
        uvicorn.run(self.app, host=host, port=port)


def _write_failure(dest: Path, exc: OSError) -> fastapi.responses.JSONResponse:
    print(f"{dest}: write failed ({exc})")
    return fastapi.responses.JSONResponse(
        status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"failed to write recording: {exc}"},
    )


@plac.annotations(
    directory=plac.Annotation(
        "Directory recordings are written into", abbrev="d", kind="option", type=Path
    ),
    port=plac.Annotation("Port to listen on", abbrev="p", kind="option", type=int),
)
def main(
    directory: Path = Path("./recordings"),
    port: int = RECORDING_RECEIVER_DEFAULT_PORT,
) -> None:
    """Run a standalone recording receiver."""
    RecordingReceiver(directory).serve(port=port)


if __name__ == "__main__":
    plac.call(main)
