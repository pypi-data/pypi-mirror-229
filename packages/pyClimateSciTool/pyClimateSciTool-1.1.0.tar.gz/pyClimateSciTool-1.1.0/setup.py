from setuptools import find_packages, setup

VERSION = '1.1.0'
DESCRIPTION = 'A toolkit including useful functions for climate science'
setup(
    name='pyClimateSciTool',
    version='1.1.0',
    author='HE Yanfeng',
    author_email='412694462@qq.com',
    description=DESCRIPTION,
    packages=find_packages(include=['pyClimateSciTool']),
    install_requires=[],
    keywords=['python','climate science','climate data processing'],
    license='MIT',
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests'
)