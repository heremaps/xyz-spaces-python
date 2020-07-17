# Jupyter Notebooks with XYZ Spaces Examples

Th XYZ Spaces for Python project includes several [Jupyter notebooks](https://jupyter-notebook.readthedocs.io/en/stable/) with examples.

## Prerequisites

Before you can use the example notebooks, make sure your system meets the following prerequisities:

- A Python installation, 3.6+ recommended, with the `pip` command available to install dependencies
- A HERE developer account, free and available under [HERE Developer Portal](https://developer.here.com)
- An XYZ API access token from your XYZ Hub server or the [XYZ portal](https://www.here.xyz) (see also its [Getting started](https://www.here.xyz/getting-started/) section) in an environment variable named `XYZ_TOKEN` which you can set like this (with a valid value, of course):

    ```bash
    export XYZ_TOKEN="MY-FANCY-XYZ-TOKEN"
    ```

    If you prefer, you can alternatively provide this token as a parameter in your code.

In order to be able run the Jupyter notebooks in this directory, you may need to install some third-party dependencies
on your system.

1. Copy the text below to a file named `viz.txt`.

```
ipyleaflet
ipyrest
ipywidgets>=7.5.1
jupyterlab>=2.1
sidecar
```


2. Run the command:

```bash
pip install -r viz.txt
```

## Running the Examples

You can run all the examples in this repository locally with or without Docker, as described below.

### Using Docker

If you are using Docker, please follow the instructions in `binder/README.md` to create a requirements file. Then
install a tool named *repo2docker* that runs this repository in a docker container:

```bash
pip install jupyter-repo2docker
jupyter-repo2docker --user-id 1000 --env XYZ_TOKEN=$XYZ_TOKEN .
```

(`--user-id 1000` is a workaround for a buglet in *repo2docker* when running in networks with many users)

This will generate some output ending with something like this:

```
[...]
To access the notebook, open in a web browser:
    http://127.0.0.1:53186/?token=722b9fc8781ca0aef1b34b47645ff37c1d523a9e1a3766f4
```

Now you can open the link at the bottom in a browser to run a local Jupyter server. Once the server is running, click on the `demo.ipynb` file to open the demo notebook and execute the cells at your convenience.

### Without Docker

If you want to install it all locally you can run:

```bash
pip install -e .
bash binder/postBuild
jupyter lab docs/notebooks/demo.ipynb
```

With or without Docker, when you execute all cells of the demo notebook, you should see a map similar to the image below.

![Example map from xyzspaces demo.ipynb notebook](../../images/example_map.png)
