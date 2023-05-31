CONTAINER_ENGINE ?= podman
CONTAINER_PLATFORM ?= linux/amd64

REG ?= quay.io
ORG ?= $(USER)
TARGET ?= hello
VERSION ?= latest

IMAGE ?= "$(REG)/$(ORG)/$(TARGET):$(VERSION)"

image/build:
	echo "building image: $(IMAGE)"
	$(CONTAINER_ENGINE) build --platform=$(CONTAINER_PLATFORM) -t $(IMAGE) .

image/push:
	echo "pushing image: $(IMAGE)"
	$(CONTAINER_ENGINE) push $(IMAGE)

set/kubefile/image:
	echo "Please manually update the images in the kubefiles"
	echo "image: $(IMAGE)"
