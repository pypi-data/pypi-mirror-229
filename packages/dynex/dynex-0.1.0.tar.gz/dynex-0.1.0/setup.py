from setuptools import setup

setup(
    name='dynex',
    version='0.1.0',    
    description='Dynex SDK Neuromorphic Computing',
    url='https://github.com/dynexcoin/DynexSDK',
    author='Dynex Developers',
    author_email='office@dynexcoin.org',
    license='GPLv3',
    packages=['dynex'],
    install_requires=['pycryptodome>=3.18.0',
                      'dimod>=0.12.10',
                      'tabulate>=0.9.0',
                      'tqdm>=4.65.0',
                      'ipywidgets>=8.0.7',
                      'numpy'
                      ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',  
        'Operating System :: POSIX :: Linux',     
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3 :: Only',
        'Natural Language :: English',
        'Topic :: System :: Distributed Computing',
    ],
)


