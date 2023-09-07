from setuptools import setup, find_packages

setup(name='mq-event-bus-23',
      version='0.2',
      url='https://github.com/the-gigi/pathology',
      license='MIT',
      author="FEFU Analytics sector",
      description="A simple async event bus in Python",
      packages=find_packages(exclude=['tests']),
      zip_safe=False)
