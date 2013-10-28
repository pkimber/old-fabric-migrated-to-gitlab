from fabric.api import cd
from fabric.api import abort
from fabric.api import prompt
from fabric.api import env
from fabric.api import get
from fabric.api import local
from fabric.api import put
from fabric.api import run
from fabric.api import sudo
from fabric.api import task
from fabric.colors import green
from fabric.colors import yellow
from fabric.contrib.files import exists

from lib.backup.path import Path
from lib.manage.command import DjangoCommand
from lib.server.folder import FolderInfo
from lib.site.info import SiteInfo


env.use_ssh_config = True
FILES = 'files'
POSTGRES = 'postgres'


def _local_database_exists(database_name):
    import psycopg2
    conn = psycopg2.connect('dbname={0} user={0}'.format('postgres'))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pg_database WHERE datname='{}'".format(database_name))
    return cursor.fetchone()


def _local_postgres_user_exists(database_name):
    """ Return some data if the user exists, else 'None' """
    import psycopg2
    conn = psycopg2.connect('dbname={0} user={0}'.format('postgres'))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pg_user WHERE usename = '{0}'".format(database_name))
    return cursor.fetchone()


@task
def backup_db(site_name):
    """
    To backup the 'csw_web' database on the 'rs.web' server:
    fab -H rs.db backup_db:csw_web
    """
    print(green("Backup '{}' on '{}'").format(site_name, env.host_string))
    path = Path(site_name, 'postgres')
    run('mkdir -p {0}'.format(path.remote_folder()))
    run('pg_dump -U postgres {0} -f {1}'.format(
        site_name, path.remote_file()
        ))
    get(path.remote_file(), path.local_file())
    print(green("restore to test database"))
    if _local_database_exists(path.test_database_name()):
        local('psql -X -U postgres -c "DROP DATABASE {0}"'.format(path.test_database_name()))
    local('psql -X -U postgres -c "CREATE DATABASE {0} TEMPLATE=template0 ENCODING=\'utf-8\';"'.format(path.test_database_name()))
    if not _local_postgres_user_exists(site_name):
        local('psql -X -U postgres -c "CREATE ROLE {0} WITH PASSWORD \'{1}\' NOSUPERUSER CREATEDB NOCREATEROLE LOGIN;"'.format(site_name, site_name))
    local("psql -X --set ON_ERROR_STOP=on -U postgres -d {0} --file {1}".format(
        path.test_database_name(), path.local_file()), capture=True
    )
    local('psql -X -U postgres -d {} -c "REASSIGN OWNED BY {} TO {}"'.format(
        path.test_database_name(), site_name, path.user_name()
    ))
    print(green("psql {}").format(path.test_database_name()))


@task
def backup_files():
    """
    To backup the files 'rs.connexionsw' server:
    fab -H rs.web.connexionsw backup_files
    """
    print(green("Backup files on '{}'").format(env.host_string))
    name = env.host_string.replace('.', '_')
    name = name.replace('-', '_')
    path = Path(name, 'files')
    run('mkdir -p {0}'.format(path.remote_folder()))
    with cd(path.files_folder()):
        run('tar -cvzf {} .'.format(path.remote_file()))
    get(path.remote_file(), path.local_file())


@task
def create_db(prefix, site_name, table_space):
    """
    Note: table space 'cbs' is the name we have given to the Rackspace Cloud Block Storage volume.
    If you are not using cloud block storage, then leave the ``table_space`` parameter empty.

    e.g.
    fab -H 37.239.28.222 create_db:prefix=pkimber,site_name=hatherleigh_net,table_space=
    fab -H 37.239.28.222 create_db:prefix=pkimber,site_name=hatherleigh_net,table_space=cbs

    psql parameters:
    -X  Do not read the start-up file
    """
    print(green("create '{}' database on '{}'").format(site_name, env.host_string))
    site_info = SiteInfo(prefix, site_name)
    #run('psql -X -U postgres -c "DROP DATABASE {};"'.format(site_name))
    run('psql -X -U postgres -c "CREATE ROLE {} WITH PASSWORD \'{}\' NOSUPERUSER CREATEDB NOCREATEROLE LOGIN;"'.format(
        site_name, site_info.password()
        ))
    parameter = ''
    if table_space:
        print(yellow("using block storage, table space {}...".format(table_space)))
        parameter = 'TABLESPACE={}'.format(table_space)
    run('psql -X -U postgres -c "CREATE DATABASE {} WITH OWNER={} TEMPLATE=template0 ENCODING=\'utf-8\' {};"'.format(
        site_name, site_name, parameter,
        ))
    print(green('done'))


