**************
Batch Criteria
**************

- :ref:`Block Density <ln-bc-block-density>`
- :ref:`Swarm Population Dynamics <ln-bc-population-dynamics>`
- :ref:`Block Quantity <ln-bc-block-quantity>`
- :ref:`Block Motion Dynamics <ln-bc-block-motion-dynamics>`
- :ref:`Oracle <ln-bc-oracle>`
- :ref:`Task Allocation Policy <ln-bc-ta-policy-set>`
- :ref:`Temporal Variance <ln-bc-tv>`

.. _ln-bc-population-dynamics:

Swarm Population Dynamics
=========================

Cmdline Syntax
--------------

::

   population_dynamics.C{cardinality}.F{Factor}[.{dynamics_type}{prob}[...]]

- ``cardinality`` - The # of different values of each of the specified dynamics
  types to to test with (starting with the one on the cmdline). This defines the
  cardinality of the batched experiment.

- ``Factor`` - The factor by which the starting value of all dynamics types
  specified on the cmdline are increased for each each experiment (i.e., value
  in last experiment in batch will be ``<start value> + cardinality``; a linear
  increase).

- ``dynamics_type`` - [B,D,M,R]

  - ``B`` - Adds birth dynamics to the population. Has no effect by itself, as
    it specifies a pure birth process with :math:`\lambda=\infty`,
    :math:`\mu_{b}`=``prob`` (a queue with an infinite # of robots in it which
    robots periodically leave from), resulting in dynamic swarm sizes which will
    increase from N...N over time. Can be specified with along with ``D|M|R``,
    in which case swarm sizes will increase according to the birth rate up until
    N, given N robots at the start of simulation.

  - ``D`` - Adds death dynamics to the population. By itself, it specifies a
    pure death process with :math:`\lambda_{d}=prob`, and :math:`\mu_{d}=\infty`
    (a queue which robots enter but never leave), resulting in dynamic swarm
    sizes which will decrease from N...1 over time. Can be specified along with
    ``B|M|R``.

  - ``M|R`` - Adds malfunction/repair dynamics to the population. If ``M``
    dynamics specified, ``R`` dynamics must also be specified, and vice
    versa. Together they specify the dynamics of the swarm as robots temporarily
    fail, and removed from simulation, and then later are re-introduced after
    they have been repaired (a queue with :math:`\lambda_{m}` arrival rate and
    :math:`\mu_{r}` repair rate). Can be specified along with ``B|D``.


.. IMPORTANT:: The specified :math:`\lambda` or :math:`\mu` are the rate
   parameters of the exponential distribution used to distribute the event times
   of the Poisson process governing swarm sizes, *NOT* Poisson process
   parameter, which is their mean; e.g., :math:`\lambda=\frac{1}{\lambda_{d}}`
   for death dynamics.

Examples:
    - ``population_dynamics.C10.F2p0.B0p001``: 10 levels of population
      variability applied using a pure birth process with a 0.001 parameter,
      which will be linearly varied in [0.001,0.001*2.0*10]. For all
      experiments, the initial swarm is not controlled directly; the value in
      template input file will be used if swarm size is not set by another
      variable.

    - ``population_dynamics.C4.F3p0.D0p001``: 4 levels of population variability
      applied using a pure death process with a 0.001 parameter, which will be
      linearly varied in [0.001,0.001*3.0*4]. For all experiments, the initial
      swarm size is not controlled directly; the value in template input file
      will be used if swarm size is not set by another variable.

    - ``population_dynamics.C8.F4p0.B0p001.D0p005``: 8 levels of population
      variability applied using a birth-death process with a 0.001 parameter for
      birth and a 0.005 parameter for death, which will be linearly varied in
      [0.001,0.001*4.0*8] and [0.005, 0.005*4.0*8] respectively. For all
      experiments, the initial swarm is not controlled directly; the value in
      the template input file will be used if swarm size is is not set by
      another variable.

    - ``population_dynamics.C2.F1p5.M0p001.R0p005``: 2 levels of population
      variability applied using a malfunction-repair process with a 0.001
      parameter for malfunction and a 0.005 parameter for repair which will be
      linearly varied in [0.001, 0.001*1.5*2] and [0.005, 0.005*1.5*2]
      respectively. For all experiments, the initial swarm size is not
      controlled directly; the value in the template input file will be used if
      swarm size is not set by another variable.


