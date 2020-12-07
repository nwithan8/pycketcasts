import setuptools
import pycketcasts._info as package_info

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", 'r') as fh:
    requirements = fh.read().splitlines()

setuptools.setup(
    name=package_info.__title__,  # How you named your package folder (MyLib)
    packages=[package_info.__title__],  # Choose the same as "name"
    version=package_info.__version__,  # Start with a small number and increase it with every change you make
    license=package_info.__license__,
    description="Interact with PocketCast's unofficial API",  # Give a short description about your library
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=package_info.__author__,  # Type in your name
    author_email=package_info.__author_email__,  # Type in your E-Mail
    url=f'https://github.com/nwithan8/{package_info.__title__}',  # Provide either the link to your github or to your website
    download_url=f'https://github.com/nwithan8/{package_info.__title__}/archive/{package_info.__version__}.tar.gz',
    keywords=[
        'PocketCasts',
        'podcast',
        'podcasts',
        'API',
        'Home Assistant',
        'library'
    ],  # Keywords that define your package best
    install_requires=requirements,
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Development Status :: 4 - Beta',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3',  # Specify which python versions that you want to support
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia',
        'Topic :: Internet :: WWW/HTTP',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.6'
)