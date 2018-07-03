import os.path

from setuptools import setup

install_requires=['cffi>=1.0.0']

dirname = os.path.dirname(os.path.abspath(__file__))

setup(
    name='kafka_cffi',
    version='0.1',
    description='A CFFI binding for librdkafka',
    author='Wenxiang Wu',
    author_email='thewrongboy@gmail.com ',
    url='https://github.com/wenxiang/cffi_kafka',
    license='MIT',
    packages=['kafka_cffi'],
    setup_requires=install_requires,
    install_requires=install_requires,
    cffi_modules=['build_ffi.py:ffi'],
)