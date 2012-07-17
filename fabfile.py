from __future__ import with_statement
from fabric.api import *
from cuisine import *
import time
import os

try:
    import boto.ec2
except Exception as e:
    print "Install boto for EC2 support"

branch = "git://github.com/flavour/eden.git"
template = "default"

def init_env():
    run('apt-get -y update')
    run('apt-get -y upgrade')
    run('apt-get -y install aptitude sudo curl') # So that Cuisine plays nice
    run("export DEBIAN_FRONTEND='noninteractive' && apt-get -y -q install postfix")
    package_update()
    package_ensure(["unzip",
                    "wget",
                    "psmisc",
                    "mlocate",
                    "lrzsz",
                    "rcconf",
                    "htop"])

def setup_eden(): # By default setups postgres,uwsgi and cherokee
    init_env()
    run('echo "deb http://apt.balocco.name squeeze main" >> /etc/apt/sources.list')
    run('curl http://apt.balocco.name/key.asc | apt-key add -')
    run('apt-get -y update')
    package_ensure(["python2.6",
                    "python-dev",
                    "ipython",
                    "build-essential",
                    "cherokee",
                    "libcherokee-mod-rrd",
                    "libxml2-dev"])

    #run('apt-get -y --force-yes install psmisc cherokee libcherokee-mod-rrd')
    
    drop_eden() # Put Eden files in the proper directories.
    install_postgres() # Install Postgres
    with cd('/tmp'): #uwsgi setup
        with settings(warn_only=True):
            run('rm uwsgi-*.tar.gz')
        run('wget http://projects.unbit.it/downloads/uwsgi-latest.tar.gz')
        run('tar xzf uwsgi-latest.tar.gz')
        run('cd uwsgi-* && make && cp uwsgi /usr/local/bin')
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
    run('/etc/init.d/cherokee stop')

def drop_eden(path='/home'): # Web2py directory will be created within this directory.
    
    package_ensure(["git-core",
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
                    "python-psycopg2"])

    with settings(warn_only=True):
        run('useradd -M web2py')

    with cd(path): # Pull Web2py
        with settings(warn_only=True):
            run('git clone git://github.com/mdipierro/web2py.git')
        put('configs/routes.py',os.path.join(path,'web2py'))

    with cd(os.path.join(path,'web2py/applications')): #Eden setup
        with settings(warn_only=True):
            run('git clone '+branch+' eden')
            run('chown web2py '+str(os.path.join(path,'web2py')))
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


def configure_eden_standalone(start_eden = True):

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

    # Setting up Sahana
    run('cp /home/web2py/applications/eden/private/templates/000_config.py /home/web2py/applications/eden/models')
    run('sed -i "s|EDITING_CONFIG_FILE = False|EDITING_CONFIG_FILE = True|" /home/web2py/applications/eden/models/000_config.py')
    run('sed -i "s|#settings.base.public_url|settings.base.public_url|" /home/web2py/applications/eden/models/000_config.py')
    run('sed -i "s|127.0.0.1:8000|'+hostname+'.'+domain+'|" /home/web2py/applications/eden/models/000_config.py')
    run('sed -i "s|#settings.base.cdn|settings.base.cdn|" /home/web2py/applications/eden/models/000_config.py')
    run('sed -i "s|settings.base.template = \"default\"|settings.base.template = "'+template+'"|" /home/web2py/applications/eden/models/000_config.py')

    # Configure Database
    run('sed -i \'s|#settings.database.db_type = "postgres"|settings.database.db_type = "postgres"|\' /home/web2py/applications/eden/models/000_config.py')
    run('sed -i \'s|#settings.database.port = 5432|settings.database.port = 5432|\' /home/web2py/applications/eden/models/000_config.py')
    run('sed -i \'s|#settings.database.password = "password"|settings.database.password = "'+password+'"|\' /home/web2py/applications/eden/models/000_config.py')
    run('sed -i \'s|#settings.gis.spatialdb = True|settings.gis.spatialdb = True|\' /home/web2py/applications/eden/models/000_config.py')

    # Create the Tables & Populate with base data
    run("sed -i 's|settings.base.migrate = False|settings.base.migrate = True|' /home/web2py/applications/eden/models/000_config.py")

    with cd('/home/web2py'):
        run("sudo -H -u web2py python web2py.py -S eden -M -R applications/eden/static/scripts/tools/noop.py")

    #Configure for Production
    run("sed -i 's|settings.base.migrate = True|settings.base.migrate = False|' /home/web2py/applications/eden/models/000_config.py")

    with cd('/home/web2py'):
        run("sudo -H -u web2py python web2py.py -S eden -R applications/eden/static/scripts/tools/compile.py -M")

    #Schedule backups for 2:01 daily
    run('echo "1 2   * * * * root    /usr/local/bin/backup" >> "/etc/crontab"')

    if start_eden:
        run('/etc/init.d/uwsgi start')
        run('/etc/init.d/cherokee start')
    
    time.sleep(3)

    print "Done."


