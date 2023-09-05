from setuptools import setup, find_packages

setup(
    name='BungBing26',
    version='3.11.4',
    description='Function By BungBing',
    author='Siriwat Wachirasamphan',
    author_email='siriwat_wachira26@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Education',
        'Operating System :: Microsoft :: Windows :: Windows 11',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    keywords='BungBing26',
    packages=find_packages(),
    install_requires=['numpy', 'pandas', 'matplotlib']
)
