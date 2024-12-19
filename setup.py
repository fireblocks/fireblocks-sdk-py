from distutils.core import setup
setup(
  name = 'fireblocks_sdk',
  packages = ['fireblocks_sdk'],
  version = '2.15.0',
  license='MIT',
  description = 'Fireblocks python SDK',
  long_description="""Fireblocks python SDK""",
  long_description_content_type='text/markdown',
  url = 'https://github.com/fireblocks/fireblocks-sdk-py',
  download_url = 'https://github.com/fireblocks/fireblocks-sdk-py/archive/v2.15.0.tar.gz',
  keywords = ['Fireblocks', 'SDK'],
  install_requires=[
          'PyJWT>=2.8.0',
          'cryptography>=2.7',
          'requests>=2.22.0',
      ],
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Topic :: Software Development',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.8',
  ],
)
