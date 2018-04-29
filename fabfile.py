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
__copyright__ = 'Copyright (C) 2013-2018 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = [
    'VAGRANT_DIRECTORY', 'HOME_DIRECTORY', 'BASH_PROFILE_FILE',
    'SCRIPTS_DIRECTORY', 'STORAGE_DIRECTORY', 'REQUIRED_DEBIAN_PACKAGES',
    'SOFTWARES_URLS', 'SCRIPTS', 'INTERPRETERS',
    'REQUIRED_CONDA_PYTHON_PACKAGES', 'REQUIRED_PIP_PYTHON_PACKAGES',
    'WORKSPACE_DIRECTORY', 'Repository', 'REPOSITORIES',
    'WEBSITE_LOCAL_DIRECTORY', 'download', 'system_update',
    'install_required_packages', 'install_conda', 'create_bash_profile_file',
    'source_bash_profile_file', 'create_environments', 'clone_repositories',
    'configure_website', 'install_OpenImageIO'
]

VAGRANT_DIRECTORY = '/vagrant'
HOME_DIRECTORY = '/home/vagrant'
SCRIPTS_DIRECTORY = os.path.join(VAGRANT_DIRECTORY, 'scripts')
STORAGE_DIRECTORY = os.path.join(VAGRANT_DIRECTORY, 'tmp')

BASH_PROFILE_FILE = os.path.join(HOME_DIRECTORY, '.bash_profile')

# Base
REQUIRED_DEBIAN_PACKAGES = [
    'unzip',
    'wget',
]

# Repositories
REQUIRED_DEBIAN_PACKAGES += [
    'git',
]

# Website
REQUIRED_DEBIAN_PACKAGES += [
    'apache2',
    'pandoc',
]

# Development
REQUIRED_DEBIAN_PACKAGES += [
    'cmake', 'build-essential', 'make', 'python3.5-dev'
]

# OpenImageIO
REQUIRED_DEBIAN_PACKAGES += [
    'libboost-all-dev',
    'libbz2-dev',
    # 'libfield3d-dev',  # Is not found.
    'libgif-dev',
    'libfreetype6-dev',
    'libilmbase-dev',
    'libjpeg-dev',
    'libopenexr-dev',
    # 'libopencv-dev',  # Does not build.
    'libopenjpeg-dev',
    'libpng-dev',
    'libraw-dev',
    'libtiff5-dev',
    'libwebp-dev',
    'qtbase5-dev',
]

SOFTWARES_URLS = {
    'anaconda':
    'https://repo.continuum.io/miniconda/Miniconda3-4.4.10-Linux-x86_64.sh',
    'OpenImageIO':
    'https://github.com/OpenImageIO/oiio/archive/Release-1.8.10.zip'
}

SCRIPTS = {}

INTERPRETERS = {'python2.7': '2.7', 'python3.5': '3.5'}

CONDA_DIRECTORY = os.path.join(HOME_DIRECTORY, 'miniconda')

REQUIRED_CONDA_PYTHON_PACKAGES = [
    'coverage',
    'flake8',
    'matplotlib',
    'mock',
    'nose',
    'numpy',
    'pandas',
    'scipy',
    'six',
    'sphinx',
    'twine',
    'yapf',
]

REQUIRED_PIP_PYTHON_PACKAGES = [
    'invoke',
    'nikola',
    'nikola[extras]',
    'restructuredtext_lint',
    'sphinxcontrib-bibtex',
    'sphinx_rtd_theme',
]

WORKSPACE_DIRECTORY = '/colour-science'

Repository = namedtuple('Repository',
                        ('directory', 'url', 'add_to_python_path'))

REPOSITORIES = {
    'colour':
    Repository(
        os.path.join(WORKSPACE_DIRECTORY, 'colour'),
        'https://github.com/colour-science/colour.git', True),
    'colour-notebooks':
    Repository(
        os.path.join(WORKSPACE_DIRECTORY, 'colour-notebooks'),
        'https://github.com/colour-science/colour-notebooks.git', False),
    'colour-science.org':
    Repository(
        os.path.join(WORKSPACE_DIRECTORY, 'colour-science.org'),
        'https://github.com/colour-science/colour-science.org.git', False)
}

