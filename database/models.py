import peewee

#db = peewee.SqliteDatabase("Connection.sql")
db = peewee.SqliteDatabase("database_conn.sql")

class BaseModel(peewee.Model):
    class Meta:
        database = db

class User(BaseModel):
    user_id = peewee.IntegerField(primary_key=True)
    name = peewee.CharField(max_length=100)

class Request(BaseModel):
    request_id = peewee.PrimaryKeyField(primary_key=True)
    user = peewee.ForeignKeyField(User)
    city = peewee.CharField(max_length=100)
    name = peewee.CharField(max_length=100)
    dateTo = peewee.CharField(max_length=100) #peewee.DateField()
    dateFrom = peewee.CharField(max_length=100) #peewee.DateField()
    price = peewee.DecimalField(decimal_places=2, null=True)
    #maxPrice = peewee.DecimalField(decimal_places=2, null=True)
    number_of_people = peewee.CharField(max_length=100) #peewee.IntegerField()
    image = peewee.TextField()

def initialize_db():
    #db.connect()
    db.create_tables([User, Request], safe=True)
    db.close()