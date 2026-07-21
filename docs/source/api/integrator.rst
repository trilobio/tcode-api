T-code Integrator API
=====================

The T-code integrator is the other side of :class:`tcode_api.commands.SEND_WEBHOOK`. Here
is an example integration with ATC Thermocycler. The :code:`ATCThermoCycler` class came from
`pylabrobot`_.

.. _pylabrobot: https://github.com/PyLabRobot/pylabrobot/blob/main/pylabrobot/thermocycling/thermo_fisher/atc.py

.. code::

    from tcode_api.servicer.integrator import TCodeIntegratorBase, WebHookBody

    class ATCIntegrator(TCodeIntegratorBase):
        async def perform_action(self, data: WebHookBody):
            thermal_cycler = ATCThermoCycler("192.168.8.129")
            await thermal_cycler.setup()

            if data.payload == "open_lid":
                await thermal_cycler.open_lid()
            elif data.payload == "close_lid":
                await thermal_cycler.close_lid()

            await thermal_cycler.stop()

            if data.is_execution_paused:
                self.resume_tcode()


    integrator = ATCIntegrator()
    integrator.serve()


The T-code used to trigger this action is

.. code::

    script.commands.append(
        tc.SEND_WEBHOOK(pause_execution=True, url="http://localhost:8092", payload="open_lid")
    )


Recording receiver
------------------

Robot cameras (trilo-cam) can stream a recording to a network target instead of
the robot's limited local storage. The recording receiver is the other side of
that: it accepts the streamed MP4 over HTTP and writes it to disk on the fleet
controller. Run it standalone:

.. code::

    python -m tcode_api.servicer.recording_receiver --directory ./recordings --port 8096

then start a remote recording pointing at it, e.g. via
:class:`tcode_api.commands.SEND_WEBHOOK` with url
``http://<rcm>:8095/api/v1/cameras/CAM_POS_X/remote-recording/start`` and payload

.. code::

    {"url": "http://<fleet-controller>:8096/robot1/CAM_POS_X.mp4", "max_duration_s": 600}

The request path selects the file under the receiver's directory; existing
files are never overwritten.

API Reference
-------------

.. autoclass:: tcode_api.servicer.integrator.TCodeIntegratorBase
    :members:

.. autoclass:: tcode_api.servicer.integrator.WebHookBody

.. autoclass:: tcode_api.servicer.recording_receiver.RecordingReceiver
    :members:

