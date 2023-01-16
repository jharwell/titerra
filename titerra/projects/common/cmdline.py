# Copyright 2021 John Harwell, All rights reserved.
#
#  SPDX-License-Identifier: MIT
#
"""
Command line parsing and validation for the :xref:`TITAN` project.
"""

# Core packages
import typing as tp
import argparse

# 3rd party packages
from sierra.core import types
import sierra.core.cmdline as cmd

# Project packages


class CommonCmdline(cmd.CoreCmdline):
    """
    Defines TITAN extensions to the core command line arguments defined in
    :class:`~sierra.core.cmdline.CoreCmdline`.
    """

    def init_stage4(self):
        super().init_stage4()

        # Performance measure calculation options
        pm = self.parser.add_argument_group(
            'Stage4: Summary Performance Measure Options')

        pm.add_argument("--pm-scalability-from-exp0",
                        help="""

                        If passed, then swarm scalability will be calculated
                        based on the "speedup" achieved by a swarm of size N in
                        exp X relative to the performance in exp 0, as opposed
                        to the performance in exp X-1 (default).

                        """ + self.stage_usage_doc([4]),
                        action='store_true')

        pm.add_argument("--pm-scalability-normalize",
                        help="""

                        If passed, then swarm scalability will be normalized
                        into [-1,1] via ``--pm-normalize-method``, as opposed to
                        raw values (default). This may make graphs more or less
                        readable/interpretable.

                        """ + self.stage_usage_doc([4]),
                        action='store_true')

        pm.add_argument("--pm-self-org-normalize",
                        help="""

                        If passed, then swarm self-organization calculations
                        will be normalized into [-1,1] via
                        ``--pm-normalize-method``, as opposed to raw values
                        (default). This may make graphs more or less
                        readable/interpretable.

                        """,
                        action='store_true')

        pm.add_argument("--pm-flexibility-normalize",
                        help="""

                        If passed, then swarm flexibility calculations will be
                        normalized into [-1,1] via ``--pm-normalize-method``, as
                        opposed to raw values (default), and HIGHER values will
                        be better. This may make graphs more or less
                        readable/interpretable; without normalization, LOWER
                        values are better.

                       """ + self.stage_usage_doc([4]),
                        action='store_true')

        pm.add_argument("--pm-robustness-normalize",
                        help="""

                        If passed, then swarm robustness calculations will be
                        normalized into [-1,1] via ``--pm-normalize-method``, as
                        opposed to raw values (default). This may make graphs
                        more or less readable/interpretable.

                        """ + self.stage_usage_doc([4]),
                        action='store_true')

        pm.add_argument("--pm-all-normalize",
                        help="""

                        If passed, then swarm scalability, self-organization,
                        flexibility, and robustness calculations will be
                        normalized into [-1,1] via ``--pm-normalize-method``, as
                        opposed to raw values (default). This may make graphs
                        more or less readable/interpretable.

                        """ + self.stage_usage_doc([4]),
                        action='store_true')

        pm.add_argument("--pm-normalize-method",
                        choices=['sigmoid'],
                        help="""

                        The method to use for normalizing performance measure
                        results, where enabled:

                        - ``sigmoid`` - Use a pair of sigmoids to normalize the
                          results into [-1, 1]. Can be used with all performance
                          measures.

                        """ + self.stage_usage_doc([4]),
                        default='sigmoid')

        # Variance curve similarity options
        vcs = self.parser.add_argument_group(
            'Stage4: Variance Curve Similarity (VCS) Options')

        vcs.add_argument("--gen-vc-plots",
                         help="""

                          Generate plots of ideal vs. observed swarm
                          [reactivity, adaptability] for each experiment in the
                          batch.""" +
                         self.bc_applicable_doc([':ref:`Temporal Variance <ln-bc-tv>`']) +
                         self.stage_usage_doc([4]),
                         action="store_true")

        vcs.add_argument("--rperf-cs-method",
                         help="""

                         Raw Performance curve similarity method. Specify the
                         method to use to calculate the similarity between raw
                         performance curves from non-ideal conditions and ideal
                         conditions (exp0). """ +
                         self.cs_methods_doc() +
                         self.bc_applicable_doc([':ref:`SAA Noise <ln-bc-saa-noise>`']) +
                         self.stage_usage_doc([4]),
                         choices=["pcm", "area_between",
                                  "frechet", "dtw", "curve_length"],
                         default="dtw")
        vcs.add_argument("--envc-cs-method",
                         help="""

                         Environmental conditions curve similarity
                         method. Specify the method to use to calculate the
                         similarity between curves of applied variance
                         (non-ideal conditions) and ideal conditions (exp0). """ +
                         self.cs_methods_doc() +
                         self.bc_applicable_doc([':ref:`Temporal Variance <ln-bc-tv>`']) +
                         self.stage_usage_doc([4]),
                         choices=["pcm", "area_between",
                                  "frechet", "dtw", "curve_length"],
                         default="dtw")

        vcs.add_argument("--reactivity-cs-method",
                         help="""

                         Reactivity calculatation curve similarity
                         method. Specify the method to use to calculate the
                         similarity between the inverted applied variance curve
                         for a simulation and the corrsponding performance
                         curve. """ +
                         self.cs_methods_doc() +
                         self.bc_applicable_doc([':ref:`Temporal Variance <ln-bc-tv>`']) +
                         self.stage_usage_doc([4]),
                         choices=["pcm", "area_between",
                                  "frechet", "dtw", "curve_length"],
                         default="dtw")

        vcs.add_argument("--adaptability-cs-method",
                         help="""

                         Adaptability calculatation curve similarity
                         method. Specify the method to use to calculate the
                         similarity between the inverted applied variance curve
                         for a simulation and the corrsponding performance
                         curve.""" +
                         self.cs_methods_doc() +
                         self.bc_applicable_doc([':ref:`Temporal Variance <ln-bc-tv>`']) +
                         self.stage_usage_doc([4]),
                         choices=["pcm", "area_between",
                                  "frechet", "dtw", "curve_length"],
                         default="dtw")

    @staticmethod
    def cmdopts_update(cli_args: argparse.Namespace, cmdopts: types.Cmdopts):
        """Updates the core cmdopts dictionary with (key,value) pairs from the
        FORDYCA-specific cmdline options.

        """
        # Stage1
        updates = {
            # stage 4
            'envc_cs_method': cli_args.envc_cs_method,
            'gen_vc_plots': cli_args.gen_vc_plots,
            'reactivity_cs_method': cli_args.reactivity_cs_method,
            'adaptability_cs_method': cli_args.adaptability_cs_method,
            'rperf_cs_method': cli_args.rperf_cs_method,

            'pm_scalability_normalize': cli_args.pm_scalability_normalize,
            'pm_scalability_from_exp0': cli_args.pm_scalability_from_exp0,
            'pm_self_org_normalize': cli_args.pm_self_org_normalize,
            'pm_flexibility_normalize': cli_args.pm_flexibility_normalize,
            'pm_robustness_normalize': cli_args.pm_robustness_normalize,
            'pm_normalize_method': cli_args.pm_normalize_method,
        }

        if cli_args.pm_all_normalize:
            updates['pm_scalability_normalize'] = True
            updates['pm_self_org_normalize'] = True
            updates['pm_flexibility_normalize'] = True
            updates['pm_robustness_normalize'] = True

        cmdopts.update(updates)

    @staticmethod
    def cs_methods_doc() -> str:
        return r"""

        The following methods can be specified. Note that each some methods have
        a defined normalized domain, and some do not, and that the normalized
        domain may invert the meaning of lower values=better. If defined, the
        normalized domain the default for a given measure.

        - ``pcm`` - Partial Curve Mapping(Witowski2012).

          - Intrinsic domain: math: `[0, \infty)`. Lower values indicate greater
            similarity.

          - Normalized domain: N/A.

        - ``area_between`` - Area between the two curves(Jekel2018).

          - Intrinsic domain::math:`[0, \infty)`. Lower values indicate greater
            similarity.

          - Normalized domain: N/A.

        - ``frechet`` - Frechet distance(Frechet1906).

          - Intrinsic domain::math:`[0, \infty)`. Lower values indicate greater
            similarity.

          - Normalized domain: N/A.

        - ``dtw`` - Dynamic Time Warping(Berndt1994).

          - Intrinsic domain::math:`[0, \infty)`. Lower values indicate greater
            similarity.

          - Normalized domain: [0, 1]. Higher values indicate greater
            similarity.

        - ``curve_length`` - Arc-length distance along the curve from the origin
          of(applied - ideal) curve(Andrade-campos2009).

          - Intrinsic domain::math:`[0, \infty)`.

          - Normalized domain: N/A.
        """


