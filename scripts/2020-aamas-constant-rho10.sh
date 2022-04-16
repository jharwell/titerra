#!/bin/bash -l
#SBATCH --time=48:00:00
#SBATCH --nodes 1
#SBATCH --tasks-per-node=3
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=2G
#SBATCH --mail-type=ALL
#SBATCH --mail-user=harwe006@umn.edu
#SBATCH --output=R-%x.%j.out
#SBATCH --error=R-%x.%j.err
#SBATCH -J 2020-aamas-d0-constant-rho10-1

################################################################################
# Setup Simulation Environment                                                 #
################################################################################
# Initialize modules
source /home/gini/shared/swarm/bin/msi-env-setup.sh

export RESEARCH_INSTALL_PREFIX=$HOME/.local

if [ -n "$MSIARCH" ]; then # Running on MSI
    export TITERRA_ROOT=$HOME/research/titerra
    export FORDYCA_ROOT=$HOME/research/fordyca
else
    export TITERRA_ROOT=$HOME/git/titerra
    export FORDYCA_ROOT=$HOME/git/fordyca
fi

# Set ARGoS library search path. Must contain both the ARGoS core libraries path
# AND the fordyca library path.
export ARGOS_PLUGIN_PATH=$ARGOS_PLUGIN_PATH:$RESEARCH_INSTALL_PREFIX

# Setup logging (maybe compiled out and unneeded, but maybe not)
export LOG4CXX_CONFIGURATION=$FORDYCA_ROOT/log4cxx.xml

# Set SIERRA envvars
export SIERRA_ARCH=$MSIARCH
export SIERRA_PLUGIN_PATH=$TITERRA_ROOT/titerra/projects

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
OUTPUT_ROOT=$HOME/exp/2020-aamas-constant-rho10-1
EXP_SETUP=exp_setup.T1000

CONTROLLERS_LIST=(d1.BITD_DPO d1.BITD_ODPO d2.BIRTD_DPO d2.BIRTD_ODPO)
SCENARIOS_LIST=(SS.36x18x1 DS.36x18x1 QS.36x36x1)
#CONTROLLERS_LIST=(d1.BITD_DPO)
#SCENARIOS_LIST=(SS.36x18x1)

TASK="exp"
CARDINALITY=C8
NRUNS=3

BLOCK_COUNT=1000

# With the configured density, I12 increment, and specified starting
# arena sizes, we get 1024 max swarm size.
DENSITY=CD10p0

SIERRA_BASE_CMD="sierra-cli \
                 --sierra-root=$OUTPUT_ROOT  \
                 --template-input-file=$TITERRA_ROOT/templates/2020-aamas-constant-rho10.argos\
                 --n-runs=$NRUNS \
                 --exp-graphs=inter\
                 --project-no-yaml-LN\
                 --platform=platform.argos \
                 --project=fordyca_argos\
                 --dist-stats=conf95\
                 --exp-overwrite \
                 --exp-setup=${EXP_SETUP}\
                 --with-robot-leds\
                 --log-level=DEBUG \
                 --skip-verify-results"

if [ -n "$MSIARCH" ]; then # Running on MSI
    # 4 controllers, 3 scenarios
    SCENARIO_NUM=$(($SLURM_ARRAY_TASK_ID / 4)) # This is the scenario
    CONTROLLER_NUM=$(($SLURM_ARRAY_TASK_ID % 4)) # This is the controller
    CONTROLLERS=(${CONTROLLERS_LIST[$CONTROLLER_NUM]})
    SCENARIOS=(${SCENARIOS_LIST[$SCENARIO_NUM]})

    SIERRA_CMD="$SIERRA_BASE_CMD \
                --exec-env=hpc.slurm \
                --exec-resume \
                --pipeline 1 2"

    echo -e "********************************************************************************\n"
    squeue -j $SLURM_JOB_ID[$SLURM_ARRAY_TASK_ID] -o "%.9i %.9P %.8j %.8u %.2t %.10M %.6D %S %e"
    echo -e "********************************************************************************\n"
else
    TASK="$1"
    CONTROLLERS=("${CONTROLLERS_LIST[@]}")
    SCENARIOS=("${SCENARIOS_LIST[@]}")

    SIERRA_CMD="$SIERRA_BASE_CMD\
                  --exec-env=hpc.local\
                  --physics-n-engines=8 \
                  --exec-resume \
                  --pipeline 1 2
                  "
fi

cd $SIERRA_ROOT

if [ "$TASK" == "exp" ]; then
    for c in "${CONTROLLERS[@]}"
    do
        for s in "${SCENARIOS[@]}"
        do
            $SIERRA_CMD\
                --controller=${c} \
                --scenario=${s} \
                --n-blocks=${BLOCK_COUNT} \
                --batch-criteria population_constant_density.${DENSITY}.I12.C10 ta_policy_set.all
        done
    done
fi

if [ "$TASK" == "comp" ]; then
    STAGE5_CMD="sierra-cli \
                  --project=fordyca_argos\
                  --pipeline 5\
                  --controller-comparison\
                  --dist-stats=conf95\
                  --bc-bivar\
                  --plot-large-text\
                  --log-level=TRACE\
                  --sierra-root=$OUTPUT_ROOT\
                  --comparison-type=HMraw"
    for s in "${SCENARIOS[@]}"
    do
        $STAGE5_CMD --batch-criteria population_constant_density.${DENSITY}.I12.C10 ta_policy_set.all \
                    --controllers-list=d0.DPO,d0.DPO \
                    --scenario=${s} \
                    --controllers-legend="Average Cross-Clique Centrality=1","Average Cross-Clique Centrality=1.2"
        done
fi
