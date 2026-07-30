import sqlalchemy

settings = Settings()

engine = sqlalchemy.create_engine("mysql : //root:123456@localhost/fastapi_demo",echo=True)
conn = engine.connect()