from setuptools import setup, find_packages

# '../../../Product/x86_64-linux.release/out/lib/' 경로에서 모든 .so 파일을 수집

setup(
    name='SG1AB',
    version='0.1.7',
    description='nnfw_api binding',
    long_description='you can use nnfw_api by python',
    url='https://github.com/Samsung/ONE/tree/master/runtime',
    author='Your Name',
    author_email='your@email.com',
    license='Samsung',
    packages=find_packages(),
    package_data={'SSG1AB' : ['../../../Product/x86_64-linux.release/out/lib/nnfw_api_pybind.so','../../../Product/x86_64-linux.release/out/lib/libnnfw-dev.so', '../../../Product/x86_64-linux.release/out/lib/libonert_core.so', '../../../Product/x86_64-linux.release/out/lib/libbackend_cpu.so']},
    install_requires=[
        # 필요한 의존성 패키지를 여기에 추가
    ],
)

