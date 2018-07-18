import os.path

from setuptools import setup

install_requires=["cffi>=1.0.0", "six"]

dirname = os.path.dirname(os.path.abspath(__file__))

setup(
    name="kafka-cffi",
    version="0.11.4b1",
    description="A CFFI binding for librdkafka",
    author="Wenxiang Wu",
    author_email="thewrongboy@gmail.com",
    url="https://github.com/wenxiang/cffi_kafka",
    license="MIT",
    package_dir={"": "src"},
    packages=["kafka_cffi"],
    setup_requires=install_requires,
    install_requires=install_requires,
    cffi_modules=["src/build_ffi.py:ffi"],
)
