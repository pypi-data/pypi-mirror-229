import pytest
from src.main import app # Import your Flask app
import pandas as pd

# Define sample data for testing
sample_clients_data = {
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie'],
    'country': ['United Kingdom', 'Netherlands', 'United Kingdom']
}

sample_financial_data = {
    'id': [1, 2, 3],
    'balance': [1000, 2000, 3000],
    'credit_card_type': ['china-unionpay', 'maestro', 'mastercard']
}

# Create sample DataFrames
clients_df = pd.DataFrame(sample_clients_data)
financial_df = pd.DataFrame(sample_financial_data)

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_welcome_page(client):
    """
    Test the welcome_page route.

    Args:
        client: The Flask test client.

    Asserts:
        - Checks that the response status code is 200 == OK.
        - Verifies that the template is rendered with specific content.
    """
    response = client.get('/')
    assert response.status_code == 200  # Check that the page loads successfully

    # Verify that the template is rendered
    assert b"Welcome to the Client Data Collation App!" in response.data
    assert b"This app for RATS PRO serves collated client data for marketing purposes." in response.data

def test_load_datasets_no_paths(client):
    """
    Test the load_datasets route when CSV paths are not provided/accessible.

    Args:
        client: The Flask test client.

    Asserts:
        - Checks that the response contains a message indicating CSV paths are not accessible.
    """
    response = client.get('/load-datasets')
    assert b"CSV paths not provided or datasets not accessible" in response.data

def test_load_datasets_with_paths(client, tmpdir):
    """
    Test the load_datasets route when CSV paths are provided/accessible.

    Args:
        client: The Flask test client.

    Asserts:
        - Checks that the response contains a message indicating CSV paths were correctly provided.
        - Checks that the files from the paths are indeed panda dataframes and can be used.
    """
    # Create temporary CSV files
    csv_path1 = tmpdir.join("csv1.csv")
    csv_path1.write("data1")

    csv_path2 = tmpdir.join("csv2.csv")
    csv_path2.write("data2")

    response = client.get(f'/load-datasets?csv_path1={csv_path1}&csv_path2={csv_path2}')
    assert b"Datasets loaded successfully!" in response.data

    # Check that clients_df and financial_df are pandas dataframes
    assert isinstance(clients_df, pd.DataFrame)
    assert isinstance(financial_df, pd.DataFrame)

def test_select_countries_form(client):
    """
    Test the select_countries route
    Args:
        client: The Flask test client.

    Asserts:
        - Checks that the response status code is 200 == OK.
        - Verifies that the template is rendered with specific content.
    """
    response = client.get('/')
    assert response.status_code == 200  # Check that the page loads successfully

    # Verify that the template is rendered
    assert b"Input Dataset Paths" in response.data
    assert b"Select Countries" in response.data

def test_process_selected_countries(client):
    """
    Test the process_selected_countries route.

    Args:
        client: The Flask test client.

    Asserts:
        - Checks that the response status code is 200 == OK.
        - Verifies the response content contains selected countries.
    """
    response = client.post('/process-selected-countries', data={'country': ['United Kingdom', 'Netherlands']})
    assert response.status_code == 200  # Check that the page processes the POST request successfully

    # Verify the response content
    assert b"Selected countries: United Kingdom, Netherlands" in response.data
