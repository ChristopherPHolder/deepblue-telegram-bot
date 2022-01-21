import configparser
config = configparser.ConfigParser()
config.read('config.ini')

# App crediencials
APP_NAME = config.get('Credencials', 'APP_NAME')
API_ID = int(config.get('Credencials', 'API_ID'))
API_HASH = config.get('Credencials', 'API_HASH')
BOT_TOKEN = config.get('Credencials', 'BOT_TOKEN')

# Database information
DB_NAME = config.get('Database', 'DB_NAME')

# Admin information
ADMIN_GROUP = int(config.get('Admin', 'ADMIN_GROUP'))
SUPER_USER = int(config.get('Admin', 'SUPER_USER'))
