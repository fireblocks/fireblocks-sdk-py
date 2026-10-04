from distutils.core import setup
from pathlib import Path

setup(
  name = 'fireblocks_sdk',
  packages = ['fireblocks_sdk'],
  version = '2.19.0',
  license='MIT',
  description = 'DEPRECATED — use the fireblocks package instead. Legacy Fireblocks python SDK, end-of-life November 1, 2026',
  long_description=(Path(__file__).parent / 'README.md').read_text(encoding='utf-8'),
  long_description_content_type='text/markdown',
  url = 'https://github.com/fireblocks/fireblocks-sdk-py',
  download_url = 'https://github.com/fireblocks/fireblocks-sdk-py/archive/v2.19.0.tar.gz',
  keywords = ['Fireblocks', 'SDK'],
  install_requires=[
          'PyJWT>=2.8.0',
          'cryptography>=2.7',
          'requests>=2.22.0',
      ],
  classifiers=[
    'Development Status :: 7 - Inactive',
    'Intended Audience :: Developers',
    'Topic :: Software Development',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.8',
  ],
)
