import setuptools
# used by python -m build
# python -m build needs pyproject.toml or setup.py
setuptools.setup(
     name='profile-local',  
     version='0.0.10',   #https://pypi.org/project/profile-local/
     author="Circles",
     author_email="info@circles.life",
     description="PyPI Package for Circles Profile Local Python",
     long_description="This is a package for sharing common profile functions used in different repositories",
     long_description_content_type="text/markdown",
     url="https://github.com/circles",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: Other/Proprietary License",
         "Operating System :: OS Independent",
     ],
    install_requires=[
        'mysqlclient',
        'mysql-connector>=2.2.9',
        'pymysql>=1.1.0',
        'python-dotenv>=1.0.0',
        'pytest>=7.4.0',
        'logzio-python-handler>=4.1.0',
        'database-without-orm-local==0.0.65',
        'location_profile_local>=0.0.18',
        'operational-hours-local>=0.0.17',
        'database-infrastructure-local>=0.0.12',
        'person-local>=0.0.12',
        'location-local>=0.0.23',
        'reaction-local>=0.0.2',
        'profile-reaction-local>=0.0.6',
        'language-local>=0.0.4',
        'gender-local>=0.0.1',
        'user-context-remote>=0.0.10',
    ],
 )
