
# Standard library imports
import os

# Third party imports
from dotenv import load_dotenv
import clang.cindex

# Load environment vairables set in .env
load_dotenv()

# Set libclang path
clang.cindex.Config.set_library_file(os.getenv('LIBCLANG_PATH'))