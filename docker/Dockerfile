FROM ubuntu:focal


RUN apt -y update && apt -y upgrade
# Install deps that are not automatically installed by pre_install.sh
# TODO use "--no-install-recommends" here. git has some optional deps that prevent it from cloning
RUN apt -y install git sudo lsb-release

RUN git clone --branch docker https://github.com/maringuu/FACT_core.git /opt/FACT_core

RUN useradd -r fact
RUN DEBIAN_FRONTEND="noninteractive" apt -y install tzdata


RUN apt-get -y install python3-pip git libffi-dev
RUN apt-get -y install apt-transport-https ca-certificates curl software-properties-common
RUN apt-get -y install docker-compose docker.io

# TODO figure out why enum34 is relevant

RUN pip3 install --upgrade pip
RUN pip3 install --upgrade virtualenv distro python-magic requests

RUN pip3 install --upgrade git+https://github.com/fkie-cad/common_helper_files.git
RUN pip3 install --upgrade git+https://github.com/fkie-cad/common_helper_process.git

RUN apt install wget

RUN /opt/FACT_core/src/install.py -B
