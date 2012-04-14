from __future__ import with_statement
from fabric.api import *
from cuisine import *


def init_env():
    run('apt-get -y update')
    run('apt-get -y upgrade')
    run('apt-get -y install aptitude sudo curl') # So that Cuisine plays nice
    package_update()

def setup_eden():
    init_env()
    run('echo "deb http://apt.balocco.name squeeze main" >> /etc/apt/sources.list')
    run('curl http://apt.balocco.name/key.asc | apt-key add -')
    run('apt-get -y update')
    package_ensure(["unzip",
                    "wget",
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
                    "python-lxml",
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

    with settings(warn_only=True):
        run('useradd -M web2py')

    with cd('/home'): # Pull Web2py
        with settings(warn_only=True):
            run('git clone git://github.com/mdipierro/web2py.git')
        put('configs/routes.py','/home/web2py/')

    with cd('/home/web2py/applications'): #Eden setup
        with settings(warn_only=True):
            run('git clone git://github.com/flavour/eden.git')
            run('chown web2py /home/web2py')
            run('mkdir -p admin/cache')
            run('chown web2py admin/cache')
            run('chown web2py admin/cron')
            run('mkdir -p admin/databases')
            run('chown web2py admin/databases')
            run('mkdir -p admin/errors')
            run('chown web2py admin/errors')
            run('mkdir -p admin/sessions')
            run('chown web2py admin/sessions')
            run('chown web2py eden')
            run('mkdir -p eden/cache')
            run('chown web2py eden/cache')
            run('chown web2py eden/cron')
            run('mkdir -p eden/databases')
            run('chown web2py eden/databases')
            run('mkdir -p eden/errors')
            run('chown web2py eden/errors')
            run('chown web2py eden/models')
            run('mkdir -p eden/sessions')
            run('chown web2py eden/sessions')
            run('chown web2py eden/static/img/markers')
            run('mkdir -p eden/static/cache/chart')
            run('chown web2py -R eden/static/cache')
            run('mkdir -p eden/uploads')
            run('chown web2py eden/uploads')
            run('mkdir -p eden/uploads/gis_cache')
            run('mkdir -p eden/uploads/images')
            run('mkdir -p eden/uploads/tracks')
            run('chown web2py eden/uploads/gis_cache')
            run('chown web2py eden/uploads/images')
            run('chown web2py eden/uploads/tracks')

    with cd('/tmp'): #uwsgi setup
        run('rm uwsgi-1.0.2.1.tar.gz')
        run('wget http://projects.unbit.it/downloads/uwsgi-1.0.2.1.tar.gz')
        run('tar xzf uwsgi-1.0.2.1.tar.gz')
        run('cd uwsgi-1.0.2.1 && make && cp uwsgi /usr/local/bin')
        put('configs/run_scheduler.py','/home/web2py/')
        put('configs/uwsgi.xml','/home/web2py/uwsgi.xml')
        run('touch /tmp/uwsgi-prod.pid')
        run('chown web2py: /tmp/uwsgi-prod.pid')
        run('mkdir -p /var/log/uwsgi')
        run('chown web2py: /var/log/uwsgi')
        put('configs/uwsgi','/etc/init.d/uwsgi')
        run('chmod a+x /etc/init.d/uwsgi')
        run('update-rc.d uwsgi defaults')


