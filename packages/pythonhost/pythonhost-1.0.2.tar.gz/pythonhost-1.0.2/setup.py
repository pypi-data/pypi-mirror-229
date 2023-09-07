import setuptools

setuptools.setup(
    name="pythonhost",
    version="1.0.2",
    author="pythonhost Co",
    author_email="info@pythonhost.ir",
    description="pythonhost Library",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://pythonhost.ir",
    download_url='https://github.com/pythonhost/pythonhost.git',
    packages=setuptools.find_packages(),
    keywords="pythonhost pythonhost.ir ftp python host",
    install_requires=['ftplib'],
    license='MIT',
    platforms=['any'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
    	'Environment :: Console',
    	'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
