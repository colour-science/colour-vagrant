"""
colour-vagrant Fabric File
==========================
"""

from __future__ import unicode_literals

import os
from collections import namedtuple

from fabric.api import cd, run, sudo, task
from fabric.contrib.files import append, exists, is_link

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013 - 2015 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['VAGRANT_DIRECTORY',
           'HOME_DIRECTORY',
           'BASH_PROFILE_FILE',
           'SCRIPTS_DIRECTORY',
           'STORAGE_DIRECTORY',
           'REQUIRED_DEBIAN_PACKAGES',
           'SOFTWARES_URLS',
           'SCRIPTS',
           'INTERPRETERS',
           'REQUIRED_PYTHON_PACKAGES',
           'WORKSPACE_DIRECTORY',
           'Repository',
           'REPOSITORIES',
           'WEBSITE_LOCAL_DIRECTORY',
           'download',
           'system_update',
           'install_required_packages',
           'install_anaconda',
           'create_bash_profile_file',
           'source_bash_profile_file',
           'create_environments',
           'clone_repositories',
           'configure_website',
           'install_OpenImageIO',
           'install_Nodejs_toolchain']

VAGRANT_DIRECTORY = '/vagrant'
HOME_DIRECTORY = '/home/vagrant'
SCRIPTS_DIRECTORY = os.path.join(VAGRANT_DIRECTORY, 'scripts')
STORAGE_DIRECTORY = os.path.join(VAGRANT_DIRECTORY, 'tmp')

BASH_PROFILE_FILE = os.path.join(HOME_DIRECTORY, '.bash_profile')

REQUIRED_DEBIAN_PACKAGES = [
    'apache2',
    'build-essential',
    'cmake',
    'expect',
    'fontconfig',
    'g++',
    'gfortran',
    'git',
    'pandoc',
    'php5',
    'python-dev',
    'libboost-all-dev',
    'libjpeg-dev',
    'liblapack-dev',
    'libopenblas-dev',
    'libopenexr-dev',
    'libpng-dev',
    'libsm6',
    'libtiff4-dev',
    'libxrender-dev',
    'make',
    'unzip',
    'wget']

SOFTWARES_URLS = {
    'anaconda': 'https://3230d63b5fc54e62148e-c95ac804525aac4b6dba79b00b39d1d3.ssl.cf1.rackcdn.com/Anaconda3-2.4.0-Linux-x86_64.sh',
    'OpenImageIO': 'https://github.com/OpenImageIO/oiio/archive/Release-1.5.21.zip',
    'nodejs': 'http://nodejs.org/dist/v0.12.9/node-v0.12.9.tar.gz'}

SCRIPTS = {
    'anaconda_expect': os.path.join(SCRIPTS_DIRECTORY, 'anaconda_expect.exp')}

INTERPRETERS = {
    'python2.7': '2.7',
    'python3.5': '3'}

REQUIRED_PYTHON_PACKAGES = [
    'coverage',
    'flake8',
    'mock',
    'nikola',
    'nikola[extras]']

WORKSPACE_DIRECTORY = '/colour-science'

Repository = namedtuple('Repository', ('directory',
                                       'url',
                                       'add_to_python_path'))

REPOSITORIES = {
    'colour': Repository(
        os.path.join(WORKSPACE_DIRECTORY, 'colour'),
        'https://github.com/colour-science/colour.git',
        True),
    'colour-ipython': Repository(
        os.path.join(WORKSPACE_DIRECTORY, 'colour-ipython'),
        'https://github.com/colour-science/colour-ipython.git',
        False),
    'colour-science.org': Repository(
        os.path.join(WORKSPACE_DIRECTORY, 'colour-science.org'),
        'https://github.com/colour-science/colour-science.org.git',
        False)}

WEBSITE_LOCAL_DIRECTORY = os.path.join(WORKSPACE_DIRECTORY,
                                       'colour-science.org',
                                       'output')


def download(url, directory):
    """
    Downloads given url to given directory.

    Parameters
    ----------
    url : unicode
        Url to download.
    directory : unicode
        Directory to write the download to.
    """

    run('wget -P {0} {1}'.format(directory, url))


@task
def system_update():
    """
    Task for system update.
    """

    sudo('apt-get update --yes')


@task
def install_required_packages(required_packages=REQUIRED_DEBIAN_PACKAGES):
    """
    Task for required packages installation.

    Parameters
    ----------
    required_packages : array_like
        Required system packages to install.
    """

    for package in required_packages:
        sudo('apt-get install --yes {0}'.format(package))


@task
def install_anaconda(url=SOFTWARES_URLS.get('anaconda'),
                     directory=STORAGE_DIRECTORY,
                     anaconda_expect_script=SCRIPTS.get('anaconda_expect')):
    """
    Task for *Anaconda* installation.

    Parameters
    ----------
    url : unicode
        *Anaconda* installer url.
    directory : unicode
        Directory to write the download to.
    anaconda_expect_script : unicode
        *Anaconda* *expect* installation script.
    """

    anaconda_installation_directory = os.path.join(HOME_DIRECTORY, 'anaconda3')
    if not exists(anaconda_installation_directory):
        name = os.path.basename(url)
        anaconda_installer = os.path.join(directory, name)
        if not exists(anaconda_installer):
            download(url, directory)

        run('chmod +x {0}'.format(anaconda_installer))
        run('chmod +x {0}'.format(anaconda_expect_script))
        run('expect {0} {1}'.format(
            anaconda_expect_script, anaconda_installer))


