Tutorial: Camera Control over Webhooks
======================================

**Goal**: Drive the robot's cameras from a T-code script with ``SEND_WEBHOOK``.

Background
----------

A Trilobot carries two camera systems, both HTTP services on the robot network:

- **Frame cameras** — the USB cameras on the robot frame (``CAM_POS_X`` and
  ``CAM_NEG_X``), served by the trilo-cam service on the robot at port ``8095``.
- **Arm camera** — the WiFi camera node on the arm (canmera), serving its API on
  port ``8081`` once it is on the network.

T-code has no per-action camera commands: camera work is scripted with the generic
``SEND_WEBHOOK`` command.

How ``SEND_WEBHOOK`` reaches a camera
-------------------------------------

``SEND_WEBHOOK`` sends one HTTP ``POST`` to ``url``. The optional ``payload`` is a
string holding one JSON object; both camera services unpack it and read your
parameters from it, so a webhook call behaves exactly like a native API call.

.. code-block:: python

   import json
   import tcode_api.api as tc

   command = tc.SEND_WEBHOOK(
       pause_execution=False,
       url="http://trilobot-a.local:8095/api/v1/cameras/CAM_POS_X/recording/start",
       payload=json.dumps({"max_duration_s": 600, "label": "assay-42"}),
   )

Things to know:

- **POST only.** Endpoints with other verbs (e.g. trilo-cam's ``PUT .../settings``)
  or whose *response* is the point (status, media listings, downloads) are not
  usable from a script; use the camera's console or plain HTTP for those.
- **Responses are discarded.** A webhook triggers a side effect; nothing comes
  back into the script.
- **Check your failure handling.** With ``pause_execution=True`` a failed call
  fails the command — and a successful one *pauses* the run until resumed, so
  reserve it for wait-for-operator flows. With ``pause_execution=False`` the
  script keeps running regardless of the call's outcome; as of this writing the
  executor does not act on ``ignore_external_error``, so don't rely on that flag
  to surface camera errors.

Exploring the APIs
------------------

Both camera services are FastAPI apps and serve their own interactive API
reference (Swagger UI) at ``/docs`` — ``http://<robot-host>:8095/docs`` for the
frame cameras, ``http://<canmera-ip>:8081/docs`` for the arm camera — covering
every endpoint, including the ones a webhook can't reach. Each also serves a
browser console at ``/console`` for controlling the cameras interactively
(live view, captures, recordings, settings).

Frame cameras (trilo-cam, port 8095)
------------------------------------

Base URL: ``http://<robot-host>:8095/api/v1``; cameras are addressed by name.

.. list-table::
   :header-rows: 1
   :widths: 55 45

   * - Action (``POST``)
     - Payload (JSON object)
   * - ``/cameras/{name}/on``
     - —
   * - ``/cameras/{name}/off``
     - —
   * - ``/cameras/{name}/picture``
     - ``{"label": "..."}`` (optional)
   * - ``/cameras/{name}/recording/start``
     - ``{"max_duration_s": 600, "label": "..."}`` (both optional)
   * - ``/cameras/{name}/recording/stop``
     - —
   * - ``/cameras/{name}/remote-recording/start``
     - ``{"url": "<receiver>", "max_duration_s": 600}``
   * - ``/cameras/{name}/remote-recording/stop``
     - —

A ``label`` is recorded into the media filename on the robot and is filterable
later through the media API and console.

.. note::

   Enabling a camera returns before its stream is publishing, and captures are
   rejected until it is. Put a few seconds of ``WAIT`` between ``/on`` and the
   first capture.

Example — enable a camera, take a labeled still, then film a stretch of the run
(``robot_id`` comes from your ``ADD_ROBOT`` command, as in
:doc:`connect_to_fleet`):

.. code-block:: python

   import json
   import tcode_api.api as tc
   from tcode_api.utilities import s

   CAM = "http://trilobot-a.local:8095/api/v1/cameras/CAM_POS_X"

   def cam_webhook(path: str, **params: object) -> tc.SEND_WEBHOOK:
       return tc.SEND_WEBHOOK(
           pause_execution=False,
           url=f"{CAM}{path}",
           payload=json.dumps(params) if params else None,
       )

   commands += [
       cam_webhook("/on"),
       tc.WAIT(robot_id=robot_id, duration=s(8)),
       cam_webhook("/picture", label="before"),
       cam_webhook("/recording/start", max_duration_s=600, label="assay-42"),
       # ... the protocol steps to film ...
       cam_webhook("/recording/stop"),
   ]

Arm camera (canmera, port 8081)
-------------------------------

The arm camera must already be on WiFi; joining it to the network and learning
its address is part of robot deployment. Base URL: ``http://<canmera-ip>:8081``.

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Action (``POST``)
     - Payload (JSON object)
   * - ``/api/still``
     - —
   * - ``/api/control``
     - ``{"control": "exposure" | "gain" | "resolution", "value": 150}``
   * - ``/api/recording/start``
     - ``{"mode": "stream" | "camera" | "auto", "max_duration_s": 60}`` (both optional)
   * - ``/api/recording/stop``
     - —
   * - ``/api/stream/start``
     - —
   * - ``/api/stream/stop``
     - —

Captures stay on the node (oldest are pruned when storage runs low); fetch them
from ``http://<canmera-ip>:8081/`` or the node's console.

.. note::

   Parameterized calls (``/api/control``, custom recording modes/durations) need a
   canmera build that unwraps the webhook envelope
   (`trilobio/canmera#12 <https://github.com/trilobio/canmera/pull/12>`_); earlier
   builds only handle parameterless webhooks.

Example — bump the gain, then take a still:

.. code-block:: python

   commands += [
       tc.SEND_WEBHOOK(
           pause_execution=False,
           url="http://192.168.0.42:8081/api/control",
           payload=json.dumps({"control": "gain", "value": 150}),
       ),
       tc.SEND_WEBHOOK(
           pause_execution=False,
           url="http://192.168.0.42:8081/api/still",
       ),
   ]

Scheduling and running these commands works like any other script — see the
example scripts in the repository's ``scripts/`` directory.
