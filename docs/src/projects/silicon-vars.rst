.. _ln-silicon-vars:

=================
SILICON Variables
=================

- :ref:`Construct Targets <ln-silicon-var-construct-targets>`

.. _ln-silicon-var-construct-targets:

Construction Targets
====================

Construction target classes for defining the volumetric extent of one or more
structures to be built during simulation.

Cmdline Syntax
--------------

::

   construct_targets.{class}.{AxBxC}@{D,E}

- ``class``

  - ``rectprism`` - A rectangular prism defined by the bounding box ``AxBxC``
    with an anchor (lower left corner) at ``D,E``.

  - ``ramp`` - A sloped structure that robots can drive up, defined by the
    bounding box ``AxBxC`` with an anchor (lower left corner) at ``D,E``.


Examples:
    - ``construct_targets.ramp.8x8x4@4,4``: A square ramp structure 4 units tall
      anchored on its lower left corner at 4,4.
