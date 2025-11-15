TCode Integrator API
====================

The TCode integrator is the other side of :class:`tcode_api.commands.SEND_WEBHOOK`. Here
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


The TCode used to trigger this action is

.. code::

    script.commands.append(
        tc.SEND_WEBHOOK(pause_execution=True, url="http://localhost:8092", payload="open_lid")
    )


API Reference
-------------

.. autoclass:: tcode_api.servicer.integrator.TCodeIntegratorBase
    :members:

.. autoclass:: tcode_api.servicer.integrator.WebHookBody