@task
def db_version():
    """
    To find the Postgres version install on 'rs.db':
    fab -H rs.db db_version
    """
    print(green("Postgres version installed on '{0}'").format(env.host_string))
    run('psql -X -U postgres -c "SELECT VERSION();"')


@task
def haystack_index(prefix, name):
    """
    e.g:
    fab -H web@rs.web.connexionsw haystack_index:prefix=pkimber,name=csw_web
    """
    print(green("Haystack - reindex: '{}' on '{}' ").format(
        name, env.host_string)
    )
    site_info = SiteInfo(prefix, name)
    folder_info = FolderInfo(name)
    command = DjangoCommand(
        folder_info.live(),
        folder_info.live_venv(),
        site_info
    )
    command.haystack_index()


@task
def haystack_index_clear(prefix, name):
    """
    e.g:
    fab -H web@rs.web.connexionsw haystack_index:prefix=pkimber,name=csw_web
    """
    print(green("Haystack - reindex: '{}' on '{}' ").format(
        name, env.host_string)
    )
    confirm = ''
    while confirm not in ('Y', 'N'):
        confirm = prompt("Are you sure you want to clear the Haystack index (Y/N)?")
        confirm = confirm.strip().upper()
    if not confirm == 'Y':
        abort("exit")
    site_info = SiteInfo(prefix, name)
    folder_info = FolderInfo(name)
    command = DjangoCommand(
        folder_info.live(),
        folder_info.live_venv(),
        site_info
    )
    command.haystack_index_clear()


@task
def valid(prefix, name):
    """ For docs, see https://github.com/pkimber/docs """
    SiteInfo(prefix, name)
    print(green("The configuration for '{0}' appears to be valid").format(name))


@task
def solr_status():
    print(green("SOLR status: '{0}'").format(env.host_string))
    #run('curl http://localhost:8080/solr/status/')
    run('curl http://localhost:8080/solr/')
    #run('psql -X -U postgres -c "SELECT VERSION();"')


@task
def ssl_cert(prefix, site_name):
    """
    fab -H server ssl_cert:prefix=pkimber,name=hatherleigh_net
    """
    site_info = SiteInfo(prefix, site_name)
    if not site_info.ssl():
        abort("'{}' is not set-up for SSL in the Salt pillar".format(site_name))
    folder_info = FolderInfo(site_name)
    if not exists(folder_info.srv_folder(), use_sudo=True):
        abort("{} folder does not exist on the server".format(folder_info.srv_folder()))
    if exists(folder_info.ssl_folder(), use_sudo=True):
        print(green("SSL folder exists: {}".format(folder_info.ssl_folder())))
    else:
        print(green("Create SSL folder: {}".format(folder_info.ssl_folder())))
        sudo('mkdir {}'.format(folder_info.ssl_folder()))
        sudo('chown www-data:www-data {}'.format(folder_info.ssl_folder()))
        sudo('chmod 0400 {}'.format(folder_info.ssl_folder()))
    if exists(folder_info.ssl_cert_folder(), use_sudo=True):
        print(green("Certificate folder exists: {}".format(folder_info.ssl_cert_folder())))
    else:
        print(green("Create certificate folder: {}".format(folder_info.ssl_cert_folder())))
        sudo('mkdir {}'.format(folder_info.ssl_cert_folder()))
        sudo('chown www-data:www-data {}'.format(folder_info.ssl_cert_folder()))
        sudo('chmod 0400 {}'.format(folder_info.ssl_cert_folder()))
    put(
        site_info.ssl_cert(),
        folder_info.ssl_cert(),
        use_sudo=True,
        mode=0400,
    )
    sudo('chown www-data:www-data {}'.format(folder_info.ssl_cert()))
    print(green(folder_info.ssl_cert()))
    put(
        site_info.ssl_server_key(),
        folder_info.ssl_server_key(),
        use_sudo=True,
        mode=0400,
    )
    sudo('chown www-data:www-data {}'.format(folder_info.ssl_server_key()))
    print(green(folder_info.ssl_server_key()))
    print(yellow("Complete"))