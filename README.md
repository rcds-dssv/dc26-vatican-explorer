# dc26-vatican-explorer
DSSV Data Conclave project for FY26: Vatican Explorer

Favorite emoji: 🫠

[Github Project](https://github.com/orgs/rcds-dssv/projects/8)


## Features 

- [ ] fast
- [ ] fun
- [ ] tba

## Installation steps (testing)
Install uv
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install packages (perhaps in a conda env).
```
uv sync
```

Create the `.gz` and `.whl` files in the `dist/` directory
```
uv build
```

Test the local installlation
```
uv pip install dist/*.whl
import dc26-vatican-explorer
```

Create an account on [TestPyPI](https://test.pypi.org).  The create an API token and add to `$HOME/.pypirc`

!!!!!update this
```
[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-xxxxxxxxxxxxxxxx
```

publish to TestPyPI:
```
uv publish --repository testpypi
```

Install from TestPyPI:
!!!!!update this
```
pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple \
  myproject
```