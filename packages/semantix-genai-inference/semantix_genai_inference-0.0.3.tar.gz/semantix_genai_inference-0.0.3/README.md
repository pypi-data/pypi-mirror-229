# Semantix GenAI Inference

A python client library to help you interact with the Semantix GenAI Inference API.


# Installation

If you're using pip, just install it from the latest release:

    $ pip install semantix-genai-inference

Else if you want to run local, clone this repository and install it with poetry:

    $ poetry build
    $ poetry install

# Usage

To use it:

First, make sure you have a valid API key. You can get one at [Semantix Gen AI Hub](https://home.ml.semantixhub.com/)

Set an environment variable with your api secret:

    $ export SEMANTIX_API_SECRET=<YOUR_API_SECRET>
    $ semantix-ai --help

# DEV - Publish to pypi

    $ poetry config pypi-token.pypi <YOUR_PYPI_TOKEN>
    $ poetry build
    $ poetry publish

# DEV - Bump version

    $ poetry version patch | minor | major | premajor | preminor | prepatch | prerelease

See more at [Poetry version command docs](https://python-poetry.org/docs/cli/#version)

# DEV - Commit message semantics

See at [Conventional Commits](https://gist.github.com/joshbuchea/6f47e86d2510bce28f8e7f42ae84c716)