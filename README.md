# Data Scraper

## Requirements

- [Python 3](https://www.python.org/downloads/)
- [Pipenv](https://pipenv.kennethreitz.org/en/latest/)


## Usage

The scraper needs the following environment variables:

- `$SCRAPER_DATA_PATH`  : The path where the data will be saved
- `$SYMBOLS_FILE_PATH`  : Path to the file that contains the symbols to scrape
- `$TIINGO_API_KEY`     : Used by the Tiingo scraper
- `$SLACK_WEBHOOK`      : Used to send Slack notifications (Optional)
- `$SLACK_CHANNEL`      : Channel to send Slack notifications to (Optional)

To backup data to S3, the following variables must be set:

- `$AWS_ACCESS_KEY_ID`
- `$AWS_SECRET_ACCESS_KEY`
- `$S3_BUCKET`

### Install

```
$> make install
```

### Run tiingo scraper

```
$> make scrape CRAWLER=tiingo
```

### Run cboe scraper

```
$> make scrape CRAWLER=cboe
```

### Backup to S3

```
$> make backup
```

### Build Docker image

```
$> make image
```

## Deploy to Kubernetes

You will need [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl).  
Remember to configure the appropriate values in the various `yml` files inside `deploy/k8s/`.

```
$> make deploy
```
