#!/bin/bash -l

################################################################################
# Setup Simulation Environment                                                 #
################################################################################
# Set paths
FORDYCA=$HOME/git/fordyca
SIERRA=$HOME/git/sierra

OUTPUT_ROOT=$HOME/exp/2022-aamas-demo

cd $SIERRA
TASK="$1"

BASE_CMD="sierra-cli \
        --sierra-root=$OUTPUT_ROOT\
        --platform=platform.argos\
        --template-input-file=templates/2022-aamas-demo.argos \
        --project=fordyca_argos\
        --physics-n-engines=1\
        --exp-setup=exp_setup.T1000\
        --batch-criteria population_size.Log16\
        --exp-overwrite\
        --models-disable\
        --log-level=INFO\
        --no-verify-results\
        --with-robot-leds"

################################################################################
# Basic Experiment                                                             #
################################################################################
if [ "$TASK" == "demo1" ]; then
    $BASE_CMD --controller=d0.CRW\
              --scenario=SS.12x6x2\
              --n-runs=16 --exec-resume --dist-stats=bw
fi

################################################################################
# Controller Comparison: CRW and DPO                                           #
################################################################################
if [ "$TASK" == "demo2" ]; then
    $BASE_CMD --controller=d0.DPO\
              --scenario=SS.12x6x2\
              --n-runs=24

    $BASE_CMD --pipeline 5\
              --controller-comparison\
              --controller-list=d0.CRW,d0.DPO\
              --controllers-legend=CRW,DPO\
              --bc-univar
fi

################################################################################
# ARGoS Video Rendering                                                        #
################################################################################
if [ "$TASK" == "demo3" ]; then
    controllers=(d0.CRW d1.BITD_DPO d2.BIRTD_DPO)
    $BASE_CMD --controller=d0.CRW\
              --scenario=SS.12x6x2\
              --n-runs=4\
              --platform-vc\
              --camera-config=sierra.sw+interp+zoom\
              --exp-graphs=none
fi

################################################################################
# .csv Video Rendering                                                         #
################################################################################
if [ "$TASK" == "demo4" ]; then
    $BASE_CMD --controller=d0.CRW\
              --scenario=SS.12x6x1\
              --n-runs=4\
              --platform-vc\
              --project-imagizing\
              --project-rendering\
              --exp-graphs=none
fi
