**************
Batch Criteria
**************

- :ref:`Construction Target Specifications <ln-prism-bc-ct-specs>`

.. _ln-prism-bc-ct-specs:

Construction Target Specifications
==================================

Define a construction target to be built during simulation. Multiple targets can
be specified.

Cmdline Syntax
--------------

::

   ct_specs.{class}.{AxBxC}@{D,E,F}

- ``class``

  - ``rectprism`` - A rectangular prism defined by the bounding box ``AxBxC``
    with an anchor (lower left corner) at ``(D,E,F)``.

  - ``ramp`` - A sloped structure that robots can drive up, defined by the
    bounding box ``AxBxC`` with an anchor (lower left corner) at ``(D,E,F)``.


Examples:
    - ``ct_specs.ramp.8x8x4@4,4,0``: A square ramp structure 4 units tall anchored
      on its lower left corner at (4,4,0).
