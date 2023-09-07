# {# pkglts, pysetup.kwds
# format setup arguments
from pathlib import Path
from setuptools import setup, find_packages

short_descr = "Set of formalisms around black bodies"
readme = open('README.rst').read()
history = open('HISTORY.rst').read()

# find packages
pkgs = find_packages('src')

src_dir = Path("src/black_body")

data_files = []
for pth in src_dir.rglob("*"):
    if not pth.is_dir() and "__pycache__" not in pth.parts:
        if pth.suffix in ['.json', '.ini', '.csv', '.rst', '.svg']:
            data_files.append(str(pth.relative_to(src_dir)))

pkg_data = {'black_body': data_files}

setup_kwds = dict(
    name='black_body',
    version="1.1.0",
    description=short_descr,
    long_description=readme + '\n\n' + history,
    author="revesansparole",
    author_email="revesansparole@gmail.com",
    url='https://gitlab.com/revesansparole/black_body',
    license='cc_by_nc',
    zip_safe=False,

    packages=pkgs,
    
    package_dir={'': 'src'},
    
    
    package_data=pkg_data,
    setup_requires=[
        "pytest-runner",
        ],
    install_requires=[
        ],
    tests_require=[
        "coverage",
        "pytest",
        "pytest-cov",
        "pytest-mock",
        ],
    entry_points={},
    keywords='',
    
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.9",
    ],
    )
# #}
# change setup_kwds below before the next pkglts tag

# do not change things below
# {# pkglts, pysetup.call
setup(**setup_kwds)
# #}
