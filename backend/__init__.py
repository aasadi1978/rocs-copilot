from utils.initialize_logger import initialize_logger
from dotenv import load_dotenv
load_dotenv()
initialize_logger()

import logging
logging.info("Backend initialized. LLM connection will be tested on first use.")
