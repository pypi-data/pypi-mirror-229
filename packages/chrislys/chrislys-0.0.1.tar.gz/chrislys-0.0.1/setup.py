from setuptools import find_packages, setup
setup(
    name='chrislys',
    packages=find_packages(include=['chrislys']),
    version='0.0.1',
    description='test qualys library',
    author='Chris Nam',
    license='MIT',
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)