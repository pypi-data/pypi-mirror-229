import glob
from setuptools import setup, Extension, find_packages

# '../../../Product/x86_64-linux.release/out/lib/' 경로에서 모든 .so 파일을 수집
so_files = glob.glob('../../../Product/x86_64-linux.release/out/lib/*.so')

setup(
    name='SG1AB',
    version='0.1.1',
    description='nnfw_api binding',
    long_description='you can use nnfw_api by python',
    url='https://github.com/Samsung/ONE/tree/master/runtime',
    author='Your Name',
    author_email='your@email.com',
    license='Samsung',
    packages=find_packages(),
    ext_modules=[
        Extension(
            'SG1AB',
            sources=so_files,  # 수집한 .so 파일 목록 사용
        )
    ],
    install_requires=[
        # 필요한 의존성 패키지를 여기에 추가
    ],
)

