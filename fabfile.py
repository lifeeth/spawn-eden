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
    run("export DEBIAN_FRONTEND='noninteractive' && apt-get -y -q install postfix")
    package_ensure(["unzip",
                    "wget",
                    "psmisc",
                    "mlocate",
                    "lrzsz",
                    "rcconf",
                    "htop",
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
                    "libxml2-dev",
                    "python-psycopg2"])

    with settings(warn_only=True):
        run('useradd -M web2py')

    with cd('/home'): # Pull Web2py
        with settings(warn_only=True):
            run('git clone git://github.com/mdipierro/web2py.git')
        put('configs/routes.py','/home/web2py/')

    with cd('/home/web2py/applications'): #Eden setup
        with settings(warn_only=True):
#            run('git clone git://github.com/flavour/eden.git')
            run('git clone git://github.com/flavour/ifrc.git eden')
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
        with settings(warn_only=True):
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


    run('cp /etc/cherokee/cherokee.conf /etc/cherokee/cherokee.conf.bak') #Cherokee configs
    put('configs/cherokee.conf','/etc/cherokee/cherokee.conf')
    put('configs/maintenance.html','/var/www/maintenance.html')
    run('/etc/init.d/cherokee restart')

    install_postgres() #install postgres

    ##Maintenance scripts

    put('configs/compile','/usr/local/bin')
    run('chmod +x /usr/local/bin/compile')

    put('configs/pull','/usr/local/bin')
    run('chmod +x /usr/local/bin/pull')

    put('configs/clean','/usr/local/bin')
    run('chmod +x /usr/local/bin/clean')

    put('configs/w2p','/usr/local/bin')
    run('chmod +x /usr/local/bin/w2p')

    put('configs/reload-uwsgi','/usr/local/bin')
    run('chmod +x /usr/local/bin/reload-uwsgi')

    put('configs/start-uwsgi','/usr/local/bin')
    run('chmod +x /usr/local/bin/start-uwsgi')

    put('configs/stop-uwsgi','/usr/local/bin')
    run('chmod +x /usr/local/bin/stop-uwsgi')

def install_postgres():
    """Install Postgres on a remote machine"""

    package_ensure(["postgresql-8.4",
                    "postgresql-8.4-postgis",
                    "ptop"])

    put('configs/sysctl.conf','/tmp') #Postgres configs
    run('echo /tmp/sysctl.conf >> /etc/sysctl.conf')
    run('sysctl -w kernel.shmmax=279134208') # For 512MB RAM
    #run('sysctl -w kernel.shmmax=552992768') # For 512MB RAM
    run('sysctl -w kernel.shmall=2097152')
    run("sed -i 's|#track_counts = on|track_counts = on|' /etc/postgresql/8.4/main/postgresql.conf")
    run("sed -i 's|#autovacuum = on|autovacuum = on|' /etc/postgresql/8.4/main/postgresql.conf")
    run("sed -i 's|shared_buffers = 28MB|shared_buffers = 160MB|' /etc/postgresql/8.4/main/postgresql.conf")
    run("sed -i 's|#effective_cache_size = 128MB|effective_cache_size = 512MB|' /etc/postgresql/8.4/main/postgresql.conf")
    run("sed -i 's|#work_mem = 1MB|work_mem = 4MB|' /etc/postgresql/8.4/main/postgresql.conf")

    ##Maintenance scripts
    put('configs/backup','/usr/local/bin')
    run('chmod +x /usr/local/bin/backup')

def install_memcached():
    """Installs memcached on the remote machine"""
    package_ensure(["memcached"])

