import os.path
from setuptools import setup, find_packages

import stun


def main():
    src = os.path.realpath(os.path.dirname(__file__))
    README = open(os.path.join(src, 'README.rst')).read()

    setup(
        name='pystun3-fix',
        version=stun.__version__,
        packages=find_packages(),
        zip_safe=False,
        license='MIT',
        author='Narlim (original authors: gaohawk, Justin Riley)',
        author_email='wangweimingooo@gmail.com',
        url='https://github.com/Narlim/pystun3',
        description='A Python STUN client for getting NAT type and external IP (RFC 3489)',
        long_description=README,
        keywords='STUN NAT',
        classifiers=[
            'Development Status :: 4 - Beta',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.8',
            'Topic :: Internet',
            'Topic :: System :: Networking :: Firewalls',
        ],
        tests_require=['coverage', 'nose', 'prospector'],
        test_suite='tests',
        entry_points={
            'console_scripts': [
                'pystun3=stun.cli:main'
            ]
        }
    )

if __name__ == '__main__':
    main()