WEBSITE_LOCAL_DIRECTORY = os.path.join(WORKSPACE_DIRECTORY,
                                       'colour-science.org', 'output')


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

    if not exists('~/.system_is_updated'):
        sudo('apt-get update --yes')
        sudo('touch ~/.system_is_updated')

    sudo('apt-get install --yes unattended-upgrades')
    sudo('unattended-upgrades')


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
def install_conda(
        url=SOFTWARES_URLS.get('anaconda'), directory=STORAGE_DIRECTORY):
    """
    Task for *Anaconda* installation.

    Parameters
    ----------
    url : unicode
        *Anaconda* installer url.
    directory : unicode
        Directory to write the download to.
    """

    if not exists(CONDA_DIRECTORY):
        name = os.path.basename(url)
        conda_installer = os.path.join(directory, name)
        if not exists(conda_installer):
            download(url, directory)

        run('chmod +x {0}'.format(conda_installer))
        run('{0} -b -p {1}'.format(conda_installer, CONDA_DIRECTORY))


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
        append(bash_profile_file, 'source {0}'.format(bashrc_file))

        conda_bin_directory = os.path.join(CONDA_DIRECTORY, 'bin')
        append(bash_profile_file,
               'export PATH={0}:$PATH'.format(conda_bin_directory))
        python_path = ':'.join([
            repository.directory for name, repository in REPOSITORIES.items()
            if repository.add_to_python_path
        ])
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
                        conda_packages=REQUIRED_CONDA_PYTHON_PACKAGES,
                        pip_packages=REQUIRED_PIP_PYTHON_PACKAGES):
    """
    Task for virtual *Anaconda* environments.

    Parameters
    ----------
    interpreters : dict
        *Python* interpreters to create.
    conda_packages : array_like
        Required *Conda* *Python* packages to install.
    pip_packages : array_like
        Required *Pip* *Python* packages to install.
    """

    for interpreter, version in interpreters.items():
        conda_environment_directory = os.path.join(CONDA_DIRECTORY, 'envs',
                                                   interpreter)
        if not exists(conda_environment_directory):
            run('{0} create --yes -n {1} python={2} anaconda'.format(
                os.path.join(HOME_DIRECTORY, 'miniconda', 'bin', 'conda'),
                interpreter, version))
            run('source activate {0} && conda install --yes {1}'.format(
                interpreter, " ".join(conda_packages)))
            run('source activate {0} && pip install {1}'.format(
                interpreter, " ".join(pip_packages)))


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

    provider_directory = '/var/www/html'
    if not is_link(provider_directory):
        sudo(('sed -i "s/AllowOverride None/AllowOverride All/g" '
              '/etc/apache2/apache2.conf'))
        sudo(('sed -i "s|/usr/lib/cgi-bin|/var/www/html/cgi-bin|g" '
              '/etc/apache2/sites-enabled/000-default.conf'))
        sudo('rm -rf {0}'.format(provider_directory))
        sudo('ln -fs {0} {1}'.format(website_local_directory,
                                     provider_directory))
        sudo('a2enmod rewrite')
        sudo('service apache2 restart')


@task
def install_OpenImageIO(
        url=SOFTWARES_URLS.get('OpenImageIO'), directory=STORAGE_DIRECTORY):
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
    OpenImageIO_directory = os.path.join(directory, 'oiio-{0}'.format(
        os.path.splitext(name)[0]))

    if not exists(OpenImageIO_directory):

        with cd('/usr/lib/x86_64-linux-gnu'):
            for library in [
                    'libboost_mpi_python.a',
                    'libboost_mpi_python-py27.a',
                    'libboost_mpi_python-py27.so',
                    'libboost_mpi_python-py27.so.1.58.0',
                    'libboost_mpi_python.so',
                    'libboost_python.a',
                    'libboost_python-py27.a',
                    'libboost_python-py27.so',
                    'libboost_python-py27.so.1.58.0',
                    'libboost_python.so',
            ]:
                sudo('mv {0} {0}.colour-vagrant.old'.format(library))

            sudo('ln -s libboost_mpi_python-py35.a libboost_mpi_python.a')
            sudo('ln -s libboost_python-py35.a libboost_python.a')

            sudo('ln -s libboost_mpi_python-py35.so libboost_mpi_python.so')
            sudo('ln -s libboost_python-py35.so libboost_python.so')

        if not exists(OpenImageIO_installer):
            download(url, directory)

        with cd(STORAGE_DIRECTORY):
            run('unzip {0}'.format(OpenImageIO_installer))

        with cd(OpenImageIO_directory):
            run('make PYTHON_VERSION=3.5')

        with cd(os.path.join(OpenImageIO_directory, 'dist', 'linux64')):
            sudo('cp bin/* /usr/local/bin/')
            sudo('cp lib/*.so* /usr/local/lib/')

        conda_site_package_directory = os.path.join(
            CONDA_DIRECTORY, 'envs', 'python3.5', 'lib', 'python3.5',
            'site-packages')
        OpenImageIO_python_library = os.path.join(
            OpenImageIO_directory, 'dist', 'linux64', 'lib', 'python3.5',
            'site-packages', 'OpenImageIO.so')

        run('cp {0} {1}'.format(OpenImageIO_python_library,
                                conda_site_package_directory))
