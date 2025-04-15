from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
import requests
from decimal import Decimal
from django.core.cache import cache


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self,user,timestamp):
        return (six.text_type(user.pk)+six.text_type(timestamp)+six.text_type(user.is_active))

generate_token=TokenGenerator()

def get_exchange_rate(base_currency='USD'): 
    """
    Fetch exchange rates from the API and cache them.

    Args:
    - base_currency (str): The base currency to fetch rates for (default is 'USD').

    Returns:
    - dict: Exchange rates for the base currency.
    """
    # Attempt to retrieve rates from cache
    rates = cache.get(f'rates_{base_currency}')
    
    if not rates:
        # API Key and URL setup
        api_key = 'bd130c99c516b56995ed7efd'  # Replace with your actual API key
        url = f'https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}'

        try:
            # Fetch data from the API
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Parse JSON response
            data = response.json()
            

            # Extract rates from response
            rates = data.get('conversion_rates', {})
            if not rates:
                print(f"No rates found in response data.")
                print(f"Full Response Data: {data}")  # Print full response for debugging
            else:
                print(f"Rates fetched for {base_currency}: {rates}")  # Debugging line
            
            # Cache the rates for future use
            cache.set(f'rates_{base_currency}', rates, timeout=3600)  # Cache for 1 hour

        except requests.RequestException as e:
            # Handle request errors
            print(f"Failed to fetch exchange rates. Error: {e}")
            rates = {}  # Fallback to empty rates

    return rates


def convert_currency(amount, from_currency, to_currency, rates):
    """
    Convert an amount from one currency to another using provided rates.

    Args:
    - amount (float or Decimal): The amount to convert.
    - from_currency (str): The currency to convert from.
    - to_currency (str): The currency to convert to.
    - rates (dict): Exchange rates for conversion.

    Returns:
    - float or None: The converted amount or None if conversion is not possible.
    """
    # Convert amount to Decimal if it's not already
    if not isinstance(amount, Decimal):
        amount = Decimal(amount)

    if from_currency == to_currency:
        return amount
    
    if from_currency in rates and to_currency in rates:
        rate_from = Decimal(rates[from_currency])
        rate_to = Decimal(rates[to_currency])

        # Calculate the conversion rate from the rates
        conversion_rate = rate_to / rate_from
        print(f"Conversion rate from {from_currency} to {to_currency}: {conversion_rate}")  # Debugging line
        
        # Convert the amount
        return round(amount * conversion_rate, 2)  # Round to 2 decimal places
    
    print(f"Conversion rate for {from_currency} to {to_currency} not found in rates.")
    return None


def test_api():
    """
    Test the API endpoint to ensure it's working and returning expected data.
    """
    api_key = 'bd130c99c516b56995ed7efd'  # Replace with your actual API key
    url = f'https://v6.exchangerate-api.com/v6/{api_key}/latest/USD'

    try:
        # Fetch data from the API
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse JSON response
        data = response.json()
        print(f"API Response Data: {data}")

    except requests.RequestException as e:
        # Handle request errors
        print(f"Failed to fetch exchange rates. Error: {e}")


def parse_datetime_safe(value):
    if isinstance(value, str):  # Ensure it's a string
        try:
            return datetime.fromisoformat(value)  # Parse ISO 8601 string
        except ValueError:
            return None  # Handle invalid date formats
    return None  # Return None for non-string values