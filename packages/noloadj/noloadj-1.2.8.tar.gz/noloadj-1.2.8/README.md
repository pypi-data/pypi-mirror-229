<!--
SPDX-FileCopyrightText: 2021 G2Elab / MAGE

SPDX-License-Identifier: Apache-2.0
-->

NoLOAD_Jax: Non Linear Optimization by Automatic Differentiation using Jax
==========================================================================

We are happy that you will use or develop the NoLOAD_Jax.
It is an **Open Source** project located on GitLab at https://gricad-gitlab.univ-grenoble-alpes.fr/design_optimization/NoLoad_v2
It aims at **solving constrained optimization** problem for the design of engineering systems

Project Presentation
====================

**NoLOAD_Jax:** Please have a look to NoLOAD presentation : https://noload-jax.readthedocs.io/en/latest/

A scientific article presenting NoLOAD is available here:

Agobert Lucas, Hodencq Sacha, Delinchant Benoit, Gerbaud Laurent, Frederic Wurtz, “NoLOAD, Open Software for Optimal Design and Operation using Automatic Differentiation”, OIPE 2020, Poland, 09-2021. https://hal.archives-ouvertes.fr/hal-03352443

Please cite us when you use NoLOAD.

NoLOAD_Jax Community
====================

Please use the git issues system to report an error: https://gricad-gitlab.univ-grenoble-alpes.fr/design_optimization/NoLoad_v2
Otherwise you can also contact the developer team using the following email adress: benoit.delinchant@G2ELab.grenoble-inp.fr

Installation Help
=================
You can install the library as a user or as a developer. Please follow the corresponding installation steps below.

Prerequisite
------------

Please install Python 3.8 or later
https://www.python.org/downloads/

Windows
-------

The simplest way to install it
------------------------------
Go on  https://whls.blob.core.windows.net/unstable/index.html and download the cpu/jaxlib-0.3.25-cp3X-cp3X-win_amd64.whl, where 3.X is your Python version.
Put it in your Python environment and tape on a terminal :

    pip install cpu/jaxlib-0.3.25-cp3X-cp3X-win_amd64.whl
    pip install jax==0.3.25
    pip install noloadj

The Jax version installed is not the newest one, but it is sufficient to use Noload_Jax.

    
How to configure a virtual environment on WSL running with an Ubuntu distribution :
------------------------------
The alternative to get Jax last versions is to install a virtual environment on WSL running with an Ubuntu distribution.
At first, activate the WSL on you computer and install on it an Ubuntu distribution by following the 6 first steps of the link :
https://docs.microsoft.com/en-us/windows/wsl/install-win10

Then open WSL.exe using the Windows search bar and tape :

    cd ~
    sudo apt update
    sudo apt install python3-pip
    sudo pip3 install virtualenv
    python3 -m virtualenv pythonenv
    
You can replace "pythonenv" by "venv" or another name of your choice. Then write :

    source pythonenv/bin/activate

You must see a "(pythonenv)" written at the beginning of the command line.
Now close WSL and open Pycharm in a new project. 
Go to File/Settings/Project:_name_of_your_project_/Project Interpreter and add a new interpreter.
Choose WSL option then change the Python interpreter path by /home/_your_username_/pythonenv/bin/python3. (_your_username_ is the login you chose for WSL)
Close the Settings window. Click on Terminal section at the bottom, and tape on the commande line  :

    source /home/your_username/pythonenv/bin/activate

If you see a "(pythonenv)" written at the beginning of the command line, the configuration is completed and you can run your code now !

Linux
-----
Please install NoLOAD_Jax with pip using the command prompt.   

If you are working on a virtual environment on Linux
    
    pip install noloadj

If you want a local installation or you are not admin
    
    pip install --user noloadj

If you are admin on Linux:
    
    sudo pip install noloadj

Launch the examples to understand how the NoLOAD_Jax works:
	
	python noloadj/01-UnconstrainedMonoObjective.py
	python noloadj/02-ConstrainedMonoObjective.py
	python noloadj/03-ConstrainedMultiObjective.py
	python noloadj/04-ConstrainedMonoObjective2.py
	
Enjoy your time using NoLOAD_Jax !

GPU & IPOPT Algorithm
---------------------
As it uses the JAX library, NoLOAD_Jax can run on CPU (Central Processor Unit) or GPU (Graphics Processor Unit), where GPU offers better performances than CPU.
With WSL only CPU can be used. To use GPU you may run NoLOAD on Ubuntu.
If you want to use GPU, you need to install CUDA and CuDNN on your computer then tape on Pycharm terminal (where 0.3.XX is your JAX version):

    pip install --upgrade pip
    pip install --upgrade jax jaxlib==0.3.XX+cuda111 -f https://storage.googleapis.com/jax-releases/jax_releases.html
    
If you use GPU, you need to put these lines at the beginning of your "optimization" file to avoid memory issues :

    import os
    os.environ['XLA_PYTHON_CLIENT_PREALLOCATE']='false'
    os.environ['XLA_PYTHON_CLIENT_MEM_FRACTION']='0.50'
    
To install IPOPT algorithm, please install an Anaconda environment and run this command on a terminal :

    conda install -c conda-forge cyipopt

Library Installation Requirements
---------------------------------
Matplotlib >= 3.0
Scipy >= 1.2
Jax >= 0.3.25
Jaxlib >= 0.3.25
Pandas >= 1.3.5


Main Authors: 
=============
B. DELINCHANT, L. GERBAUD, F. WURTZ, L. AGOBERT


Partners:
=========
Vesta-System: http://vesta-system.fr/

Acknowledgments:
================


Licence
=======
This code is under the Apache License, Version 2.0
