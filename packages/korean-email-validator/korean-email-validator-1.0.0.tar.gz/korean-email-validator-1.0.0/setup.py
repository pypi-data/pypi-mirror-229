from setuptools import setup, find_packages

setup(
    name='korean-email-validator',
    version='1.0.0',
    description='이메일 유효성 검증 패키지로, 한국어로 이메일 유효성 검증 결과를 반환합니다.',
    author='Kim Ain',
    author_email='kimain0401@kakao.com',
    url='https://github.com/kimain050401/korean-email-validator',
    install_requires=['re'],
    packages=find_packages(exclude=[]),
    keywords=['kimain', 'corondev', 'email', 'email validator', 'email verify', 'email check', 'email checker'],
    python_requires='>=3.6',
    package_data={},
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)