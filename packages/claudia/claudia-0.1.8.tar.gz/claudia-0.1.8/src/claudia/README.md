# Claudia
Claudia is a helper utility that allows users to perform XRPL specific tasks both locally and on other public networks. Both macOS and Ubuntu are supported. Currently, there is no support for Windows.

Claudia provides users a seamless UI and CLI experience. There are a lot of commands which support a lot of options. It also offers a _demo_ mode, which can help reduce typing efforts significantly. You would mostly navigate a pre-built menu using `↑ ↓` and `↵` keys. Minimal typing will be required. UI, CLI and demo modes offer the similar functionality. UI mode also includes _XRPL Learning Center_.

Some important tasks that can be performed using Claudia are listed below:

- Build rippled from local code
- Install rippled from pre-built binaries released by Ripple
- Manage a local-mainnet network using local rippled instance
- Manage a local-sidechain network
- Build a local witness server using local code
- Run unit tests on the built/installed rippled instance
- Run system tests on local-mainnet, local-sidechain, devnet and testnet network
- Manage rippled features on the local-mainnet and local-sidechain networks

---
---

## General Prerequisites
Please have the following installed on your machine before proceeding further:
- [Python3](https://www.python.org/)
  - Run ```python3 --version``` to check if Python3 is already installed. 
  - If Python3 is not installed, please install it using the official [Python installer](https://www.python.org/downloads/).
  - Verify installation by running: ```python3 --version```
- [pip3](https://pip.pypa.io/en/stable/)
  - Run ```pip3 --version``` to check if Python3 is already installed. 
  - If pip3 is not installed, follow the next steps:
    - macOS: 
      - ```python3 -m ensurepip --upgrade```
    - Linux:
      - ```sudo apt update```
      - ```sudo apt install python3-pip```
    - Verify installation by running: ```pip3 --version```
- [docker](https://www.docker.com/)
  - Run ```docker --version``` to check if docker is already installed.
  - If docker is not installed, follow the next steps:
    - macOS:
      - Download and then run the [Docker Desktop installer for macOS](https://docs.docker.com/desktop/install/mac-install/).
    - Linux:
      - Download and then run the [Docker Desktop installer for Linux](https://docs.docker.com/desktop/install/linux-install/).
-  _Following is **ONLY** required if you intend to run Javascript system tests:_
   - [node](https://nodejs.org/en/download)
     -  Run ```node --version``` to check if node is already installed.
     -  If node is not installed, follow the next steps:
        - macOS:
          - ```brew install node```
        - Linux: 
          - ```curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt-get install -y nodejs```
   - [npm](https://www.npmjs.com/package/download)
     - Run ```npm -v``` to check if npm ia already installed. 
     - If npm in not installed, follow the next steps:
       - macOS:
         - ```brew install npm```
       - Linux:
         - ```sudo apt install npm```
- Clone [rippled](https://github.com/XRPLF/rippled) code, if you intend to build rippled locally and/or manage/test a sidechain network.
  - If you intend to use sidechain functionality, please use [this](https://github.com/seelabs/rippled/tree/xbridge) rippled fork instead.
- Clone [XBridge Witness](https://github.com/seelabs/xbridge_witness) code, if you intend to build witness server locally and/or manage/test the sidechain network.

---
---

## Installation

Install claudia from [PyPi](https://pypi.org/project/claudia/), by running: 

      pip3 install claudia

### If you want to build Claudia from the local code, you can run:

      rm -fr build/ dist/ claudia.egg-info
      pip uninstall -y claudia
      python3 setup.py sdist bdist_wheel
      pip install dist/*.tar.gz
      rm -fr build/ dist/ claudia.egg-info

---
---

## Usage
Following are some important tasks you can perform with Claudia. There are a lot more options. Please explore using the demo mode or `--help` flag in the CLI mode.

---

### How to run Claudia UI?
- CLI Mode
  - After installing claudia, go to your terminal and run `claudia ui`.
- Demo Mode
  - Launch Claudia in demo mode and select `Launch Claudia UI`.
---

### How to run Claudia in CLI mode?
- After installing claudia, go to your terminal and run `claudia`
  - TIP: Use `--help` flag to see what options are available at different levels. e.g. `claudia --help`

---

### How to run Claudia in demo mode?
- After installing claudia, go to your terminal and run `claudia demo`.
- Follow the instructions on the screen. Please use `↑ ↓` and `↵` keys to navigate.

---

### How to build rippled?
- CLI Mode
  - Run `claudia rippled build --repo` <absolute_path_to_local_repo>
- Demo Mode
  - Launch Claudia in demo mode and select `Rippled` -> `Build rippled from local code`. Follow the instructions.

This is where you can use the 'rippled' code cloned as part of the setup in the [General Prerequisites](#general-prerequisites) section. The path to the code directory must be absolute. 

TIP: This step will take a while. _Feel free to grab a drink of your choice!_

---

### How to install rippled?
- CLI Mode
  - Run `claudia rippled install`
- Demo Mode
  - Launch Claudia in demo mode and select `Rippled` -> `Install rippled`. Follow the instructions.

---

### How to switch between build and install rippled modes?
Once you start with with build or install mode, claudia will remember that context forever.
If you would like to switch between install and build modes, run the following:
- CLI Mode
  - Run `claudia set-install-mode build` to set build mode.
  - Run `claudia set-install-mode install` to set install mode.
- Demo Mode
  - Launch Claudia in demo mode and select `Settings` -> `Set install mode as build` to set build mode. Follow the instructions.
  - Launch Claudia in demo mode and select `Settings` -> `Set install mode as install` to set install mode. Follow the instructions.

Please note that all previously running networks will have to be stopped and started again.

---

### How to enable a feature in rippled?
  - Prerequisite: rippled has to be built/installed locally. Please see rippled [build](#how-to-build-rippled)/[install](#how-to-install-rippled) instructions.
  - CLI Mode
    - Run `claudia enable-feature --feature <feature_name>`
  - Demo Mode
    - Launch Claudia in demo mode and select `Settings` -> `Enable a feature`. Follow the instructions.
  
    Please note that there is no validation for feature name. Please make sure the feature name is correct (case-sensitive).

---

### How to build witness server?
- CLI Mode
  - Run `claudia witness build --repo` <absolute_path_to_local_repo>
- Demo Mode
  - Launch Claudia in demo mode and select `Custom XRPL Networks` -> `Build witness server`. Follow the instructions.

This is where you can use the 'XBridge Witness' code cloned as part of the setup in the [General Prerequisites](#general-prerequisites) section. The path to the code directory must be absolute.

TIP: This step will take a while. _Feel free to grab a drink of your choice!_

---

### How to start local networks?
#### How to start a local-mainnet network?
  - Prerequisite:  rippled has to be built/installed locally. Please see rippled [build](#how-to-build-rippled)/[install](#how-to-install-rippled) instructions.
  - CLI Mode
    - Run `claudia local-mainnet start`
  - Demo Mode
    - Launch Claudia in demo mode and select `Custom XRPL Networks` -> `Start local-mainnet`. Follow the instructions.

#### How to stop a local-mainnet network?
  - Prerequisite:  local-mainnet has to be running. Please see [how to start a local-mainnet network](#how-to-start-a-local-mainnet-network)
  - CLI Mode
    - Run `claudia local-mainnet stop`
  - Demo Mode
    - Launch Claudia in demo mode and select `Custom XRPL Networks` -> `Stop local-mainnet`. Follow the instructions.

#### How to start a local-sidechain network?
  - Prerequisite: 
    - rippled has to be built/installed locally. Please see rippled [build](#how-to-build-rippled)/[install](#how-to-install-rippled) instructions.
    - Witness server has to be built locally. Please see witness server [build](#how-to-build-witness-server) instructions.
    - `XChainBridge` feature has to be enabled. Please see [how to enable a feature](#how-to-enable-a-feature-in-rippled).
    - The local-mainnet network has to be running. Please see [how to start a local-mainnet network](#how-to-start-a-local-mainnet-network).
  - CLI Mode
    - Run `claudia local-sidechain start`
  - Demo Mode
    - Launch Claudia in demo mode and select `Custom XRPL Networks` -> `Start local-sidechain`. Follow the instructions.


#### How to stop a local-sidechain network?
  - Prerequisite:
    - local-sidechain has to be running. Please see [how to start a local-sidechain network](#how-to-start-a-local-sidechain-network).
  - CLI Mode
    - Run `claudia local-sidechain stop`
  - Demo Mode
    - Launch Claudia in demo mode and select `Custom XRPL Networks` -> `Stop local-sidechain`. Follow the instructions.

Please note that once the sidechain has been stopped, local-mainnet has to be stopped and then started again before attempting to start the local-sidechain again.

---

### How to run unit tests?
- Prerequisite: 
    - rippled has to be built/installed locally. Please see rippled [build](#how-to-build-rippled)/[install](#how-to-install-rippled) instructions.
  - CLI Mode
    - Run `claudia run unittests`. Run `claudia run unittests --help` to see options.
  - Demo Mode
    - Launch Claudia in demo mode and select `XRPL Tests` -> `Run unit tests`. Follow the instructions.

---

### How to run system tests?
- CLI Mode
  - Run `claudia run systemtests`. Run `claudia run systemtests --help` to see options.
- Demo Mode
    - Launch Claudia in demo mode and select `XRPL Tests` -> `Run system tests`. Follow the instructions.

Please note that if you want to run the tests on local-mainnet/local-sidechain networks, the networks need to be started first. Please see [how to start local networks](#how-to-start-local-networks)

### How to cleanup your computer and free resources after running Claudia?
While using claudia, there are a few files created permanently. Also, there are a few system resources which are reserved for future use. Running this command will delete these files and free up resources. As a result, _***any progress made by using Claudia will be lost. This action cannot be undone.***_
- CLI Mode
  - Run `claudia clean`.
- Demo Mode
    - Launch Claudia in demo mode and select `Settings` -> `Clean up the host and free resources`. Follow the instructions.

### How to uninstall Claudia?
We recommend that you [cleanup your machine](#how-to-cleanup-your-computer-and-free-resources-after-running-claudia) before uninstalling Claudia. Afterwards, please run:

      pip3 uninstall claudia

---
---

## Contributions
Claudia is developed by Ripple Automation Team. The following people contributed to this release:

- Manoj Doshi <mdoshi@ripple.com>
- Ramkumar SG <rsg@ripple.com>
- Kaustubh Saxena <ksaxena@ripple.com>
- Michael Legleux <mlegleux@ripple.com>
- Anagha Agashe <aagashe@ripple.com>
- Mani Mounika Kunasani <mkunasani@ripple.com>
