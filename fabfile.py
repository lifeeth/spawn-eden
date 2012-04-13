from __future__ import with_statement
from fabric.api import *
from cuisine import *


def init_env():
    run('apt-get -y update')
    run('apt-get -y upgrade')
    run('apt-get -y install aptitude sudo') # So that Cuisine plays nice
    package_update()

def setup_eden():
    init_env()
    run('echo "deb http://apt.balocco.name squeeze main" >> /etc/apt/sources.list')
    run('curl http://apt.balocco.name/key.asc | apt-key add -')
    run('apt-get -y update')
    package_ensure(["unzip",
                    "psmisc",
                    "mlocate",
                    "lrzsz",
                    "rcconf",
                    "htop",
                    "exim4-config",
                    "exim4-daemon-light",
                    "git-core",
                    "libgeos-c1",
                    "python2.6",
                    "python-dev",
                    "ipython",
                    "pyhton-lxml",
                    "python-setuptools",
                    "python-shapely",
                    "python-dateutil",
                    "python-serial",
                    "python-imaging",
                    "python-reportlab",
                    "python-matplotlib",
                    "python-xlwt",
                    "python-xlrd",
                    "build-essential",
                    "cherokee",
                    "libcherokee-mod-rrd",
                    "libxml2-dev"])
    #user_ensure("web2py")
    #with cd("/home/web2py"):
    #    run('bzr checkout --lightweight -r 3430 lp:~mdipierro/web2py/devel web2py')
    #with cd("/home/web2py/web2py/applications"):
    #    run('bzr checkout --lightweight lp:sahana-eden eden')
    #run('chown -R web2py: /home/web2py')
