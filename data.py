from faker import Faker 
fake = Faker()
fake.seed(4321)

#create user details

for n in range(0, 20):
    user = User()
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.email()
    password = fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)
    city = fake.city()
    state = fake.state()
    zipcode = fake.zipcode()

#create instructor names

name = fake.first_name()
