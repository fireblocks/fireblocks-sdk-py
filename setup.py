from distutils.core import setup
setup(
  name = 'fireblocks_sdk',         # How you named your package folder (MyLib)
  packages = ['fireblocks_sdk'],   # Chose the same as "name"
  version = '0.1.1',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Fireblocks python SDK',   # Give a short description about your library
  #author = 'Yoni Moses',                   # Type in your name
  #author_email = 'yoni@fireblocks.io',      # Type in your E-Mail
  url = 'https://github.com/fireblocks/fireblocks-sdk-py',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/fireblocks/fireblocks-sdk-py/archive/v0.1.1.tar.gz',    # I explain this later on
  keywords = ['Fireblocks', 'SDK'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'PyJWT==1.7.1',
          'requests==2.22.0',
      ],
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Topic :: Software Development',    
    'License :: OSI Approved :: MIT License',   # Again, pick a license    
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)