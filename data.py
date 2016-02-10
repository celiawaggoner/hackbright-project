from faker import Faker
fake = Faker()
fake.seed(4321)

#create user details

for n in range(0, 30):
    print (str(fake.first_name()), str(fake.last_name()), str(fake.email()),
    str(fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)),
    str(fake.city()), str(fake.state()), str(fake.zipcode()))


