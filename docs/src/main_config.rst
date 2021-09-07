.. _ln-main-config:

========================
Additional Configuration
========================

TITERRA defines some additional configuration options besides those
available/required by SIERRA, as shown below.

Summary Performance Measures Configuration File
===============================================

Within the pointed-to .yaml file for ``perf`` configuration, the structure is:

.. code-block:: YAML

   perf:

     # The ``.csv`` file under ``sim_metrics_leaf`` for each experiment
     # which contains the applied environmental variances.
     tv_environment_csv: 'tv-environment.csv'

     # The ``.csv``file under ``sim_metrics_leaf`` for each experiment which
     # contains information about temporally fluctuating populations.
     tv_population_csv: 'tv-population.csv'

``perf.robustness`` sub-dictionary
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

See :ref:`SAA noise config <ln-bc-saa-noise-yaml-config>`.