@task
def create_bash_profile_file(bash_profile_file=BASH_PROFILE_FILE):
    """
    Task for the *.bash_profile* file creation.

    Parameters
    ----------
    bash_profile_file : unicode
        *.bash_profile* file path.
    """

    if not exists(bash_profile_file):
        bashrc_file = os.path.join(HOME_DIRECTORY, '.bashrc')
        append(bash_profile_file,
               'source {0}'.format(bashrc_file))
        anaconda_bin_directory = os.path.join(
            HOME_DIRECTORY, 'anaconda3/envs/python2.7/bin')
        append(bash_profile_file,
               'export PATH={0}:$PATH'.format(anaconda_bin_directory))
        python_path = ':'.join([repository.directory
                                for name, repository in REPOSITORIES.items()
                                if repository.add_to_python_path])
        append(bash_profile_file,
               'export PYTHONPATH={0}:$PYTHONPATH'.format(python_path))


@task
def source_bash_profile_file(bash_profile_file=BASH_PROFILE_FILE):
    """
    Task for sourcing the *.bash_profile* file.

    Parameters
    ----------
    bash_profile_file : unicode
        *.bash_profile* file path.
    """

    if exists(bash_profile_file):
        run('source {0}'.format(bash_profile_file))


@task
def create_environments(interpreters=INTERPRETERS,
                        packages=REQUIRED_PYTHON_PACKAGES):
    """
    Task for virtual *Anaconda* environments.

    Parameters
    ----------
    interpreters : dict
        *Python* interpreters to create.
    packages : array_like
        Required *Python* packages to install.
    """

    for interpreter, version in interpreters.items():
        anaconda_environment_directory = os.path.join(
            HOME_DIRECTORY, 'anaconda/envs', interpreter)
        if not exists(anaconda_environment_directory):
            run('conda create --yes -n {0} python={1} anaconda'.format(
                interpreter, version))
            run('source activate {0} && pip install {1}'.format(
                interpreter, " ".join(packages)))


@task
def clone_repositories(repositories=REPOSITORIES,
                       workspace_directory=WORKSPACE_DIRECTORY):
    """
    Task for *Git* repositories to clone.

    Parameters
    ----------
    repositories : dict
        *Git* repositories to clone
    workspace_directory : unicode
        Workspace directory to clone the *Git* repositories into.
    """

    with cd(workspace_directory):
        for name, repository in repositories.items():
            if not exists(repository.directory):
                run('git clone {0} {1}'.format(repository.url,
                                               repository.directory),
                    repository.directory)
                with cd(repository.directory):
                    run('git remote rename origin upstream')


@task
def configure_website(website_local_directory=WEBSITE_LOCAL_DIRECTORY):
    """
    Task for *colour-science.local* website configuration.

    Parameters
    ----------
    website_local_directory : unicode
        Website local directory.
    """

    provider_directory = '/var/www'
    if not is_link(provider_directory):
        sudo(('sed -i "s/AllowOverride None/AllowOverride All/g" '
              '/etc/apache2/apache2.conf'))
        sudo(('sed -i "s|/usr/lib/cgi-bin|/var/www/cgi-bin|g" '
              '/etc/apache2/sites-enabled/000-default'))
        sudo('rm -rf {0}'.format(provider_directory))
        sudo('ln -fs {0} {1}'.format(
            website_local_directory, provider_directory))
        sudo('a2enmod rewrite')
        sudo('service apache2 restart')


@task
def install_OpenImageIO(url=SOFTWARES_URLS.get('OpenImageIO'),
                        directory=STORAGE_DIRECTORY):
    """
    Task for *OpenImageIO* installation.

    Parameters
    ----------
    url : unicode
        *OpenImageIO* installer url.
    directory : unicode
        Directory to write the download to.
    """

    name = os.path.basename(url)
    OpenImageIO_installer = os.path.join(directory, name)
    OpenImageIO_directory = os.path.join(
        directory, 'oiio-{0}'.format(os.path.splitext(name)[0]))

    if not exists(OpenImageIO_directory):
        if not exists(OpenImageIO_installer):
            download(url, directory)

        with cd(STORAGE_DIRECTORY):
            run('unzip {0}'.format(OpenImageIO_installer))

        with cd(OpenImageIO_directory):
            run('make')

        with cd(os.path.join(OpenImageIO_directory, 'dist', 'linux64')):
            sudo('cp bin/* /usr/local/bin/')
            sudo('cp lib/* /usr/local/lib/')

        anaconda_site_package_directory = os.path.join(
            HOME_DIRECTORY,
            'anaconda3/envs/python2.7/lib/python2.7/site-packages')
        OpenImageIO_python_library = os.path.join(
            OpenImageIO_directory, 'dist/linux64/python/OpenImageIO.so')

        with cd(anaconda_site_package_directory):
            run('cp {0} .'.format(OpenImageIO_python_library))


@task
def install_Nodejs_toolchain(url=SOFTWARES_URLS.get('nodejs'),
                             directory=STORAGE_DIRECTORY):
    """
    Task for *Nodejs* toolchain installation.

    Parameters
    ----------
    url : unicode
        *Nodejs* installer url.
    directory : unicode
        Directory to write the download to.
    """

    name = os.path.basename(url)
    nodejs_installer = os.path.join(directory, name)
    nodejs_directory = os.path.join(
        directory, os.path.splitext(os.path.splitext(name)[0])[0])

    if not exists(nodejs_directory):
        if not exists(nodejs_installer):
            download(url, directory)

        with cd(STORAGE_DIRECTORY):
            run('tar -xvf {0}'.format(nodejs_installer))

        with cd(nodejs_directory):
            run('./configure')
            run('make')
            sudo('make install')

        sudo('npm install -g grunt-cli')
