from setuptools import setup

"""
The setup script.
"""

setup(
    name='Autotest_api',
    url='https://github.com/leo/Autotest_api',
    version='v1.0.4',
    author="QA-leo",
    author_email='994991952@qq.com',
    description='http/https API run by yaml',
    long_description=open("README.rst", encoding='utf-8').read(),
    package_dir={"": "src"},
    packages=["Autotest_api"],
    classifiers=[
        'Framework :: Pytest',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python :: 3.9',
    ],
    license='proprietary',
    keywords=[
        'pytest', 'py.test', 'pytest-yaml', 'Autotest_api',
    ],
    python_requires=">=3.9",
    install_requires=[
        'Jinja2>=3.1.2',
        'jmespath>=0.9.5',
        'jsonpath>=0.82',
        'pytest>=7.2.0',
        'PyYAML>=6.0',
        'requests==2.18.4',
        'allure-pytest>=2.12.0',
        'pymysql>=1.0.2',
        'DingtalkChatbot>=1.5.7',
        'Faker>=15.3.4',
        'requests_toolbelt>=0.10.1',
        'redis>=4.6.0',
        'websocket-client>=1.6.1',
        'websockets>=11.0.3',
    ],
    entry_points={
        'pytest11': [
            'Autotest_api = Autotest_api.plugin',
        ]
    }
)
