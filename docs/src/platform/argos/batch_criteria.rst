.. _ln-platform-argos-bc:

==============
Batch Criteria
==============

The following :term:`Batch Criteria` are defined which can be used with any
:term:`Project` in TITERRA (in addition to the general SIERRA batch criteria).

- :ref:`ln-platform-argos-bc-saa-noise`

.. _ln-platform-argos-bc-saa-noise:

Sensor and Actuator Noise
=========================

Inject sensor and/or actuator noise into the swarm.

Cmdline Syntax
--------------

``saa_noise.{category}.C{cardinality}[.Z{population}]``

- ``category`` - [sensors,actuators,all]

  - ``sensors`` - Apply noise to robot sensors only. The ``sensors`` dictionary
    must be present and non-empty in the ``main.yaml``.

  - ``actuators`` - Apply noise to robot actuators only. The ``actuators``
    dictionary must be present and non-empty in ``main.yaml``.

  - ``all`` - Apply noise to robot sensors AND actuators. [ ``sensors``,
    ``actuators`` ] dictionaries both optional in ``main.yaml``.

- ``cardinality`` - The # of different noise levels to test with between the min
  and max specified in the config file for each sensor/actuator which defines
  the cardinality of the batch experiment.

- ``population`` - The static swarm size to use (optional).

Examples
--------

- ``saa_noise.sensors.C4.Z16``: 4 levels of noise applied to all sensors in a
  swarm of size 16.

- ``saa_noise.actuators.C3.Z32``: 3 levels of noise applied to all actuators in
  a swarm of size 32.

- ``saa_noise.all.C10``: 10 levels of noise applied to both sensors and
  actuators; swarm size not modified.

The values for the min, max noise levels for each sensor which are used along
with ``cardinality`` to define the set of noise ranges to test are set via the
main YAML configuration file (not an easy way to specify ranges in a single
batch criteria definition string). The relevant section is shown below. If the
min, max level for a sensor/actuator is not specified in the YAML file, no XML
changes will be generated for it.

.. IMPORTANT::

   In order to use this batch criteria, you **MUST** have the version of ARGoS
   from `Swarm Robotics Research <https://github.com/swarm-robotics/argos3.git>`_.
   The version accessible on the ARGoS website does not have a consistent noise
   injection interface, making usage with this criteria impossible.

The following sensors can be affected (dependent on your chosen robot's
capabilities in ARGoS):

- light
- proximity
- ground
- steering
- position

The following actuators can be affected (dependent on your chosen robot's
capabilities in ARGoS):

- steering

.. _ln-platform-argos-bc-saa-noise-yaml-config:

YAML Config
-----------

For all sensors and actuators to which noise should be applied, the noise model
and dependent parameters must be specified (i.e. if a given sensor or sensor is
present in the config, all config items for it are mandatory).

The appropriate ``ticks_range`` attribute is required, as there is no way to
calculate in general what the correct range of X values for generated graphs
should be, because some sensors/actuators may have different
assumptions/requirements about noise application than others. For example, the
differential steering actuator ``noise_factor`` has a default value of 1.0
rather than 0.0, due to its implementation model in ARGoS, so the same range of
noise applied to it and, say, the ground sensor, will have different XML changes
generated, and so you can't just average the ranges for all sensors/actuators to
compute what the ticks should be for a given experiment.

.. code-block:: YAML

   perf:
     ...
     robustness:
       # For ``uniform`` models, the ``uniform_ticks_range`` attributes are
       # required.
       uniform_ticks_range: [0.0, 0.1]

       # For ``gaussian`` models, the ``gaussian_ticks_stddev_range`` and
       # ``gaussian_ticks_mean_range`` attributes are required.
       gaussian_ticks_mean_range: [0.0, 0.1]
       gaussian_ticks_stddev_range: [0.0, 0.0]

       # For ``gaussian`` models, the ``gaussian_labels_show``,
       # ``gaussian_ticks_src`` attributes are required, and control what is
       # shown for the xticks/xlabels: the mean or stddev values.
       gaussian_ticks_src: stddev
       gaussian_labels_show: stddev

       # The sensors to inject noise into. All shown sensors are optional. If
       # omitted, they will not be affected by noise injection.
       sensors:
         light:
           model: uniform

           # For a ``uniform`` model, the ``range`` attribute is required, and
           # defines the -[level, level] distribution that injected noise will
           # be drawn from.
           range: [0.0, 0.4]

         proximity:
           model: gaussian
           stddev_range: [0.0, 0.1]
           mean_range: [0.0, 0.0]
         ground:
           model: gaussian
           stddev_range: [0.0, 0.1]
           mean_range: [0.0, 0.0]
         steering: # applied to [vel_noise, dist_noise]
           model: uniform
           range: [0.0, 0.1]
         position:
           model: uniform
           range: [0.0, 0.1]

         # The actuators to inject noise into. All shown actuators are
         # optional. If omitted, they will not be affected by noise injection.
         actuators:
           steering: # applied to [noise_factor]
             model: uniform
             range: [0.95, 1.05]

Uniform Noise Injection Examples
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``range: [0.0,0.1]`` with ``cardinality=1`` will result in two experiments
  with uniform noise distributions of ``[0.0, 0.0]``, and ``[-0.1, 0.1]``.

Gaussian Noise Injection Examples
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``stddev_range: [0.0,1.0]`` and ``mean_range: [0.0, 0.0]`` with
  ``cardinality=2`` will result in two experiments with Guassian noise
  distributions of ``Gaussian(0,0)``, ``Gaussian(0, 0.5)``, and ``Gaussian(0,
  1.0)``.

Experiment Definitions
----------------------

- exp0 - Ideal conditions, in which noise will be applied to the specified
  sensors and/or actuators at the lower bound of the specified ranges for each.

- exp1-expN - Increasing levels of noise, using the cardinality specified on the
  command line and the distribution type specified in YAML configuration.
