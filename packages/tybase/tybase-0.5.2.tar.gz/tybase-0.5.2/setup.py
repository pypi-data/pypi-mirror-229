from setuptools import setup, find_packages

setup(
    name='tybase',
    version='0.5.2',
    include_package_data=True,
    description='新增pandas第二分组规模',
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type='text/markdown',  # 版本描述
    author='Tuya',
    author_email='353335447@qq.com',
    url='https://github.com/yourusername/your_package',
    packages=find_packages(),
    install_requires=[
        'setuptools',
        "opencv-python",
        "redis",
        "celery",
        "loguru",
        "openpyxl",
        'requests',
        "python-dotenv",
        "retrying",
        "pymysql",
        "mysql-connector-python",
        "sqlalchemy",
        "pandas",
        "langchain",
        "openai",
        'python-dotenv',
        "oss2"
        ""

        # List your package dependencies here
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
    ],
)
