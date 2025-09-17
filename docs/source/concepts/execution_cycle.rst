.. execution_cycle:

Concept: Execution Cycle
========================

Overview
--------
The TCode execution cycle consists of 4 operations: 

**1. Validation**
  Your TCode is checked for syntax errors (ex. bad units) and state error (ex. trying to pick up pipette tips when you haven't picked up a pipette).
**2. Simulation**
  Your TCode is simulated to obtain the next state that will be used in **Validation** of the next command.
**3. Resolution**
  If your TCode command adds an abstract entity to your script (ex. ``ADD_TOOL``), the entity is resolved to a physical entity in your fleet (ex. a specific pipette on a specific Trilobot).
**4. Execution**
  The command is executed on the Trilobot.

When a TCode script is run, these operations are performed in the following order:

 * Each command is scheduled, which first validates, the command, then simulates it, then resolves it. If these three operations are successful, the command is added to a queue of commands to be executed.
 * Once the fleet is activated, each command on the queue is sequentially executed until the schedule is empty, or the fleet is paused.

The following sections cover each of the operations in more detail.

Validation
----------

Validation checks your TCode for syntax errors and state errors. There are many ways to command your Trilobot to do something that is not possible, and the validation step is intended to catch these errors as quickly as possible. Errors typically break down into two categories:

* Bad syntax: The TCode command that you are trying to schedule has bad information in it. Maybe, in your ``ASPIRATE`` command, you provided a volume with units of ``meters`` instead of ``microliters``. This is a syntax error, and the validation step will catch it.

* Bad state: After each command is validated, it is then simulated (see next section). The simulation step produces a new state that is used to validate the next command. If the next command is not valid in that state, then it will be caught in the validation step.

Let's look at the ``ASPIRATE`` command. There are many "valid" ``ASPIRATE`` commands that we don't want to run, and detecting them requires some knowledge of state. Some examples are:

  * A large ``ASPIRATE`` command that specifies a volume larger than the target pipette's maximum volume
  * A small ``ASPIRATE`` command that causes the pipette to over-aspirate due to previous ``ASPIRATE`` commands
  * Any ``ASPIRATE`` command run on a robot that hasn't picked up a pipette or a pipette tip.

Simulation
----------

The simulation step maintains a simplified model of the fleet's state that updates as commands are scheduled. No collision detection, path planning, or other complex calculations are performed during simulation. The goal of the simulation step is to maintain a model of the fleet's state that is "good enough" to validate the next command.

Resolution
----------

The resolution step matches entity descriptions in the TCode commands to physical entites in your fleet. There are four primary types of entities that can be resolved:

* Robots (``ADD_ROBOT``)
* Tools (``ADD_TOOL``)
* Labware (``ADD_LABWARE``)
* PIPETTE_TIP_GROUPS (``ADD_PIPETTE_TIP_GROUP``)

When you add one of these entities to your TCode script, you provide a description of the entity that you want to add. The resolution step matches that description to a physical entity in your fleet. If a matching entity is found, that entity is registered to the ID provided in the command. If the resolution fails, the error message will give some indication as to why it failed (see Error Handling).

Execution
---------

The final step of any protocol is execution. Once a command has been validated, simulated, and resolved, it is added to a queue of commands to be executed. When the fleet is activated, each command on the queue is sequentially executed until the schedule is empty, or the fleet is paused.

The errors resulting from execution are typically real-world errors, such as unexpected collisions, estops being pressed, or other unexpected situations. See Error Handling for more information.
