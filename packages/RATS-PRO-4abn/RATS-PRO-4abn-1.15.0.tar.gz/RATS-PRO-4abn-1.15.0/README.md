# RATS PRO collation Flask app

Flask app dedicatded to the small company RATS PRO. Dealing with bitcoin trading, two datasets are provided by their paths to the app and the user can also select the countries they would like to have a final report of. Objective is to collate the data so that the collated data can be used for their upcoming marketing campaign.

## Getting started

Following instructions will guide you through the setup and execution of the Data Collation app.

## Installation
To install the application, head to https://pypi.org/project/RATS-PRO-4abn/1.15.0/#files and download the Source Distribution file. Once downloaded unzip the file to your desired location in your machine.

If you would prefer to clone it through github, please contact me.

Please make sure that you have all the required libraries installed for the smooth operation of the application. You should have Python 3.9.X installed, if you don't you can install it from here: https://www.python.org/downloads/
To ensure that you have all the required libraries, head to the root directory of the project you extracted and run the following command:
```bash
pip install -r requirements.txt
```
This will install all the necessary dependencies listed in the requirements.txt file.


## Execution
In order to run the application, open the folder where you extracted the project at. Navigate to the "src" folder and run/double-click the "main.py" script. This will start the local server.

Then open your web-browser and head to the address mentioned in the terminal window that opened when running the main.py script. You should copy-paste the address mentioned in the URL bar in your web-browser, and after pressing enter you will be redirected to the main page of the application.

From there, you have to provide the paths of the location of your 2 datasets you want to collate. To do so, find the datasets in your machine you wish to use, right-click on them one at a time and select the "Copy as Path" option. Then you can paste the path to each of the text-boxes of the website as indicated there. Click Load Datasets and you will be prompted whether they have been successfully loaded or if there was an error. After that click on the go back button.

After successfully loading the datasets, tick the boxes of the countries you wish to use for your results. Click the "Submit" button and same procedure as mentioned above. Head back and click on the "View Collated Data" to be redirected to the webpage displaying your results.

These results are saved under the "client_data" folder which you can access and use the results as you please.
