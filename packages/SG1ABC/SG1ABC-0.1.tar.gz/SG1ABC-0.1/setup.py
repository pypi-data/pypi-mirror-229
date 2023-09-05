#import glob
from setuptools import setup, Extension

#so_files = glob.glob('../../../Product/x86_64-linux.release/out/lib/*.so')

setup(
    name='SG1ABC',            # 패키지 이름
    version='0.1',                # 패키지 버전
    description='nnfw_api binding',  # 패키지 설명
    long_description='you can use nnfw_api by python',  # 자세한 설명
    url='https://github.com/Samsung/ONE/tree/master/runtime',   # 패키지 저장소 URL
    author='',           # 패키지 저자 이름
    author_email='',  # 저자 이메일 주소
    license='Samsung',            # 패키지 라이선스 (예: MIT)
    packages=['api/src'],      # 패키지 포함
    ext_modules=[
        Extension(
            'SG1ABC',  # Python 모듈 이름
            #sources=so_files,    
            sources=['../../../Product/x86_64-linux.release/out/lib/nnfw_api_pybind.cpython-38-x86_64-linux-gnu.so'],
            # 다른 빌드 옵션 추가
        )
    ],
    install_requires=[            # 패키지의 의존성 목록
        # 다른 패키지를 여기에 추가
    ],
)
