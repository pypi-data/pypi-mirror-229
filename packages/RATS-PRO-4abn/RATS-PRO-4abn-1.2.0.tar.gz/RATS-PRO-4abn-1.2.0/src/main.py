"""
Interview Programming Excercise for ABN AMRO

The small company RATS PRO is dealing with bitcoin trading. Given 2 datasets, it is requested
to provide a dataset with the emails of the clients from the United Kingdom and the Netherlands and some
of their financial details to starting reaching out to them for a new marketing push.

"""
import logging
import pandas as pd
from flask import Flask, render_template, request
from logging.handlers import TimedRotatingFileHandler

app = Flask(__name__, template_folder='templates', static_folder='static')

clients_df, financial_df, merged_df = None, None, None
selected_countries = None
# Way to go back button
go_back_button = '<a href="/">Go Back</a>'

# Set the logging level
logging.basicConfig(level=logging.INFO)

# Create a logger
logger = logging.getLogger(__name__)

# Define a file handler to save logs to a file
file_handler = logging.FileHandler('main.log')

# Create a rotating log file handler for rotating policy
file_handler = TimedRotatingFileHandler('main.log', when='midnight', interval=1, backupCount=7)

# Create a formatter to specify the log message format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)


@app.route('/')
def welcome_page():
    """
    Render the welcome page.

    Returns:
        str: HTML page containing a welcome message and links/buttons to other pages.
    """
    # Logger message
    logger.info('\n\tLoading welcoming page!\n')
    return render_template('index.html')

@app.route('/load-datasets', methods=['GET'])
def load_datasets():
    """
    Load datasets from provided CSV paths.

    Returns:
        str: HTML page with a message indicating whether the datasets were loaded
             successfully or an error occurred. There is also a button to go back.
    """
    csv_path1 = request.args.get('csv_path1')
    csv_path2 = request.args.get('csv_path2')

    if csv_path1 and csv_path2:
        global clients_df, financial_df
        clients_df = pd.read_csv(csv_path1)
        financial_df = pd.read_csv(csv_path2)

        # Logger message
        logger.info('\n\tDatasets loaded successfully!\n')

        return "Datasets loaded successfully! " + go_back_button

    logger.warning('\n\tCSV paths not provided or datasets not accessible\n')
    return "CSV paths not provided or datasets not accessible. " + go_back_button


@app.route('/')
def select_countries_form():
    """
    Render a form to select the countries of the final resulting dataset.

    Returns:
        str: HTML segment in main page containing a form to select countries.
    """
    return render_template('select_countries.html')

@app.route('/process-selected-countries', methods=['POST'])
def process_selected_countries():
    """
    Process the selected countries from the form to later pass them as an argument.

    Returns:
        str: An HTML page with a message displaying the selected countries, if any and a back button.
    """
    global selected_countries
    selected_countries = request.form.getlist('country')
    
    logger.info('\n\tSelected countries added succesfully!\n')
    return "Selected countries: " + ", ".join(selected_countries) + go_back_button

@app.route('/view-client-data')
def result():
    """
    Process and display client data based on selected countries and paths of datasets.

    Returns:
        str: HTML page displaying the collated client data or an error message.
    """
    global merged_df
    global countries_to_filter
    # Filter by country (United Kingdom and Netherlands)
    countries_to_filter = selected_countries
    filtered_clients_df = clients_df[clients_df['country'].isin(countries_to_filter)]

    # Drop unnecessary columns (e.g., personal identifiable info) from first dataset
    filtered_clients_df.drop(['first_name', 'last_name'], axis=1, inplace=True)

    # Drop credit card number from second dataset
    financial_df.drop(['cc_n'], axis=1, inplace=True)

    # Merge filtered client and financial DataFrames
    merged_df = pd.merge(filtered_clients_df, financial_df, on='id')

    # Rename columns
    merged_df.rename(columns={'id': 'client_identifier', 'btc_a': 'bitcoin_address', 'cc_t': 'credit_card_type'}, inplace=True)

    # Save the collated data to a CSV file
    output_path = 'client_data/collated_data.csv'
    merged_df.to_csv(output_path, index=False)

    logger.info('\n\tRedirecting to the results page\n')
    return render_template("client_data.html", tables=[merged_df.to_html()], titles='')

app.run(debug=True)
