import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="terindo-single",
    version="0.1.0",
    author="ab-Js",
    author_email="terindo.id@gmail.com",
    description="terindo-system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    install_requires=[
        'ultralytics==8.0.171',
        'opencv-contrib-python==4.6.0.66',
        'opencv-python==4.6.0.66',
        'opencv-python-headless==4.8.0.76',
        'paddleocr==2.7.0.2',
        'paddlepaddle==2.5.1',
        'websockets==11.0.3',
        'zipp==3.16.2',
        'gdown==4.7.1',
        'pyzipper==0.3.6',
        'requests==2.31.0',
        'Pillow==9.5.0'                   
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)