def aws_spawn(IMAGE='ami-cb66b2a2', # Debian Squeeze 32 bit base image.
            INSTANCE_TYPE = 't1.micro', 
            ZONE = 'us-east-1b',
            SECURITY_GROUPS = ['default'], # Allow all ports
            KEY_NAME = 'awskey', # YOUR SSH KEY
            TERMINATION_BEHAVIOR = None,
            NAME ='changeme',
            ):

    env.key_filename = KEY_NAME+".pem"
    regions = boto.ec2.regions()
    for region in regions:
        if region.name in ZONE:
            ec2_conn = region.connect()

    print 'Starting an EC2 instance of type {0} with image {1}'.format(INSTANCE_TYPE, IMAGE)
    reservation = ec2_conn.run_instances(IMAGE, instance_type=INSTANCE_TYPE, key_name=KEY_NAME, placement=ZONE, security_groups=SECURITY_GROUPS, instance_initiated_shutdown_behavior=TERMINATION_BEHAVIOR)
    instance = reservation.instances[0]
    ec2_conn.create_tags([instance.id], {"Name": NAME})
    print 'Checking if instance: {0} is running'.format(instance.dns_name)

    while not instance.update() == 'running':
        print "."
        time.sleep(1) # Let the instance start up

    print 'Started the instance: {0}'.format(instance.dns_name)
    return instance.dns_name


def aws_list(ZONE = 'us-east-1b'):

    regions = boto.ec2.regions()
    for region in regions:
        ec2_conn = region.connect()

        reservations = ec2_conn.get_all_instances()
        print "---------------------------------"
        print region
        print "You have the following instances:\n"
        for reservation in reservations:
            for instance in reservation.instances:
                print str(instance)+" state: "+str(instance.state)
        print "\n"


def aws_clean(ZONE = 'us-east-1b'):

    regions = boto.ec2.regions()
    for region in regions:
        if region.name in ZONE:
            ec2_conn = region.connect()

    reservations = ec2_conn.get_all_instances()
    print "You have the following instances:\n"
    for reservation in reservations:
        for instance in reservation.instances:
            if instance.state != 'terminated':
                print str(instance)+" state: "+str(instance.state)
                if raw_input("TERMINATE INSTANCE " + str(instance) +" Y/N : ") == "Y":
                    instance.terminate()
    print "\n"


def aws_postgres(IMAGE='ami-cb66b2a2', # Debian Squeeze 32 bit base image.
            INSTANCE_TYPE = 't1.micro', 
            ZONE = 'us-east-1b',
            SECURITY_GROUPS = ['default'], # Allow all ports
            KEY_NAME = 'awskey', # YOUR SSH KEY
            TERMINATION_BEHAVIOR = None,
            NAME ='changeme'
    ):
    
    machine = aws_spawn(IMAGE,INSTANCE_TYPE,ZONE,SECURITY_GROUPS,KEY_NAME,TERMINATION_BEHAVIOR,NAME)
    env.host_string = machine
    env.user = 'root' # For AWS
    env.key_filename = KEY_NAME+".pem"
    print 'Sleeping for 60 seconds to let the machine spawn.'
    time.sleep(60)
    init_env()
    drop_eden()
    install_postgres() # Install Postgres
    configure_eden_standalone(start_eden=False)
    print 'Eden Postgres now installed and running at {0}'.format(machine)
    return machine


def aws_eden_standalone(IMAGE='ami-cb66b2a2', # Debian Squeeze 32 bit base image.
            INSTANCE_TYPE = 't1.micro', 
            ZONE = 'us-east-1b',
            SECURITY_GROUPS = ['default'], # Allow all ports
            KEY_NAME = 'awskey', # YOUR SSH KEY
            TERMINATION_BEHAVIOR = None,
            NAME ='changeme'
    ):
    
    machine = aws_spawn(IMAGE,INSTANCE_TYPE,ZONE,SECURITY_GROUPS,KEY_NAME,TERMINATION_BEHAVIOR,NAME)
    env.host_string = machine
    env.user = 'root' # For AWS
    env.key_filename = KEY_NAME+".pem"
    print 'Sleeping for 60 seconds to let the machine spawn.'
    time.sleep(60)
    setup_eden()
    configure_eden_standalone()
    print 'Eden standalone now installed and running at {0}'.format(machine)
    return machine
    
def aws_import_key(key_name, public_key, ZONE='us-east-1b'): 
    # DSA keys not supported
    # 1024, 2048, and 4096 key lengths accepted.

    regions = boto.ec2.regions()
    for region in regions:
        if region.name in ZONE:
            ec2_conn = region.connect()

    public_key_material = open(public_key,'r').read()
    ec2_conn.import_key_pair(key_name, public_key_material)



