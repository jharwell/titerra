=========
MSI Setup
=========

.. IMPORTANT::
   Prior to executing these steps you should have:

   #. Completed the :ref:`ln-hpc-local-setup` guide.
   #. Read through :ref:`ln-usage` guide.
   #. Gotten **CORRECT** results on some small scale experiments of interest on
      your local machine.

   You really, *really*, **really**, don't want to be trying to do
   development/debugging on MSI.

Workflow
========

#. Get an MSI account (you will need to talk to Maria Gini, my advisor), and
   verify that you can login to ``mesabi`` via the following commands, run from
   your laptop on a UMN computer/UMN wifi (will not work from outside UMN campus
   without a VPN)::

     ssh <x500>@mesabi.umn.edu


   Where ``<x500>`` is your umn x500. If the commands are successful, you have
   logged into a ``mesabi`` login node (this is different than a ``mesabi``
   compute node).

   A similar check for ``mangi`` via the following commands, run from your
   laptop on a UMN computer/UMN wifi (will not work from outside UMN campus
   without a VPN)::

     ssh <x500>@mangi.umn.edu

   If the commands are successful, you have logged into a ``mangi`` login node
   (this is different than a ``mangi`` compute node).

#. Once you can login, you can begin the setup by sourcing the environment
   definitions::

     . /home/gini/shared/swarm/bin/msi-env-setup.sh

   .. IMPORTANT:: ANYTIME you log into an MSI node (login or compute) to
                  build/run ANYTHING you MUST source this script otherwise
                  things might not work. This includes if you ran the script on
                  a login node and then started an interactive session via job
                  submission with ``-p interactive`` (the environment is NOT
                  inherited).

#. On an MSI login node (can be any type, as the filesystem is shared across all
   clusters), install the same python dependencies as in :ref:`ln-usage`, but
   user local (you obviously don't have admin priveleges on the cluster)::

     pip3 install --user -r requirements/msi.txt

   This is a one time step. Must be done on a login node, as compute nodes do
   not always have internet access (apparently?).


#. On an MSI login node, get an interactive job session so you can build your
   selected project and its dependencies natively to the cluster you will be
   running on (mangi/mesabi) for maximum speed::

     srun -N 1 --ntasks-per-node=4  --mem-per-cpu=1gb -t 1:00:00 -p interactive --pty bash


   The above command, when it returns, will give you 1 hour of time on an actual
   compute node. You know you are running/building on a compute node rather than
   a login node on mangi/mesabi when the hostname is ``cnXXXX`` rather than
   ``lnXXXX``.

#. In your interactive session clone the bootstrap repo and follow the
   instructions on the bootstrap README::

     git clone https://github.com/swarm-robotics/bootstrap.git

   In general, the only argument you should need for the script is ``--msi``.
