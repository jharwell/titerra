#!/bin/bash -l
#SBATCH --time=4:00:00
#SBATCH --ntasks-per-node=1
#SBATCH --ncpus-per-task=24
#SBATCH --mem=2gb
#SBATCH --mail-type=ALL
#SBATCH --mail-user=harwe006@umn.edu
#SBATCH --output=R-%x.%j.out
#SBATCH --error=R-%x.%j.err
#SBATCH -J SIERRA-example

################################################################################
# Setup Simulation Environment                                                 #
################################################################################
# Set paths
FORDYCA=$HOME/git/fordyca
TITERRA=$HOME/git/titerra
export SIERRA_PROJECT_PATH=$TITERRA

################################################################################
# Begin Experiments                                                            #
################################################################################
OUTPUT_ROOT=$HOME/exp

cd $TITERRA
sierra-cli \
    --sierra-root=$OUTPUT_ROOT\
    --template-input-file=$TITERRA/templates/ideal.argos \
    --n-sims=8\
    --log-level=INFO\
    --project=fordyca_argos\
    --hpc-env=hpc.local\
    --pipeline 4\
    --physics-n-engines=1\
    --controller=d0.CRW\
    --scenario=SS.12x6x1\
    --with-robot-leds\
    --no-verify-results\
    --batch-criteria population_size.Log8\
    --n-blocks=20\
    --exp-setup=exp_setup.T10000\
    --exp-overwrite\
    --models-disable