.. _ln-bc-block-quantity:

Block Quantity
==============

.. _ln-bc-block-quantity-cmdline:

Cmdline Syntax
--------------
::

   block_quantity.{block_type}.{increment_type}{N}

- ``block_type`` - ``cube`` or ``ramp``, depending on what type of blocks you
  want to control the count of.

- ``increment_type`` - {Log,Linear}. If ``Log``, then swarm sizes for each
  experiment are distributed 1...N by powers of 2. If ``Linear`` then block
  counts for each experiment are distributed linearly between 1...N, split evenly
  into 10 different sizes.

- ``N`` - The maximum block count.

Examples:
    - ``block_quantity.cube.Log1024``: Cube block counts 1...1024

    - ``block_quantity.ramp.Linear1000``: Ramp block counts 100...1000


.. _ln-bc-block-density:

Block Density
=============

Cmdline Syntax
--------------

::

   block_density.CD{density}.I{Arena Size Increment}.C{cardinality}

- ``density`` - <integer>p<integer> (i.e. 5p0 for 5.0)

- ``Arena Size Increment`` - Size in meters that the X and Y dimensions should
    increase by in between experiments. Larger values here will result in larger
    arenas and more blocks. Must be an integer.

- ``cardinality`` How many experiments should be generated?

Examples:
    - ``block_density.CD1p0.I16.C4``: Constant density of 1.0. Arena dimensions
      will increase by 16 in both X and Y for each experiment in the batch (4
      total).

.. _ln-bc-block-motion-dynamics:

Block Motion Dynamics
=====================

Cmdline Syntax
--------------

::

   block_motion_dynamics.C{cardinality}.F{Factor}.{dynamics_type}{prob}

- ``cardinality`` - The # of different values of each of the specified dynamics
  types to to test with (starting with the one on the cmdline). This defines the
  cardinality of the batched experiment.

- ``Factor`` - The factor by which the starting value of all dynamics types
  specified on the cmdline are increased for each each experiment (i.e., value
  in last experiment in batch will be ``<start value> + cardinality``; a linear
  increase).

- ``dynamics_type`` - [RW]

  - ``RW`` - Adds random walk dynamics to the arena. Free blocks will execute a
    random walk with a specified probability each timestep.


Examples:
    - ``block_motion_dynamics.C10.F2p0.RW0p001``: 10 levels of block motion
      variability applied using a random walk with a 0.001 probability for each
      block each timestep, which will be linearly varied in
      [0.001,0.001*2.0*10]. For all experiments, the initial swarm is not
      controlled directly; the value in template input file will be used if
      swarm size is not set by another variable.

.. _ln-bc-oracle:

Oracle
======

.. _ln-bc-oracle-cmdline:

Cmdline Syntax
--------------

::

   oracle.{oracle_name}[.Z{population}]

- ``oracle_name`` - {entities, tasks}

  - ``entities`` - Inject perfect information about locations about entities in
    the arena, such as blocks and caches.
  - ``tasks`` - Inject perfect information about task execution and interface
    times.

- ``population`` - Static size of the swarm to use (optional).

Examples:

- ``oracle.entities.Z16`` - All permutations of oracular information about
  entities in the arena, run with swarms of size 16.

- ``oracle.tasks.Z8`` - All permutations of oracular information about tasks in
  the arena, run with swarms of size 8.

- ``oracle.entities`` - All permuntations of oracular information of entities in
  the arena (swarm size is not modified).

.. _ln-bc-ta-policy-set:

Task Allocation Policy
======================

Cmdline Syntax
--------------
``ta_policy_set.all[.Z{population}]``

``population`` - The swarm size to use (optional)

Examples:

- ``ta_policy_set.all.Z16``: All possible task allocation policies with swarms
  of size 16.

- ``ta_policy_set.all``: All possible task allocation policies; swarm size not
  modified.

.. _ln-bc-tv:

Temporal Variance
-----------------

