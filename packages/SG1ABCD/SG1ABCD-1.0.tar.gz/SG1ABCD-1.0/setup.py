from setuptools import setup

setup(
    name='SG1ABCD',
    version='1.0',
    packages=['SG1ABCD'],
    package_data={'SG1ABCD': ['nnfw_api_pybind.cpython-38-x86_64-linux-gnu.so']},
    install_requires=[
        # 필요한 패키지 목록
    ],
)
