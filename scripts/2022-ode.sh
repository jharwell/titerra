#!/bin/bash -l
#SBATCH --time=24:00:00
#SBATCH --nodes 8
#SBATCH --tasks-per-node=4
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=2G
#SBATCH --mail-type=ALL
#SBATCH --mail-user=harwe006@umn.edu
#SBATCH --output=R-%x.%j.out
#SBATCH --error=R-%x.%j.err
#SBATCH -J 2022-ode-1

################################################################################
# Setup Simulation Environment                                                 #
################################################################################
set -x
set -e

if [ -n "$MSIARCH" ]; then # Running on MSI
    # Initialize modules
    source /home/gini/shared/swarm/bin/msi-env-setup.sh

    export TITERRA_ROOT=$HOME/research/$MSIARCH/titerra
    export FORDYCA_ROOT=$HOME/research/$MSIARCH/fordyca
    export SIERRA_PLUGIN_PATH=$HOME/research/$MSIARCH/titerra

    # Set SIERRA envvars--ONLY on MSI otherwise it doesn't work for
    # local runs.
    export SIERRA_ARCH=$MSIARCH

else
    export TITERRA_ROOT=$HOME/git/titan/titerra
    export FORDYCA_ROOT=$HOME/git/titan/fordyca
    export SIERRA_PLUGIN_PATH=$HOME/git/titan/titerra/titerra/projects
fi

# Set ARGoS library search path. Must contain both the ARGoS core libraries path
# AND the fordyca library path.
export ARGOS_PLUGIN_PATH=$localroot/lib/argos3:$FORDYCA_ROOT/build/lib

# Setup logging (maybe compiled out and unneeded, but maybe not)
export LOG4CXX_CONFIGURATION=$FORDYCA_ROOT/log4cxx.xml


# From MSI docs: transfers all of the loaded modules to the compute nodes (not
# inherited from the master/launch node when using GNU parallel)
export PARALLEL="--workdir . \
       --env PATH \
       --env LD_LIBRARY_PATH \
       --env LOADEDMODULES \
       --env _LMFILES_ \
       --env MODULE_VERSION \
       --env MODULEPATH \
       --env MODULEVERSION_STACK \
       --env MODULESHOME \
       --env OMP_DYNAMICS \
       --env OMP_MAX_ACTIVE_LEVELS \
       --env OMP_NESTED \
       --env OMP_NUM_THREADS \
       --env OMP_SCHEDULE \
       --env OMP_STACKSIZE \
       --env OMP_THREAD_LIMIT \
       --env OMP_WAIT_POLICY \
       --env ARGOS_PLUGIN_PATH \
       --env LOG4CXX_CONFIGURATION \
       --env SIERRA_PLUGIN_PATH \
       --env SIERRA_ARCH"


################################################################################
# Begin Experiments                                                            #
################################################################################
set -x

OUTPUT_ROOT=$HOME/exp/2022-ode-2

TIME_SMALL=exp_setup.T200000
# TIME_SMALL=exp_setup.T5000
VD_MIN_SMALL=1p0
VD_MAX_SMALL=10p0
VD_CARDINALITY_SMALL=C10

CD_SMALL=1p0
CD_CARDINALITY_SMALL=C16
CD_SIZEINC_SMALL=I4

CD_CRITERIA_SMALL=population_constant_density.${CD_SMALL}.${CD_SIZEINC_SMALL}.${CD_CARDINALITY_SMALL}
VD_CRITERIA_SMALL=population_variable_density.${VD_MIN_SMALL}.${VD_MAX_SMALL}.${VD_CARDINALITY_SMALL}

VD_MIN_LARGE=1p0
VD_MAX_LARGE=10p0
VD_CARDINALITY_LARGE=C10

TIME_LARGE=exp_setup.T200000
CD_LARGE=1p0
CD_CARDINALITY_LARGE=C16
CD_SIZEINC_LARGE=I72

CD_CRITERIA_LARGE=population_constant_density.${CD_LARGE}.${CD_SIZEINC_LARGE}.${CD_CARDINALITY_LARGE}
VD_CRITERIA_LARGE=population_variable_density.${VD_MIN_LARGE}.${VD_MAX_LARGE}.${VD_CARDINALITY_LARGE}

# SCENARIOS_LIST_CD=(LermanRN.8x8x2)
# SCENARIOS_LIST_CD=(SS.16x8x2 DS.16x8x2 RN.8x8x2 PL.8x8x2)
# SCENARIOS_LIST_CD=(RN.8x8x2 PL.8x8x2)
# SCENARIOS_LIST_VD_LARGE=(SS.256x128x2 DS.256x128x2 RN.256x256x2 PL.256x256x2)
# SCENARIOS_LIST_VD_LARGE=(RN.256x256x2)
# SCENARIOS_LIST_VD_SMALL=(SS.32x16x2 DS.32x16x2 RN.16x16x2 PL.16x16x2)
# SCENARIOS_LIST_VD_SMALL=(RN.16x16x2 PL.16x16x2)
SCENARIOS_LIST_VD_SMALL=(RN.16x16x2)

# NSIMS=32
NSIMS=4

SIERRA_BASE_CMD="sierra-cli \
                  --sierra-root=$OUTPUT_ROOT\
                  --template-input-file=$TITERRA_ROOT/templates/2022-ode.argos \
                  --n-runs=$NSIMS\
                  --controller=d0.CRW\
                  --project=fordyca_argos\
                  --pipeline 1 2 3 4 --exp-range 9:9 \
                  --project-imagizing --project-rendering\
                  --project-no-LN \
                  --dist-stats=conf95 \
                  --with-robot-leds\
                  --log-level=DEBUG\
                  --exp-overwrite"

