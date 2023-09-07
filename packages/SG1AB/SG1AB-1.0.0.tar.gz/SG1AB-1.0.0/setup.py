from setuptools import setup, find_packages
import os
import shutil

source_directory = '../../Product/x86_64-linux.release/out/lib/'
target_directory = 'SG1AB'

if os.path.exists(target_directory):
    shutil.rmtree(target_directory)

os.makedirs(target_directory)

for filename in os.listdir(source_directory):
    source_file = os.path.join(source_directory, filename)
    if os.path.isfile(source_file) and source_file.endswith('.so'):
        shutil.copy(source_file, target_directory)

setup(
    name=target_directory,
    version='1.0.0',
    description='nnfw_api binding',
    long_description='you can use nnfw_api by python',
    url='https://github.com/Samsung/ONE/tree/master/runtime',
    author='Your Name',
    author_email='your@email.com',
    license='Samsung',
    packages=[target_directory],
    package_data={target_directory: ['nnfw_api_pybind.cpython-38-x86_64-linux-gnu.so', 'libnnfw-dev.so', 'libonert_core.so', 'libbackend_cpu.so']},
    install_requires=[
        # 필요한 의존성 패키지를 여기에 추가
    ],
)

