from setuptools import setup, find_packages

setup(
    name='kubebuild',
    version='0.3.0',
    packages=find_packages(),
    install_requires=[
        'click',
        'PyInquirer',
        'PyYAML',
        'regex',
        'rich',
        'setuptools',
        'typer',
    ],
    entry_points={
        'console_scripts': [
            'KubeBuild = kubebuild:app',
        ],
    },
    author='Ahmed K. Madani',
    author_email='ahmedk.madani@outlook.com',
    description='KubeBuild - Kubernetes YAML Generator and Deployment Tool',
    url='',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
