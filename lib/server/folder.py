import getpass
import os

from datetime import datetime

from lib.site.info import SSL_CERT_NAME
from lib.site.info import SSL_SERVER_KEY


class FolderInfoError(Exception):

    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return repr('%s, %s' % (self.__class__.__name__, self.value))


class FolderInfo(object):
    """
    Standard folder names for deploying projects and for running fabric
    commands
    """

    def __init__(self, site_name, version=None):
        self.site_name = site_name
        if version:
            self.date_folder = self._get_date_folder(version)
        else:
            self.date_folder = None

    def _get_date_folder(self, version):
        return '{}__{}_{}'.format(
            version.replace('.', '_'),
            datetime.now().strftime('%Y%m%d_%H%M%S'),
            getpass.getuser()
        )

    def _repo(self):
        return '/home/web/repo'

    def deploy(self):
        return os.path.join(self.site(), 'deploy')

    def install(self):
        if not self.date_folder:
            raise FolderInfoError(
                "Cannot return an install folder if the class wasn't "
                "constructed with a version number e.g. '0.2.32'"
            )
        return os.path.join(self.deploy(), self.date_folder)

    def install_temp(self):
        return os.path.join(self.install(), 'temp')

    def install_venv(self):
        return os.path.join(self.install(), 'venv')

    def live(self):
        return os.path.join(self.site(), 'live')

    def live_venv(self):
        return os.path.join(self.live(), 'venv')

    def site(self):
        return os.path.join(
            self._repo(),
            'project',
            self.site_name,
        )

    def ssl_cert(self):
        return os.path.join(self.ssl_cert_folder(), SSL_CERT_NAME)

    def ssl_server_key(self):
        return os.path.join(self.ssl_cert_folder(), SSL_SERVER_KEY)

    def ssl_cert_folder(self):
        return os.path.join(self.ssl_folder(), self.site_name)

    def ssl_folder(self):
        return os.path.join(self.srv_folder(), 'ssl')

    def srv_folder(self):
        return os.path.join('/', 'srv')

    def vassal(self):
        return os.path.join(
            self._repo(),
            'uwsgi',
            'vassals',
            '{}.ini'.format(self.site_name)
        )