Injecting waveforms into the swarm's environment which affect the individual
robot behavior to simulate changing outdoor conditions, changing object
sizes/weights, etc.


.. NOTE::

   The graphs generated from this criteria exclude exp0.

.. WARNING::

   Some of the temporal variance config is very FORDYCA specific; hopefully this
   will change in the future, or be pushed down to a project-specific extension
   of a base flexibility class.

.. _ln-bc-tv-cmdline:

Cmdline Syntax
^^^^^^^^^^^^^^

``temporal_variance.{variance_type}{waveform_type}[step_time][.Z{population}]``

- ``variance_type`` - [BC,BM,M].

  - ``BC`` - Apply motion throttling to robot speed when it is carrying a
    block according to the specified waveform.

  - ``BM`` - Apply the specified waveform when calculating robot block
    manipulation penalties (pickup, drop, etc.).

  - ``M`` - Apply the specified waveform to robot motion unconditionally.

- ``waveform_type`` - {Sine,Square,Sawtooth,Step{U,D},Constant}.

- ``step_time`` - Timestep the step function should switch (optional).

- ``population`` - The static swarm size to use (optional).

Examples:

- ``temporal_variance.BCSine.Z16`` - Block carry sinusoidal variance in a swarm
  of size 16.

- ``temporal_variance.BCStep50000.Z32`` - Block carry step variance switch at
  50000 timesteps in a swarm of size 32.

- ``temporal_variance.BCStep50000`` - Block carry step variance switching at
  50000 timesteps; swarm size not modified.

The frequency, amplitude, offset, and phase of the waveforms is set via the
``main.yaml`` configuration file for a project (not an easy way to specify
ranges in a single batch criteria definition string). The relevant section is
shown below.

For the {Sine,Square,Sawtooth} waveforms, the cardinality of the batched
experiment is determined by: (Size of Hz list -1) * (Size of BC_amp/BM_amp
list - 1).

.. _ln-bc-tv-yaml-config:

YAML Config
^^^^^^^^^^^

.. code-block:: YAML

   perf:
     ...
     flexibility:
       # The range of Hz to use for generated waveforms. Applies to Sine,
       # Sawtooth, Square waves. There is no limit for the length of the list.
       hz:
         - frequency1
         - frequency2
         - frequency3
         - ...
       # The range of block manipulation penalties to use if that is the type of
       # applied temporal variance (BM). Specified in timesteps. There is no
       # limit for the length of the list.
       BM_amp:
         - penalty1
         - penalty2
         - penalty3
         - ...
      # The range of block carry penalties to use if that is the type of applied
      # temporal variance (BC). Specified as percent slowdown: [0.0, 1.0]. There
      #is no limit for the length of the list.
      BC_amp:
         - percent1
         - percent2
         - percent3
         - ...

      # The range of motion throttle penalties to use if that is the type of
      # applied temporal variance (M). Specified as percent slowdown: [0.0,
      # 1.0]. There is no limit for the length of the list.
      M_amp:
         - percent1
         - percent2
         - percent3
         - ...

Experiment Definitions
^^^^^^^^^^^^^^^^^^^^^^

- exp0 - Ideal conditions, which is a ``Constant`` waveform with amplitude
  ``BC_amp[0]``, ``BM_amp[0]``, ``M_amp[0]`` depending.

- exp1-expN

  - Cardinality of ``|hz|`` * ``|BM_amp|`` if the variance type is ``BM`` and
    the waveform type is Sine, Square, or Sawtooth.

  - Cardinality of ``|hz|`` * ``|BC_amp|`` if the variance type is ``BC`` and
    the waveform type is Sine, Square, or Sawtooth.

  - Cardinality of ``|hz|`` * ``|M_amp|`` if the variance type is ``M`` and
    the waveform type is Sine, Square, or Sawtooth.

  - Cardinality of ``|BM_amp|`` if the variance type is ``BM`` and the waveform
    type is StepU, StepD.

  - Cardinality of ``|BC_amp|`` if the variance type is ``BC`` and the waveform
    type is StepU, StepD.

  - Cardinality of ``|M_amp|`` if the variance type is ``M`` and the waveform
    type is StepU, StepD.
