.PHONY: help backup deploy
.DEFAULT_GOAL := help

IMAGE_NAME?=scraper
IMAGE_TAG?=0.1
CRAWLER?=tiingo

install: ## Create a Python virtual environment and install dependencies
	pipenv --three && pipenv sync

scrape: ## Launches scraper (tiingo or cboe)
	pipenv run scrapy crawl $(CRAWLER)

backup: ## Backup scraped data to S3 bucket
	pipenv run python -m backup

image: ## Build docker image
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) -t $(IMAGE_NAME):latest -f ./deploy/docker/Dockerfile .

deploy: ## Deploys to Kubernetes cluster
	kubectl apply --recursive -f deploy/k8s

help: ## This screen :)
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
