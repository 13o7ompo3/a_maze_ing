from dotenv import load_dotenv

config = load_dotenv("config.txt", override=True)
print(config)
