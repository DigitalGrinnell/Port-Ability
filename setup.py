import setuptools

# with open("README.md", "r") as fh:
#     long_description = fh.read()

setuptools.setup(
    name="port-ability",
    version="1.0.0",
    author="Mark A. McFate",
    author_email="summitt.dweller@gmail.com",
    description="A Python 3 command-line utility to help manage and deploy Dockerized application stacks",
    long_description="Port-Ability leverages '_Traefik_' and '_Portainer_' to help manage configured Docker application 'stacks'.  The stacks can be a mix of application types such as Python, Flask, Drupal versions 6, 7 and 8, etc.  Port-Ability provides easy local development (DEV), staging (STAGE), and deployment to production (PROD) environments.  Local (DEV) environments should be easily engaged with XDebug and IDEs like PyCharm and PHPStorm.  The deployed production services, the PROD stacks, are easy to encrypt for secure SSL/TLS access and suitable for occupying a single Docker-ready VPS or server of reasonable scale.  The configuration of this tool and the 'stacks' it manages is easy to define in a single, __master.env_  environment file.",
    long_description_content_type="text/markdown",
    url="https://github.com/SummittDweller/port-ability.git",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: GNU GPLv3",
        "Operating System :: OS Independent",
    ),
)
