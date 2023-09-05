import os
import sys

from setuptools import find_packages, setup

# package version
__version__ = '0.0.0'


def get_version(package_path):
    try:
        libinfo_py = os.path.join(package_path, '__init__.py')
        libinfo_content = open(libinfo_py, 'r', encoding='utf8').readlines()
        version_line = [
            line.strip() for line in libinfo_content if line.startswith('__version__')
        ][0]
        return version_line.split('=')[-1].strip().strip('"').strip("'")
    except FileNotFoundError:
        pass


def get_requiments(package_name):
    with open(f'requirements.{package_name}.txt') as f:
        lines = [
            line.strip()
            for line in f.read().splitlines()
            if not line.strip().startswith('#')
        ]
        return lines


if '--package' in sys.argv:
    index = sys.argv.index('--package')
    package = sys.argv[index + 1]
    sys.argv.remove('--package')
    sys.argv.remove(package)
else:
    package = 'schema'


if package == 'schema':
    _name = 'api_schema'

    _version = get_version('api_schema')
    _packages = find_packages(include=['api_schema'])
    _dependencies = get_requiments('schema')
    _description = 'The schemas for the Jina Serving API'
    _long_description = ''
elif package == 'gateway':

    _name = 'api_gateway'
    _version = get_version('api_gateway')
    _packages = find_packages(include=['api_gateway'])
    _dependencies = get_requiments('gateway')
    _description = 'The API gateway for the Jina Serving'
    _long_description = ''
else:
    raise ValueError(f'Unknown package name \'{package}\'')


if __name__ == '__main__':
    setup(
        name=f'jinaai_{_name}',
        packages=_packages,
        version=_version,
        include_package_data=True,
        description=_description,
        author='Jina AI',
        author_email='hello@jina.ai',
        license='Proprietary',
        download_url='https://github.com/jina-ai/jinaai-api-schema/tags',
        long_description=_long_description,
        long_description_content_type='text/markdown',
        zip_safe=False,
        setup_requires=['setuptools>=18.0', 'wheel'],
        install_requires=_dependencies,
        python_requires='>=3.8.0',
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'Intended Audience :: Education',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Environment :: Console',
            'Operating System :: OS Independent',
            'Topic :: Scientific/Engineering :: Artificial Intelligence',
        ],
        project_urls={
            'Source': 'https://github.com/jina-ai/jinaai-api-schema.fit/',
            'Tracker': 'https://github.com/jina-ai/jinaai-api-schema/issues',
        },
    )
