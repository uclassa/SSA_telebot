import os
from typing import final
from dotenv import load_dotenv

# Load environment variables from ./../config.env
APPLICATION_DIR = os.path.join(os.path.dirname(__file__), '..')
dotenv_path = os.path.join(APPLICATION_DIR, 'config.env')
load_dotenv(dotenv_path)


def get_service_account_info():
	'''
		Loads the service account credentials from the environment variables
		and returns them as a dictionary.
		:return: dictionary with service account credentials
	'''

	TYPE: final = os.environ.get("type")
	PROJECT_ID: final = os.environ.get("project_id")
	PRIVATE_KEY_ID: final = os.environ.get("private_key_id")
	PRIVATE_KEY: final = os.environ.get("private_key")
	CLIENT_EMAIL: final = os.environ.get("client_email")
	CLIENT_ID: final = os.environ.get("client_id")
	AUTH_URI: final = os.environ.get("auth_uri")
	TOKEN_URI: final = os.environ.get("token_uri")
	AUTH_PROVIDER_X509_CERT_URL: final = os.environ.get("auth_provider_x509_cert_url")
	CLIENT_X509_CERT_URL: final = os.environ.get("client_x509_cert_url")
	UNIVERSE_DOMAIN: final = os.environ.get("universe_domain")

	return {
		"type": TYPE,
		"project_id": PROJECT_ID,
		"private_key_id": PRIVATE_KEY_ID,
		"private_key": PRIVATE_KEY,
		"client_email": CLIENT_EMAIL,
		"client_id": CLIENT_ID,
		"auth_uri": AUTH_URI,
		"token_uri": TOKEN_URI,
		"auth_provider_x509_cert_url": AUTH_PROVIDER_X509_CERT_URL,
		"client_x509_cert_url": CLIENT_X509_CERT_URL,
		"universe_domain": UNIVERSE_DOMAIN
	}