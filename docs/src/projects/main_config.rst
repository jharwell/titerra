.. _ln-main-config:

=============================
Main Configuration Extensions
=============================

Summary Performance Measures
============================

Within the pointed-to .yaml file for ``perf`` configuration, the structure is:

.. code-block:: YAML

   perf:

     # The title that graphs of raw swarm performance should have (cannot be
     # known a priori for all possible projects during stage 4). This key is
     # required for all batch criteria which for which 'raw' performance graphs
     # should be generated.
     raw_perf_title: 'Swarm Blocks Collected'

     # The Y label for graphs of raw swarm performance (cannot be known a
     # priori for all possible projects during stage 4). This key is required
     # for all batch criteria for which 'raw' performance graphs should be
     # generated.
     raw_perf_ylabel: '\# Blocks'

     # The name of the collated ``.csv`` containing overall performance measures
     # for each experiment in the batch (1 per experiment) which should be used
     # for generating performance measures. This key is mandatory.
     inter_perf_csv: 'blocks-transported-cum.csv'

     # The name of the collated ``.csv`` containing the count of the average #
     # of robots experiencing inter-robot interference for each experiment in
     # the batch (1 per experiment) which is used in generating performance
     # measures. Mandatory for all batch criteria for which 'self-organization'
     # performance graphs should be generated.
     interference_count_csv: 'interference-in-cum-avg.csv'

     # The name of the collated ``.csv`` containing the count of the average
     # duration of a robot experiencing inter-robot interference for each
     # experiment in the # batch (1 per experiment) which should be used for
     # generating performance measures. Mandatory for all batch criteria for
     # which 'self-organization' graphs should be generated.
     interference_duration_csv: 'interference-duration-cum-avg.csv'

     # The ``.csv`` file under ``sim_metrics_leaf`` for each experiment
     # which contains the applied environmental variances. This key is
     # required for all batch criteria which for which 'flexibility' performance
     # graphs should be generated.
     tv_environment_csv: 'tv-environment.csv'

     # The ``.csv``file under ``sim_metrics_leaf`` for each experiment which
     # contains information about temporally fluctuating populations. This key is
     # required for all batch criteria which for which 'flexibility' performance
     # graphs should be generated.
     tv_population_csv: 'tv-population.csv'

``perf.robustness`` sub-dictionary
==================================

See :ref:`SAA noise config <ln-platform-argos-bc-saa-noise-yaml-config>`.
