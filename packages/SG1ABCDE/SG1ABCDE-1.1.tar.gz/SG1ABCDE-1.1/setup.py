from setuptools import setup

setup(
    name='SG1ABCDE',
    version='1.1',
    packages=['SG1ABCDE'],
    package_data={'SG1ABCDE': ['nnfw_api_pybind.cpython-38-x86_64-linux-gnu.so', 'libbackend_cpu.so', 'libbackend_ruy.so', 'libbackend_train.so', 'libneuralnetworks.so', 'libnnfw-dev.so']},
    install_requires=[
        # 필요한 패키지 목록
    ],
)
