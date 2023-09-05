from setuptools import setup

setup(
    name='PiKit',
    version='1.0.2',
    description='Your package description',
    author='zqs',
    author_email='your-email@example.com',
    packages=['PiKit'],
    install_requires=[
        'opencv-python',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)