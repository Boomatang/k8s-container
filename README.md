# k8s container

This repo is an example repo to show how easy it is to create container scripts that can be run on kubernetes environments.
What the code does is not the focus but how the scripts can be run locally and then ran remotely.
Python is the scripting language used here and poetry is used for dependency and script management.

There are six different ways the scripts can be called.
Each way has its advantages, but the goal is to deploy on a cluster in the end.

## Code Layout
In this project all the code is added to the `k8s_container` package. 
`__main__.py` holds the entry points or commands to execute the scripts.
There are three scripts that can be executed, these are:
* basic
* secret
* config

The scripts related to the k8s resources that they consume.
The `basic` does not require any external resources to be on the cluster.
While `secret` and `config` require kinds of Secret and ConfigMap with the correct fields respectfully.

The `Makefile` has a number of commands.
There are also variables that can be configured, it is worth looking at. 
By default `podman` tool used to work with the code base.
Method 5 will require podman.

## Running the scripts
### Method 1: Calling the package with Python
As the package has the `__main__.py` file, the package can be called directly.

With poetry being used to manage the virtual environments.
The environment needs to be activated first. 
For the first run `poetry install` should be run.
```shell
poetry shell
```

Once activated the scripts can be triggered with the following.
```shell
python -m k8s_continer <basic|config|sercet>
```

As the `config` and `sercet` files needs external information. 
This information is passed via environment varibles. 
The varibles are configured in the `.env` file.
This file is autoloaded when the scripts are executed.
If an environment variable is set outside the `.env`, its value will not be overriden by the value in the `.env` file.

This method of execution is usefully during the development as the IDE can be configured to run the command under development.
The IDE's debuggers can then be attached to aid with debugging any issues.

### Method 2: Poetry script entry points
Poetry allows the configuration of script entry points.
This feature is what all the following methods will build upon.

Looking at the `pyproject.toml` file there is a section called `[tool.poetry.scripts]`.
This section is where the entry points are configured.
Taken the `basic = "k8s_container.__main__:basic"` as an example. 
The word to the left of `=` is the reference name for calling the script, in this example that is `basic`.
On the right side is the path to the function that will be called.
The `k8s_container` is the package name, `__main__` reference the file name without the file extension.
Finally, the `basic` is the function being called.
Pay notice to the `:` between the file and function names.

Every time there is a script added `poetry install` does need to run, but once that is done then the scripts can be called as follows.
```shell
poetry <script name|basic|config|secret>
```
When inside the virtual environment these scripts are in the PATH, which allows them to be called from the command line directly.
To do this the virtual environment needs to be first activated as follows;
```shell
poetry shell
```
Then the scripts can be called.
```shell
basic|config|secret
```
When doing this method the `.env` file is still used to give values to the commands. 

### Method 3: Locally installable python package
As poetry can be used to be build distributable packages, these packages can be installed locally.
For this method the package needs to be built and installed.

Note that the simple naming of the commands would not lead to a longer term good user experience.
The use of a better cli framework should be used.

To build the package run the following:
```shell
poetry build
```
This creates the packages files in the `dist` folder. 
The package version matches the version stated in the `pyproject.toml` file.

To install the package it's recommended to use `pipx` as this will place the package in a virtual environment.
```shell
pipx install ./dist/k8s_container-<version>-py3-none-any.whl
```

Once installed the scripts should be access via the command line in any location.
```shell
baisc|config|secret
```
An important note is the `.env` file will not be used and any environment variables need to be set before running the scripts.  

### Method 4: Run a container image
This method creates a container image that can run locally. 
The `Containerfile` has the steps required to build the image. 
For the most part the image is build to give the same result as method 3.

To build the image run:
```shell
podman build -t hello:latest .
```

This builds a local image.
There is a make target that can be also used. 
```shell
make image/build
```

Once the image is build the scripts can be executed.
```shell
podman run --rm hello:latest basic
```
The above example runs the `basic` command.
Once again the `.env` file is not going to be used.
This time the values need to be past to the image.
A command as follows can be used to set teh environment variables.
```shell
podman run --rm --env=LOOP=3 --env=DELAY=2  localhost/hello:latest config
```

This method is usefully but can get unwieldy if the script has a number of environment variables to be set.

### Method 5: podman kube play and kubefiles
This method is one step away from deploying to a kubernetes environment.
`podman` is required for this method.

The `kubefile` directory holds a number of yaml files. 
Looking at the `cmd-basic.yaml` first, there are a number of things to note.
The `kind` is Pod, there are a number of deployment types that is support but this is the simplest.
`metadata.name` is used to set the name of the pod.
While the `spec` holds the configuration for the pod.
The one field that may need editing here is the `image` field this would want to be the same as the image build.
This example will use the `hello:latest` image.

Before moving on build the image to be used in the examples.
```shell
IMAGE=hello:lastet make image/build
```
To run the basic pod use the following.
```shell
podman kube play kubefile/cmd-basic.yaml
```

This creates a pod that has a number of containers.
In this cause there will be two containers.
One container is the hello:latest and the second is an infra container.
The pods can be listed with:
```shell
podman pod ls
```

To list the containers and pods they belong too can be done with:
```shell
podman container ls -a --pod
```

Logs from a pod can be viewed by:
```shell
podman pod logs basic
```

To remove the pod, run:
```shell
podman kube down kubefile/cmd-basic.yaml
```
Looking at the `cmd-config.yaml` and `cmd-secret.yaml` is where the power of this method shows.
There is a second kind configured in each file, a `ConfigMap` and `Secret`.
These secondary resources hold the data that will be loaded into the environment varibles.
The kind `Pod` now has an `env` section added to `spec.containers.[0]`.
This is how the values from the ConfigMap or Secrets are mapped the container.

Now the running of containers with complex configurations is much simpler.
```shell
podman kube play kubefile/cmd-secret.yaml 
```

This method has the advantage of being repeatable as all the configuration in the one file.
`podman kube play` does have extra flags that allow adding more resources but is the simple example.
Read more on kube play in the [documentation](https://docs.podman.io/en/latest/markdown/podman-kube-play.1.html)

### Method 6: Deploying to kubernetes environment
This method is building on method 5 and deploying to a remote kubernetes environment.
CLI access to a kubernetes environment is assumed for this.
There is two things that we must ensure are set.
1. The images are publicly access from a remote site like [quay.io](https://quay.io).
2. The correct image is set in the kubefile.

To build the image with the default repository being `quay.io` and org of the current system user.
```shell
make image/build
```
To push the image run.
```shell
make image/push
```
Check the `Makefile` to change the parameters.

Next ensure the image in kubefile is point to the image that was just pushed.
Once the is correct it is time to deploy the scripts.

To deploy the script in the default namespace, run:
```shell
kubectl apply -f kubefile/cmd-config.yaml -n default
```
This will create the ConfigMap and deploy the container.
Now check the remote environment for the running pod.

## Conclusion
This example show how little effort is required to take a script that only run on my machine to being deployable in remote environments.
For this example the `Pod` kind was used as it makes most sense for single runs of a script but this could be an application that is HA by using a `Deployment` kind.

A development work flow using Method 1, 5 & 6 is very powerfully.
Being able to develop with resources like ConfigMaps and Secrets can make the step to production less.

## What's Missing
There are a few improvements that would be nice. PR's are welcome.

- [ ] There is a stub make target to set the images in the kubefiles. 
It would be good to get this filled out. `make set/kubefile/image`.
- [ ] The `Containerfile` file needs improvements to set a user to improve security.
- [ ] A nice to have would be an example where the scripts are write using bash.
- [ ] A guide for deploying to mimikube running locally