def configure_eden():

    domain = raw_input("What domain name should we use?  ")
    hostname = raw_input("What host name should we use?  ")
    password = raw_input("What is the new PostgresSQL password?  ")
    print "Now reconfiguring system to use the hostname: " + hostname

    with cd('/etc'):
        run('sed -i "s|localdomain localhost|localdomain localhost '+hostname+'|" hosts')
        run('echo '+hostname+' >hostname')
        run('echo '+hostname+'.'+domain+' >mailname')

    with cd('/home/web2py'):
        run('git pull')

    with cd('/home/web2py/applications/eden'):
        run('git pull')


    run("export DEBIAN_FRONTEND='noninteractive' && dpkg-reconfigure postfix")

    # Setting up Sahana
    run('cp /home/web2py/applications/eden/deployment-templates/cron/crontab /home/web2py/applications/eden/cron')
    run('cp /home/web2py/applications/eden/deployment-templates/models/000_config.py /home/web2py/applications/eden/models')
    run('sed -i "s|EDITING_CONFIG_FILE = False|EDITING_CONFIG_FILE = True|" /home/web2py/applications/eden/models/000_config.py')
    run('sed -i "s|akeytochange|+'+hostname+'.'+domain+password+'|" /home/web2py/applications/eden/models/000_config.py')
    run('sed -i "s|127.0.0.1:8000|'+hostname+'.'+domain+'|" /home/web2py/applications/eden/models/000_config.py')
    run('sed -i "s|base.cdn = False|base.cdn = True|" /home/web2py/applications/eden/models/000_config.py')

    #Postgres
    run('echo "CREATE USER sahana WITH PASSWORD \''+password+'\';" > /tmp/pgpass.sql')
    sudo('psql -q -d template1 -f /tmp/pgpass.sql', user='postgres')
    run('rm -f /tmp/pgpass.sql')
    sudo('createdb -O sahana -E UTF8 sahana -T template0', user='postgres')
    sudo('createlang plpgsql -d sahana', user='postgres')

    #PostGIS
    sudo('psql -q -d sahana -f /usr/share/postgresql/8.4/contrib/postgis-1.5/postgis.sql', user='postgres')
    sudo('psql -q -d sahana -f /usr/share/postgresql/8.4/contrib/postgis-1.5/spatial_ref_sys.sql', user='postgres')
    sudo('psql -q -d sahana -c \'grant all on geometry_columns to sahana;\'', user='postgres')
    sudo('psql -q -d sahana -c \'grant all on spatial_ref_sys to sahana;\'', user='postgres')

    # Configure Database
    run('sed -i \'s|deployment_settings.database.db_type = "sqlite"|deployment_settings.database.db_type = "postgres"|\' /home/web2py/applications/eden/models/000_config.py')
    run('sed -i \'s|deployment_settings.database.password = "password"|deployment_settings.database.password = "'+password+'"|\' /home/web2py/applications/eden/models/000_config.py')

    # Create the Tables & Populate with base data
    run("sed -i 's|deployment_settings.base.prepopulate = 0|deployment_settings.base.prepopulate = 1|' /home/web2py/applications/eden/models/000_config.py")
    run("sed -i 's|deployment_settings.base.migrate = False|deployment_settings.base.migrate = True|' /home/web2py/applications/eden/models/000_config.py")

    with cd('/home/web2py'):
        run("sudo -H -u web2py python web2py.py -S eden -M -R applications/eden/static/scripts/tools/noop.py")

    #Configure for Production
    run("sed -i 's|deployment_settings.base.prepopulate = 1|deployment_settings.base.prepopulate = 0|' /home/web2py/applications/eden/models/000_config.py")
    run("sed -i 's|deployment_settings.base.migrate = True|deployment_settings.base.migrate = False|' /home/web2py/applications/eden/models/000_config.py")

    with cd('/home/web2py'):
        run("sudo -H -u web2py python web2py.py -S eden -R applications/eden/static/scripts/tools/compile.py")

    #Schedule backups for 2:01 daily
    run('echo "1 2   * * * * root    /usr/local/bin/backup" >> "/etc/crontab"')

    run('/etc/init.d/uwsgi start')
    print "Done."