class ARGoSCmdline(CommonCmdline):
    """
    Defines TITAN extensions to the core command line arguments defined in
    :class:`~sierra.core.cmdline.CoreCmdline`.
    """

    def init_multistage(self):
        super().init_multistage()

        self.multistage.add_argument("--scenario",
                                     metavar="<block dist>.AxBxC",
                                     help="""

                                     Which scenario the swarm comprised of
                                     robots running the controller specified via
                                     ``--controller`` should be run in.

                                     A scenario is defined as: block
                                     distribution type + arena dimensions. This
                                     is somewhat tied to foraging and other
                                     similar applications for the moment, but
                                     this may be modified in a future version of
                                     TITERRA.

                                     Valid block distribution types:

                                     - ``RN`` - Random
                                     - ``SS`` - Single source
                                     - ``DS`` - Dual source
                                     - ``QS`` - Quad source
                                     - ``PL`` - Power law

                                     A,B,C are the scenario X,Y,Z dimensions
                                     respectively (which can be any postive
                                     INTEGER values). All dimensions are
                                     required.

                                 """ + self.stage_usage_doc([1, 2, 3, 4]))

    def init_stage1(self):
        super().init_stage1()

        self.stage1.add_argument("--n-blocks",
                                 help="""

                                 # blocks that should be used in the
                                 simulation. Can be used to override batch
                                 criteria, or to supplement experiments that do
                                 not set it so that manual modification of input
                                 file is unneccesary.

                                 """ + self.stage_usage_doc([1]),
                                 type=int,
                                 default=None)

    @staticmethod
    def cmdopts_update(cli_args: argparse.Namespace, cmdopts: types.Cmdopts):
        """Updates the core cmdopts dictionary with (key,value) pairs from the
        FORDYCA-specific cmdline options.

        """
        CommonCmdline.cmdopts_update(cli_args, cmdopts)

        # Stage1
        updates = {
            # multi-stage
            'scenario': cli_args.scenario,

            # stage 1
            'n_blocks': cli_args.n_blocks
        }
        cmdopts.update(updates)


class ROSCmdline(CommonCmdline):
    pass
