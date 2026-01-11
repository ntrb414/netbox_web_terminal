from setuptools import setup, find_packages

setup(
    name='netbox-web-terminal',
    version='0.1',
    description='A Web SSH Terminal plugin for NetBox',
    url='https://github.com/your-repo/netbox-web-terminal',
    author='Trae Assistant',
    license='Apache 2.0',
    install_requires=[
        'paramiko',
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
