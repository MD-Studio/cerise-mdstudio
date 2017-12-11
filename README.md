# cerise-mdstudio
Home of the Cerise MDStudio CWL API.

To run the example, you need the `cerise_client` library. It's easiest to make
a virtual environment for that, then activate it and install the library:

```bash
virtualenv env
env/bin/activate
pip install cerise_client
```

Next, you can change into the `examples/` directory, and run the example

```bash
cd examples
CERISE_DAS5_USERNAME=username CERISE_DAS5_PASSWORD=password python run_gromacs.py
```