if [ -n "$MSIARCH" ]; then # Running on MSI
    # 4 scenarios, each one containing 16 experiments
    EXP_NUM=$(($SLURM_ARRAY_TASK_ID % 16)) # This is the experiment
    SCENARIO_NUM=$(($SLURM_ARRAY_TASK_ID / 16)) # This is the scenario
    SCENARIOS_CD=(${SCENARIOS_LIST_CD[$SCENARIO_NUM]})
    SCENARIOS_VD_SMALL=(${SCENARIOS_LIST_VD_SMALL[$SCENARIO_NUM]})
    SCENARIOS_VD_LARGE=(${SCENARIOS_LIST_VD_LARGE[$SCENARIO_NUM]})
    TASK="exp"
    SIERRA_CMD="$SIERRA_BASE_CMD --hpc-env=hpc.slurm --exp-range=$EXP_NUM:$EXP_NUM --exec-resume"
    echo "********************************************************************************\n"
    squeue -j $SLURM_JOB_ID[$SLURM_ARRAY_TASK_ID] -o "%.9i %.9P %.8j %.8u %.2t %.10M %.6D %S %e"
    echo "********************************************************************************\n"

else
    SCENARIOS_CD=("${SCENARIOS_LIST_CD[@]}")
    SCENARIOS_VD_SMALL=("${SCENARIOS_LIST_VD_SMALL[@]}")
    SCENARIOS_VD_LARGE=("${SCENARIOS_LIST_VD_LARGE[@]}")
    TASK="$1"
    SIERRA_CMD="$SIERRA_BASE_CMD \
                 --exec-env=hpc.local\
                 --df-skip-verify\
                 --exp-graphs=inter --exp-graphs=none
                 "
fi

cd $TITERRA_ROOT

if [ "$TASK" == "small" ] || [ "$TASK" == "exp" ]; then

    for s in "${SCENARIOS_VD_SMALL[@]}"
    do
        $SIERRA_CMD --scenario=$s \
                    --batch-criteria ${VD_CRITERIA_SMALL}\
                    --exp-setup=${TIME_SMALL}\
                    --physics-n-engines=1

    done

    for s in "${SCENARIOS_CD[@]}"
    do
        $SIERRA_CMD --scenario=$s \
                    --batch-criteria ${CD_CRITERIA_SMALL}\
                    --exp-setup=${TIME_SMALL}\
                    --physics-n-engines=1

    done
fi

if [ "$TASK" == "large" ] || [ "$TASK" == "exp" ]; then

    for s in "${SCENARIOS_VD_LARGE[@]}"
    do
        $SIERRA_CMD --scenario=$s \
                    --batch-criteria ${VD_CRITERIA_LARGE}\
                    --exp-setup=${TIME_LARGE}\
                    --physics-n-engines=2
    done

    # for s in "${SCENARIOS_CD[@]}"
    # do
    #     $SIERRA_CMD --scenario=$s \
    #                 --batch-criteria ${CD_CRITERIA_LARGE}\
    #                 --exp-setup=${TIME_LARGE}\
    #                 --physics-n-engines=2

    # done
fi

if [ "$TASK" == "comp" ]; then
    STAGE5_CMD="sierra-cli \
                  --project=fordyca_argos\
                  --pipeline 5\
                  --scenario-comparison\
                  --dist-stats=conf95\
                  --bc-univar\
                  --controller=d0.CRW\
                  --plot-large-text\
                  --log-level=TRACE\
                  --sierra-root=$OUTPUT_ROOT"

    $STAGE5_CMD --batch-criteria $CD_CRITERIA_SMALL\
                --scenarios-list=SS.16x8x2,DS.16x8x2 \
                --scenarios-legend="SS","DS"

    $STAGE5_CMD --batch-criteria $CD_CRITERIA_SMALL\
                --scenarios-list=RN.8x8x2,PL.8x8x2\
                --scenarios-legend="RN","PL"

    $STAGE5_CMD --batch-criteria $VD_CRITERIA_SMALL\
                --scenarios-list=SS.32x16x2,DS.32x16x2\
                --scenarios-legend="SS","DS"

    $STAGE5_CMD --batch-criteria $VD_CRITERIA_SMALL\
                --scenarios-list=RN.16x16x2,PL.16x16x2\
                --scenarios-legend="RN","PL"

    # $STAGE5_CMD --batch-criteria $CD_CRITERIA_LARGE\
    #             --scenarios-list=SS.16x8x2,DS.16x8x2\
    #             --plot-enumerated-xscale\
    #             --plot-log-yscale\
    #             --scenarios-legend="SS","DS"

    # $STAGE5_CMD --batch-criteria $CD_CRITERIA_LARGE\
    #             --scenarios-list=RN.8x8x2,PL.8x8x2\
    #             --plot-enumerated-xscale\
    #             --plot-log-yscale\
    #             --scenarios-legend="RN","PL"

    # # $STAGE5_CMD --batch-criteria $VD_CRITERIA_LARGE\
    #             --scenarios-list=SS.256x128x2,DS.256x128x2\
    #             --plot-enumerated-xscale\
    #             --plot-log-yscale\
    #             --scenarios-legend="SS","DS"

    # $STAGE5_CMD --batch-criteria $VD_CRITERIA_LARGE\
    #             --scenarios-list=RN.256x256x2,PL.256x256x2\
    #             --plot-enumerated-xscale\
    #             --plot-log-yscale\
    #             --scenarios-legend="RN","PL"

fi
