# Introduction

This repo is a complete demo of real-time model monitoring using Evidently. Using a simple ML model which predicts house prices, we simulate model drift and outliers, and demonstrate these on a dashboard.

# Outline

<!-- TODO: add detail to this description -->

Within the repo, you will find:

* `data`: contains two scripts. Running the `get_data.py` will automicatically download a house sale prices dataset from Kaggle for model training and data monitoring (drift and outliers); the dataset is saved to this directory. The `generate_dataset_for_demo.py` script will split the house sale prices dataset into a production and a reference dataset which will be saved to a new directory named `datasets`.
* `pipeline`: a model training script which will use the reference data to create and train a Random Forest Regressor model.
* `inference_server`: a model server that exposes our house price model through a REST API.
* `monitoring_server`: an Evidently model monitoring service which collects inputs and predictions from the model and computes metrics such as data drift.
* `scenarios`: Two scripts that simulate different scenarios: e.g. a scenario where there is no drift in the inputs and a scenario which the input data contains drifted data.
* `dashboards`: * a data drift monitoring dashboard which uses Prometheus and Grafana to visualise Evidently's monitoring metrics in real-time.
* A `run_demo_no_drift.py` script to run the demo **with no data drift** using docker compose.
* A `run_demo_drift.py` script to run the demo **with data drift** using docker compose.
* A docker-compose file to run the whole thing.

# Running locally

## Pre-requisites

You'll need Python 3, and Docker and Docker-compose.

## Getting started

1. **Download and install [Docker](https://www.docker.com/) if you don't have it.**

2. **Create a new Python virtual environment and activate it.** For Linux/MacOS users:

```bash
python3 -m venv env
source env/bin/activate 
pip install -r requirements.txt
```

3. **Clone this repo**
```bash
git clone git@github.com:fuzzylabs/evidently-monitoring-demo.git
```

## Download and prepare data for the model

1. **Get and set up Kaggle API token**

- Go to [Kaggle](https://www.kaggle.com) to log in or create an account.
- Get into your account settings page.
- Under the API section, click on `create a new API token`.
- This will prompt you to download the `.json` file into your system. Open the file, and copy the username and key.
- You can either export your Kaggle username and token to the environment:

```bash
export set KAGGLE_USERNAME=<your-kaggle-username>
export set KAGGLE_KEY=<your-kaggle-api-key>
```

- Or move the downloaded `kaggle.json` file:

```bash
mv ~/Downloads/kaggle.json ~/.kaggle/kaggle.json
```

2. **Run the `get_data.py` script**:

```bash
python data/get_data.py
```

This will download and save the data from Kaggle.

3. **Split the dataset into production and reference**:

```bash
python data/generate_dataset_for_demo.py
```

This will split the dataset into reference and 2 production datasets, one with drifted data and one without.

- To monitor data drift or outliers, etc.., two datasets are required to perform comparison. The house price data downloaded from Kaggle is split into a reference and a production dataset. The reference dataset is used as the baseline data and for training the model. The second dataset is the current production data which will be used to compared against the reference dataset to identify data drift and detect outliers. The production dataset does not include the price column as the price will be predicted by the regression model. The scripts will create two scenarios of production data, one with data drift and one without.

## Training the Random Forest Regressor

1. **Run the `train.py` script to train the model**:

```bash
python pipeline/train.py
```
- Once the model is trained, it will be saved as `model.pkl` inside the `models` folder.

## Running the demo

**At the moment, there are two scenarios we can simulate by running the demo:**

- **Scenario 1:** No data drift

```bash
python run_demo_no_drift.py
```

OR

- **Scenario 2:** Data drift

```bash
python run_demo_drift.py
```

Once docker compose is running, the demo will start sending data to the inference server for price prediction which will then be monitor by the Evidently metric server.

The metric server will receive the price prediction along with the features (model inputs) used for the prediction. The features are used to monitor data drift by Evidently using the data drift monitor.

The metrics produced by Evidently will be logged to Promethus's database which will be available at port 9090. To access Prometheus web interface, go to your browser and open: http://localhost:9090/

To visualise these metrics, Grafana is connected to Promethus's database to collect data for the dashboard. Grafana will be available at port 3030. To access Grafana web interface, go to your browser and open: http://localhost:3000/ . If this is your first time using Grafana, you will be asked to enter a username and password, by default, both the username and password is "admin".

To stop the demo, press ctrl+c and shut down docker compose by running the following command:

```bash
docker-compose down
```

## How does the demo works?

![Flow](images/Monitoring_Flow_Chart.png)

The demo is comprised of 5 core components:

- Scenario scripts: within the `scenarios` folder, it contains two scripts namely `drift.py` and `no_drift.py`. Both scripts send production data to the model server for price prediction. The difference between the two is that one would send data from the `production_no_drift.csv` and the other would send data from the `production_with_drift.csv` which contains drifted data.

- The inference server: this is a model server that will return a price prediction when a request is sent to the server. The request would consists of the features of a house such as the number of bedrooms, etc... After a prediction is made by the model, the server would send the predictions along with the features to the metric server.

- The Evidently metric server: this is the Evidently metrics server which will monitor the predictions output by the inferenece server to detect data drift and outliers.

- Prometheus: once the Evidently metric produced some metrics, they will be logged into Prometheus's database as time series data.

- Grafana: this is what we can use to visualise the metrics produced by Evidently in real time. A pre-build dashboard for visualising data drift is include in the `dashboards` directory.

### How are the data generated?

Within the `datasets` folder, 1 reference and 2 production datasets were generated (drift & no drift).

For the no data drift production dataset, the number of bedrooms (which is currently the only features for data drift monitoring) for each row of data is generated using the same distribution as the reference dataset to ensure that the same distribution, thus no data drift will be detected.

For the data drift dataset, the number of bedrooms is generated using a skewed distribution of the the reference's dataset. At the moment, from the reference dataset, if 7 bedrooms has the lowest probability distribution, then the `generate_dataset_for_demo.py` script will always generate a value of 7 to ensure data drfit. But this can be modified later on.

Once the datasets are generatedm, the Random Forest Regressor is trained using the reference dataset.

### The dashboards

![Drift](images/No_Drift.png)

- When the no data drift scenario is running, the Grafana's dashboard should show no data drift is detected. However, as there are some randomness in dataset generation, it is possible to see data drift every once a while.

![Drift](images/Data_Drift.png)

- When the data drift scenario is running, Grafana's dashboard should show data drift at a constant time frame, e.g. no data drfit for 10 seconds -> data drift detected for 5 seconds -> no data drift for 10 seconds etc...