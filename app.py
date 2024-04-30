#--------------------IMPORTS--------------------#

from flask import Flask, render_template, session, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy import or_, and_
import string
import random

#--------------------IMPORTS--------------------#

#--------------------DATABASE-CONFIGURATION--------------------#

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ncuwy782r2UGUYigiu9G789G' # This line sets a secure secret key that will be used for sessions (can be changed if needed)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # This line helps configure the databases URI
db_path = os.path.join(os.path.dirname(__file__), 'data', 'site.db') # This line configures the databases path in the system
bcrypt = Bcrypt(app) # Configures Bcrypt in the app
db = SQLAlchemy(app) # Configures SQLAlchemy in the app

class Users(db.Model): # Creates the SQL table for users
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), unique=False, nullable=True)
    sur_name = db.Column(db.String(30), unique=False, nullable=True)
    username = db.Column(db.String(30), unique=True, nullable=True)
    password = db.Column(db.String(60), unique=False, nullable=True)
    email = db.Column(db.String(60), unique=True, nullable=True)
    phone = db.Column(db.String(11), unique=True, nullable=True)
    points = db.Column(db.Integer, unique=False, nullable=True)

class Rewards(db.Model): # Creates the SQL table for rewards
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=False, nullable=True)
    description = db.Column(db.String(100), unique=False, nullable=True)
    required_points = db.Column(db.Integer, unique=False, nullable=True)
    value = db.Column(db.Float, unique=False, nullable=True)

class Reward_codes(db.Model): # Creates the SQL table for rewards codes
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), unique=False, nullable=True)
    user_id = db.Column(db.ForeignKey(Users.id), unique=False)
    reward_name = db.Column(db.ForeignKey(Rewards.name), unique=False)

class Tickets(db.Model): # Creates the SQL table for tickets
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey(Users.id), unique=False)
    amount_of_tickets = db.Column(db.Integer, unique=False, nullable=True)
    date = db.Column(db.String, unique=False, nullable=True)
    ticket_type = db.Column(db.String, unique=False, nullable=True)
    user_email = db.Column(db.ForeignKey(Users.email), unique=False)
    user_phone = db.Column(db.ForeignKey(Users.phone), unique=False)
    total = db.Column(db.Integer, unique=False, nullable=True)

class Rooms(db.Model): # Creates the SQL table for rooms
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)

class Bookings(db.Model): # Creates the SQL table for bookings 
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey(Users.id), unique=False)
    room_id = db.Column(db.ForeignKey(Rooms.id), unique=False)
    arrival_date = db.Column(db.String, unique=False, nullable=True)
    leaving_date = db.Column(db.String, unique=False, nullable=True)
    user_email = db.Column(db.ForeignKey(Users.email), unique=False)
    user_phone = db.Column(db.ForeignKey(Users.phone), unique=False)
    total = db.Column(db.Integer, unique=False, nullable=True)

class Animals(db.Model): # Creates the SQL table for animals
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=False, nullable=True)
    description = db.Column(db.String(200), unique=False, nullable=True)
    image_location = db.Column(db.String(60), unique=False, nullable=True)
    wikidescription = db.Column(db.String(1000), unique=False, nullable=True)

rooms_data = [ # Creates the data needed in the rooms table (can be changed)
    Rooms(name='Standard Room 1', description='A standard Room with two seperate Twin size beds and a bathroom', capacity=2, price=70),
    Rooms(name='Standard Room 2', description='A standard Room with two seperate Twin size beds and a bathroom', capacity=2, price=70),
    Rooms(name='Standard Room 3', description='A standard Room with two seperate Twin size beds and a bathroom', capacity=2, price=70),
    Rooms(name='Standard Room 4', description='A standard Room with two seperate Twin size beds and a bathroom', capacity=2, price=70),
    Rooms(name='King Room 1', description='A Large Room with one King size bed and a bathroom', capacity=2, price=80),
    Rooms(name='King Room 2', description='A Large Room with one King size bed and a bathroom', capacity=2, price=80),
    Rooms(name='Deluxe Suite 1', description='A Large Room with one Queen size bed, a bathroom and a balcony', capacity=2, price=90),
]
rewards_data = [ # Creates the data needed in the rewards table (can be changed)
    Rewards(name='10 Percent off!', description='A discount code that will give you 10 Percent off!', required_points=500, value=0.9),
    Rewards(name='20 Percent off!', description='A discount code that will give you 20 Percent off!', required_points=1000, value=0.8),
    Rewards(name='30 Percent off!', description='A discount code that will give you 30 Percent off!', required_points=1500, value=0.7),
    Rewards(name='40 Percent off!', description='A discount code that will give you 40 Percent off!', required_points=2000, value=0.6 ),
]
animals_data = [ # Creates the data needed in the animals table (can be changed)
    Animals(name='Lions', description='Lions have strong, compact bodies and powerful forelegs, teeth and jaws for pulling down and killing prey.', image_location='../static/images/Lion.jpg', wikidescription="The lion (Panthera leo) is a large cat of the genus Panthera, native to Africa and India. It has a muscular, broad-chested body; a short, rounded head; round ears; and a hairy tuft at the end of its tail. It is sexually dimorphic; adult male lions are larger than females and have a prominent mane. It is a social species, forming groups called prides. A lion's pride consists of a few adult males, related females, and cubs. Groups of female lions usually hunt together, preying mostly on large ungulates. The lion is an apex and keystone predator; although some lions scavenge when opportunities occur and have been known to hunt humans, lions typically do not actively seek out and prey on humans. The lion inhabits grasslands, savannahs, and shrublands. It is usually more diurnal than other wild cats, but when persecuted, it adapts to being active at night and at twilight. During the Neolithic period, the lion ranged throughout Africa and Eurasia, from Southeast Europe to India, but it has been reduced to fragmented populations in sub-Saharan Africa and one population in western India. It has been listed as Vulnerable on the IUCN Red List since 1996 because populations in African countries have declined by about 43 percent since the early 1990s. Lion populations are untenable outside designated protected areas. Although the cause of the decline is not fully understood, habitat loss and conflicts with humans are the greatest causes for concern. One of the most widely recognised animal symbols in human culture, the lion has been extensively depicted in sculptures and paintings, on national flags, and in literature and films. Lions have been kept in menageries since the time of the Roman Empire and have been a key species sought for exhibition in zoological gardens across the world since the late 18th century. Cultural depictions of lions were prominent in Ancient Egypt, and depictions have occurred in virtually all ancient and medieval cultures in the lion's historic and current range."),
    Animals(name='Giraffes', description="Giraffes are the world's tallest mammals, thanks to their towering legs and long necks", image_location='../static/images/Giraffe (2).jpg', wikidescription="The giraffe is a large African hoofed mammal belonging to the genus Giraffa. It is the tallest living terrestrial animal and the largest ruminant on Earth. Traditionally, giraffes have been thought of as one species, Giraffa camelopardalis, with nine subspecies. Most recently, researchers proposed dividing them into up to eight extant species due to new research into their mitochondrial and nuclear DNA, as well as morphological measurements. Seven other extinct species of Giraffa are known from the fossil record. The giraffe's chief distinguishing characteristics are its extremely long neck and legs, its horn-like ossicones, and its spotted coat patterns. It is classified under the family Giraffidae, along with its closest extant relative, the okapi. Its scattered range extends from Chad in the north to South Africa in the south, and from Niger in the west to Somalia in the east. Giraffes usually inhabit savannahs and woodlands. Their food source is leaves, fruits, and flowers of woody plants, primarily acacia species, which they browse at heights most other herbivores cannot reach. Lions, leopards, spotted hyenas, and African wild dogs may prey upon giraffes. Giraffes live in herds of related females and their offspring or bachelor herds of unrelated adult males, but are gregarious and may gather in large aggregations. Males establish social hierarchies through 'necking', combat bouts where the neck is used as a weapon. Dominant males gain mating access to females, which bear sole responsibility for rearing the young. The giraffe has intrigued various ancient and modern cultures for its peculiar appearance, and has often been featured in paintings, books, and cartoons. It is classified by the International Union for Conservation of Nature (IUCN) as vulnerable to extinction and has been extirpated from many parts of its former range. Giraffes are still found in numerous national parks and game reserves, but estimates as of 2016 indicate there are approximately 97,500 members of Giraffa in the wild. More than 1,600 were kept in zoos in 2010."),
    Animals(name='Elephants', description='Elephants are the largest land mammals on earth and have distinctly massive bodies, large ears, and long trunks.',image_location='../static/images/Elephant (2).jpg', wikidescription="Elephants are the largest living land animals. Three living species are currently recognised: the African bush elephant (Loxodonta africana), the African forest elephant (L. cyclotis), and the Asian elephant (Elephas maximus). They are the only surviving members of the family Elephantidae and the order Proboscidea; extinct relatives include mammoths and mastodons. Distinctive features of elephants include a long proboscis called a trunk, tusks, large ear flaps, pillar-like legs, and tough but sensitive grey skin. The trunk is prehensile, bringing food and water to the mouth and grasping objects. Tusks, which are derived from the incisor teeth, serve both as weapons and as tools for moving objects and digging. The large ear flaps assist in maintaining a constant body temperature as well as in communication. African elephants have larger ears and concave backs, whereas Asian elephants have smaller ears and convex or level backs. Elephants are scattered throughout sub-Saharan Africa, South Asia, and Southeast Asia and are found in different habitats, including savannahs, forests, deserts, and marshes. They are herbivorous, and they stay near water when it is accessible. They are considered to be keystone species, due to their impact on their environments. Elephants have a fission fusion society, in which multiple family groups come together to socialise. Females (cows) tend to live in family groups, which can consist of one female with her calves or several related females with offspring. The leader of a female group, usually the oldest cow, is known as the matriarch. Males (bulls) leave their family groups when they reach puberty and may live alone or with other males. Adult bulls mostly interact with family groups when looking for a mate. They enter a state of increased testosterone and aggression known as musth, which helps them gain dominance over other males as well as reproductive success. Calves are the centre of attention in their family groups and rely on their mothers for as long as three years. Elephants can live up to 70 years in the wild. They communicate by touch, sight, smell, and sound; elephants use infrasound and seismic communication over long distances. Elephant intelligence has been compared with that of primates and cetaceans. They appear to have self-awareness, and possibly show concern for dying and dead individuals of their kind. African bush elephants and Asian elephants are listed as endangered and African forest elephants as critically endangered by the International Union for Conservation of Nature (IUCN). One of the biggest threats to elephant populations is the ivory trade, as the animals are poached for their ivory tusks. Other threats to wild elephants include habitat destruction and conflicts with local people. Elephants are used as working animals in Asia. In the past, they were used in war; today, they are often controversially put on display in zoos, or employed for entertainment in circuses. Elephants have an iconic status in human culture, and have been widely featured in art, folklore, religion, literature, and popular culture."),
    Animals(name='Tigers', description='Tigers have reddish-orange coats with prominent black stripes, white bellies and white spots on their ears.', image_location='../static/images/Tiger.jpg', wikidescription="The tiger (Panthera tigris) is the largest living cat species and a member of the genus Panthera. It has a powerful, muscular body with a large head and paws, a long tail, and distinctive black, mostly vertical stripes on orange fur. It was first scientifically described in 1758 and is traditionally classified into eight recent subspecies though some recognize only two subspecies, mainland Asian tigers and island tigers of the Sunda Islands. Throughout the tiger's range, it inhabits mainly forests, from coniferous and temperate broadleaf and mixed forests in the Russian Far East and Northeast China to tropical and subtropical moist broadleaf forests on the Indian subcontinent and Southeast Asia. The tiger is an apex predator and preys mainly on ungulates such as deer and wild boar, which it takes by ambush. It lives a mostly solitary life and occupies home ranges, which it defends from individuals of the same sex. The range of a male tiger overlaps with that of multiple females with which he has reproductive claims. Females give birth to usually two or three cubs that stay with their mother for about two years. When becoming independent, they leave their mother's home range and establish their own. Since the early 20th century, tiger populations have lost at least 93 percent of their historic range and are locally extinct in West and Central Asia, in large areas of China and on the islands of Java and Bali. Today, the tiger’s range is severely fragmented. The species is listed as Endangered on the IUCN Red List, as its range is thought to have declined by 53% to 68 percent since the late 1990s. Major reasons for this decline are habitat destruction and habitat fragmentation due to deforestation, and poaching for fur and illegal trade of tiger body parts for medicinal purposes. Tigers are also victims of human wildlife conflict, due to encroachment in countries with a high human population density. Tigers sometimes attack and even prey on people. The tiger is among the most recognisable and popular of the world's charismatic megafauna. It has been kept in captivity since ancient times, and has been trained to perform in circuses and other entertainment shows. The species has been popular in the exotic pet trade. The tiger featured prominently in the ancient mythology and folklore of cultures throughout its historic range and has continued to appear in culture worldwide."),
]
with app.app_context(): # This function adds all the data to their tables and creates and commits them
    #db.drop_all() # This clears the database if needed UNCOMMENT IF NEEDED
    #for room in rooms_data:
        #db.session.add(room)
    #for reward in rewards_data:
        #db.session.add(reward)
    #for animal in animals_data:
        #db.session.add(animal)
    db.create_all()
    db.session.commit()

#--------------------DATABASE-CONFIGURATION--------------------#

#--------------------HOME-PAGE--------------------#

@app.route('/', methods=['GET','POST']) # This is the app route for the home page
def home(): # This funtion contains all the logic in the home page
    if 'basket' in session: # Checks if a user has returned from buying something
        session.pop('basket', None) # Will delete their basket if they have
    else:
        pass 
    return render_template('home.html') # Renders the home html template

#--------------------HOME-PAGE--------------------#

#--------------------LOGIN-PAGE--------------------#

@app.route('/login', methods=['GET','POST']) # This is the app route for the login page
def login(): # This function contains all the logic in the login page
    if request.method == 'POST': # Checks if html method is POST
        username = request.form['username'] # Requests username from the users end
        password = request.form['password'] # Requests password from user
        user = Users.query.filter_by(username=username).first() # Checks if username exists in the Users table
        if user and bcrypt.check_password_hash(user.password, password=password): # if user returns True amd the hashed password matches the stored password
            session['username'] = user.username # Creates a session for the user with their username
            return redirect(url_for('home')) # Redirects them to the home function
        else:
            return render_template('login.html', error='Email or password incorrect') # Retruns the login html template with an appropriate error message
    else:
        return render_template('login.html') # Renders the login html template if request isnt POST
    
#--------------------LOGIN-PAGE--------------------#

#--------------------REGISTER-PAGE--------------------#

@app.route('/register', methods=['GET','POST']) # Route for the register page
def register(): # Function containing the logic for the register page
    if request.method == 'POST': # If the html method is POST
        first_name = request.form['first_name'] # Requests attribute from html
        sur_name = request.form['sur_name'] # Requests attribute from html
        username = request.form['username'] # Requests attribute from html
        password = request.form['password'] # Requests attribute from html
        email = request.form['email'] # Requests attribute from html
        phone = request.form['phone'] # Requests attribute from html
        if len(password) < 8: # Basic password security check (can be improved)
            error = 'Password is not long enough, you need a minimum of 8 characters' # Defines the error message for the user
            return render_template('register.html', error=error) # Returns the template with error message
        else:
            pass
        existing_email = Users.query.filter_by(email=email).first() # Checks if attribute already exists in the table
        existing_phone = Users.query.filter_by(phone=phone).first() # Checks if attribute already exists in the table
        existing_username = Users.query.filter_by(username=username).first() # Checks if attribute already exists in the table
        if existing_email or existing_phone: # Checks if they return True
            return render_template('register.html', error='This phone number or email has already been used to create an account with us. Please try logging in.') # If so then it will return the template with appropriate error message
        elif existing_username: # Checks if it returns True
            return render_template('register.html', error='This username has already been taken, please try something else.') # If so it will return the html template with appropriate error message
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8') # Generates a password hash for the inputted password
            new_user = Users(first_name=first_name, sur_name=sur_name, username=username, password=hashed_password, email=email, phone=phone, points=0) # Defines the new user to be added to the user table
            db.session.add(new_user) # Adds them into the session
            db.session.commit() # Permenantly commits them into the database
            return redirect(url_for('login')) # Redirects them to the login page
    else:
        return render_template('register.html') # Returns the register template if method is not POST
    
#--------------------REGISTER-PAGE--------------------#

#--------------------LOGOUT-PAGE--------------------#

@app.route('/logout', methods=['GET', 'POST']) # The app route for the logout sequence
def logout(): # This function holds all the logic for the logout route
    session.pop('username', None) # deletes the users session and relpaces it will None
    return redirect(url_for('home')) # Redirects the user to the home page

#--------------------LOGOUT-PAGE--------------------#

#--------------------MY-BOOKINGS-PAGE--------------------#

@app.route('/my-bookings', methods=['GET','POST']) # The app route for the login check on this page
def my_bookings(): # This function checks if a user is logged in
    if 'username' in session: # checks if a user is logged in
        return redirect(url_for('my_bookings_page', username=session['username'])) # Redirects them to the my bookings page if they are
    else: 
        return redirect(url_for('login')) # Redirects them to the login page if they aren't

@app.route('/my-bookings/<username>', methods=['GET','POSTS']) # The app route for the my bookings page 
def my_bookings_page(username): # This is the app route for the my bookings page it holds all the logic for this page
    user = Users.query.filter_by(username=username).first() # Gets the users information through a query based on their username
    user_points = user.points # sets their points to a variable
    user_id = user.id # sets their id to a variable
    rewards = Rewards.query.all() # Gets all rewards in the rewards table
    rewards_names = [] # creates a list for the rewards names
    rewards_descriptions = [] # creates a list for the rewards descriptions
    rewards_required_points = [] # creates a list for the rewards points needed
    for reward in rewards: # iterates through the rewards in the query made
        if reward.required_points <= user_points: # compares the required points to the users points
            reward_name = reward.name # defines the reward name as a variable
            reward_description = reward.description # defines the reward description as a variable
            reward_required_points = reward.required_points # defines the reward points needed as a variable
            rewards_names.append(reward_name) # adds them onto the end of the name list made
            rewards_descriptions.append(reward_description) # adds them onto the end of the descriptions list made
            rewards_required_points.append(reward_required_points) #  adds them onto the end of the points needed list made
        else:
            pass
    if len(rewards_names) == 0: # Checks if the users points is 0
        rewards_message = 'You cannot access any rewards yet.' # provides appropriate message
    else:
        rewards_message = None #provides appropriate message
    user_bookings = Bookings.query.filter_by(user_id=user_id).all() # fetches all of the users booking based on their user id
    for booking in user_bookings: # iterates through the users bookings
        if booking.arrival_date < date.today().strftime('%Y-%m-%d'): # Checks if the booking is in the past
            user_bookings.remove(booking) # removes the booking from the user_bookings list if its from the past
        else:
            pass
    if len(user_bookings) == 0: # checks if any bookings are returned
        booking_message = 'No Bookings found' # provides appropriate message
    else:
        booking_message = None # provides appropriate message
    my_codes_query = Reward_codes.query.filter_by(user_id=user_id).all() # finds all the users rewards codes they have
    if len(my_codes_query) == 0: # checks if they dont have any
        codes_message = 'No Discount codes found' # provides appropriate error message
    else:
        codes_message = None # provides appropriate error message
    my_codes = [] # creates list for users codes
    my_code_names = [] # creates list for what the codes are for
    for code in my_codes_query: # iterates through the query made
        my_code = code.code # adds the codes to a variable
        code_name = code.reward_name # adds what the codes are for to a variable
        my_codes.append(my_code) # adds the codes to the end of the list made
        my_code_names.append(code_name) # adds what the codes are for the the end of the list made
    return render_template('my-bookings.html', username=username, user_points=user_points, user_bookings=user_bookings, rewards_names=rewards_names, rewards_descriptions=rewards_descriptions, rewards_required_points=rewards_required_points, booking_message=booking_message, my_codes=my_codes, my_code_names=my_code_names, codes_message=codes_message, rewards_message=rewards_message) # renders the html template with all the variables
    
#--------------------MY-BOOKINGS-PAGE--------------------#

#--------------------REWARDS--------------------#

@app.route('/get-reward/<username>/<reward_name>', methods=['GET','POST']) # This is the route for claiming rewards
def get_reward(reward_name, username): # This function contains all the logic for claiming a reward
    reward_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(1, 16)) # This generates a random string of numbers and letters that is 16 characters long
    session['reward'] = [] # creates an empty session where the reward code will go
    session['reward'].append(reward_code) # adds on the reward code to the session
    user = Users.query.filter_by(username=username).first() # makes a query to get the user based on their username
    reward = Rewards.query.filter_by(name=reward_name).first() # makes a query to find the rewards name bases on the reward name
    reward_amount = reward.required_points # assigns the required points for the reward to a variable
    user.points = user.points - reward_amount # takes away the required points from the users points
    db.session.commit() # commits that to the session
    new_code = Reward_codes(code=reward_code, user_id=user.id, reward_name=reward_name) # creates a new_code to be added to the sql table with the variables
    db.session.add(new_code) # adds the new code to the session
    db.session.commit() # commits the new code to the session
    return redirect(url_for('my_bookings', username=username)) # redirects the user back to the my bookings page with their username

#--------------------REWARDS--------------------#

#--------------------CANCEL-BOOKINGS--------------------#

@app.route('/cancel-booking/<username>/<booking_id>', methods=['GET','POST']) # this is the route for cancelling bookings
def cancel_booking(booking_id, username): # this holds the logic for cancelling bookings
    username = session['username'] # gets the username from the session
    booking = Bookings.query.filter_by(id=booking_id).delete() # makes query to find the booking based on the id
    db.session.commit() # commits it to the session
    return redirect(url_for('my_bookings', username=username)) # returns the user back to the my bookings page

#--------------------CANCEL-BOOKINGS--------------------#

#--------------------TICKETS-PAGE--------------------#

@app.route('/tickets', methods=['GET','POST']) # This is the route to check a user is logged in for the tickets page
def tickets(): # A user is checked whether they are in session and then return to the appropriate page if they are, if they arent then they go to the login page
    if 'username' in session:
        return redirect(url_for('tickets_page', username=session['username']))
    else: 
        return redirect(url_for('login'))

@app.route('/tickets/<username>', methods=['GET','POST']) # This is the route for the tickets page
def tickets_page(username): # this function contains all the information for the tickets page
    todays_date = date.today().strftime('%Y-%m-%d') # finds todays todays date in order to set min values in the html file
    if request.method == 'POST': # checks if the method is POST
        amount_of_tickets = request.form['amount_of_tickets'] # assings the attribute from the user to a variable
        visit_date = request.form['date'] # assings the attribute from the user to a variable
        ticket_type = request.form['ticket_type'] # assings the attribute from the user to a variable
        requests = request.form['requests'] # assings the attribute from the user to a variable
        count = 0 # sets the count of tickets to zero
        for item in Tickets.query.filter_by(date=visit_date).all(): # iterates through how many entrys have been made in the database for that day
            count = count +1 # increases the count for that day
        if count >= 100: # checks if the count is below 100
            return render_template('tickets.html', username=username, error='We have sold out for this day, please try another day', todays_date=todays_date) # returns the html template and provides the appropriate error message
        else:
            session['basket'] = [] # sets a new session for basket as empty
            session['basket'].append('Tickets') # appends the word tickets to the basket (this is used later for checking what type of checkout we need)
            session['basket'].append(ticket_type) # adds on the ticket type to the end
            session['basket'].append(amount_of_tickets) # adds on the amount of tickets to the end
            session['basket'].append(visit_date) # adds on the visit date to the end
            session.modified = True # sets the session modification to true in order to keep it modable
            return redirect(url_for('order_confirm', username=session['username'])) # redirects the user to the order confirm page
    else:
        return render_template('tickets.html', username=username, todays_date=todays_date) # returns the tickets html template with variables
    
#--------------------TICKETS-PAGE--------------------#

#--------------------EDUCATIONAL-RESOURCES-PAGE--------------------#

@app.route('/educational-resources', methods=['GET', 'POST']) # route for the educational resources page
def educational_resources(): # this function contains the logic for the educational resources page
    all_animals = Animals.query.all() # gets all animals from the SQL table
    animals_names = [] # creates a new empty list for animal names
    animals_descriptions = [] # creates a new empty list for animal descriptions
    for animal in all_animals: # iterates through the query made
        animal_name = animal.name #  assigns the name to a variable
        animal_description = animal.description # assigns the description to a variable
        animals_names.append(animal_name) # assigns the name to the name list
        animals_descriptions.append(animal_description) # assings the description to the description list
    return render_template('educational-resources.html', animals_descriptions=animals_descriptions, animals_names=animals_names) # returns the template with variables

#--------------------EDUCATIONAL-RESOURCES-PAGE--------------------#

#--------------------CONTACT-US-PAGE--------------------#

@app.route('/contact-us', methods=['GET', 'POST']) # this is the route for the contact us page
def contact_us(): # this contains the logic for the contact us page
    return render_template('contact-us.html') # returns the html template

#--------------------CONTACT-US-PAGE--------------------#

#--------------------ORDER-CONFIRM-PAGE--------------------#

@app.route('/order-confirm/<username>', methods=['GET','POST']) #  this is the route for the order confirm page
def order_confirm(username): # this fucntion contains the logic for the order confirm page
    todays_date = date.today().strftime('%Y-%m-%d') # sets todays date as a variable
    basket=session['basket'] # sets the basket session as a variable
    if basket[0] == 'Tickets': # checks if the first item in the basket is tickets
        if basket[1] == 'Premium': # checks if the second item in the basket is premium
            price = 20 # sets the price of that ticket
        else:
            price = 10 #sets the price of the ticket
            price = price * int(basket[2]) # updates the price variable by how many tickets you ordered
    elif basket[0] == 'Hotel': # checks if the first item in basket is hotel
        price = basket[2] # gets the price of the hotel room you booked
        user_checkin_date = session['user_checkin_date'] # gets the user checkin date from the session
        user_checkout_date = session['user_checkout_date'] # gets the user checkout date from the session
        arrival= datetime.strptime(user_checkin_date, "%Y-%m-%d") # structures the arrival date as the user checkin date
        leave = datetime.strptime(user_checkout_date, "%Y-%m-%d") # structures the leaving date as the user checkout date
        days = abs((leave - arrival).days) # finds the amount of days in the user is there for
        price = price * days # times the price by how many days
    else:
        print('an error has occured') # provide error message on the server side
    points = price * 2 # set the amount of points the user gets
    if request.method == 'POST': # checks if the method is post
        card_number = request.form['card_number'] # gets attribute from users end
        cvv = request.form['cvv'] # gets attribute from users end
        expiry_date = request.form['expiry_date'] # gets attribute from users end
        first_address_line = request.form['first_address_line'] # gets attribute from users end
        second_address_line = request.form['second_address_line'] # gets attribute from users end
        city = request.form['city'] # gets attribute from users end
        county = request.form['county'] # gets attribute from users end
        discount = request.form['discount'] # gets attribute from users end
        user = Users.query.filter_by(username=username).first() # finds the users information based on their username
        user_id = user.id # sets their user id to a variable
        rewards_codes = Reward_codes.query.filter_by(user_id=user_id).all() # finds the rewards codes that the user has
        for reward_code in rewards_codes: #iterates through the reward codes
            if reward_code.code == discount: # checks if they match the discount code
                reward_value = Rewards.query.filter_by(name=reward_code.reward_name).first() # find the value of the reward code if it matches
                reward_value = reward_value.value # sets the value to a variable
                price = price / reward_value # apply the discount code
                break # ends the for loop
            else:
                pass
        user = Users.query.filter_by(username=username).first() # finds the user based on their name
        if basket[0] == 'Tickets': # checks if the user is ordering tickets or a room
            new_ticket = Tickets(user_id=user.id, amount_of_tickets=basket[1], date=basket[2], user_email=user.email, user_phone=user.phone, total=price) # creates new item in SQL table
            db.session.add(new_ticket) # commits it to the session
        else:
            new_hotel_booking = Bookings( user_id=user.id, room_id=basket[3], arrival_date=user_checkin_date, leaving_date=user_checkout_date, user_email=user.email, user_phone=user.phone, total=price) # creates new item in SQL table
            db.session.add(new_hotel_booking) # commits it to the session
        user.points += points # adds the user points
        db.session.commit() #commits it to the sesison
        remove_code = Reward_codes.query.filter_by(code=reward_code.code).delete() # delets the users discount code they used
        db.session.commit() # commits it to the session
        return render_template('order-confirm.html', message='Payment confirmed', basket=None, price=None, points=points, todays_date=todays_date) # returns the approproate template and message
    else:
        if basket[0] == 'Tickets': # checks if basket is tickets
            return render_template('order-confirm.html', username=username, basket=basket, price=price, points=points, todays_date=todays_date) # returns the approproate template and message
        else:
            return render_template('order-confirm.html', username=username, basket=basket, price=price, points=points, todays_date=todays_date, nights=days) # returns the approproate template and message
    
#--------------------ORDER-CONFIRM-PAGE--------------------#

#--------------------TERMS-AND-CONDITIONS-PAGE--------------------#

@app.route('/terms-and-conditions', methods=['GET','POST']) # this is the route for the terms and conditions page
def terms_and_conditions(): # this contains the logic for the terms and conditions page
    return render_template('terms-and-conditions.html') # returns the html template

#--------------------TERMS-AND-CONDITIONS-PAGE--------------------#

#--------------------SCHOOL-TICKETS-PAGE--------------------#

@app.route('/school-tickets', methods=['GET','POST'])
def school_tickets(): # A user is checked whether they are in session and then return to the appropriate page if they are, if they arent then they go to the login page
    if 'username' in session:
        return redirect(url_for('school_tickets_page', username=session['username']))
    else: 
        return redirect(url_for('login'))

@app.route('/school-tickets/<username>', methods=['GET','POST']) # THIS ROUTE HAS THE SAME LOGIC AS THE TICKETS PAGE 
def school_tickets_page(username):
    todays_date = date.today().strftime('%Y-%m-%d')
    if request.method == 'POST':
        amount_of_tickets = request.form['amount_of_tickets']
        visit_date = request.form['date']
        ticket_type = request.form['ticket_type']
        requests = request.form['requests']
        count = 0
        for item in Tickets.query.filter_by(date=visit_date).all():
            count = count +1
        if count >= 100:
            return render_template('school-tickets.html', username=username, error='We have sold out for this day, please try another day', todays_date=todays_date)
        else:
            session['basket'] = []
            session['basket'].append('Tickets')
            session['basket'].append(ticket_type)
            session['basket'].append(amount_of_tickets)
            session['basket'].append(visit_date)
            session.modified = True
            print (session['basket'])
            return redirect(url_for('order_confirm', username=session['username']))
    else:
        return render_template('school-tickets.html', username=username, todays_date=todays_date)
    
#--------------------SCHOOL-TICKETS-PAGE--------------------#

#--------------------PICK-DATE-PAGE--------------------#

@app.route('/pick-date', methods=['GET','POST'])
def pick_date(): # A user is checked whether they are in session and then return to the appropriate page if they are, if they arent then they go to the login page
    if 'username' in session:
        return redirect(url_for('pick_date_page', username=session['username']))
    else: 
        return redirect(url_for('login'))
    

@app.route('/pick-date/<username>', methods=['GET', 'POST']) # This is the route for the pick a date page
def pick_date_page(username): # this function holds all the logic for the pick a date page
    min_date = date.today() # sets the minimum date as today
    max_date =  min_date + relativedelta(years=1) # sets the maximum date as a year from now
    if request.method == 'POST': # checks if the method is post
        user_checkin_date = request.form['user_checkin_date'] # request attribute form html
        user_checkout_date = request.form['user_checkout_date'] # request attribute form html
        if user_checkin_date == user_checkout_date: #  checks if the user checkin date is the same as the user checkout date
            error='Please select a check out date ahead of your check in date' # creates appropriate error message
            return render_template('pick-date.html', min_date=min_date, max_date=max_date, error=error) # returns the html template
        user = Users.query.filter_by(username=username).first() # find the user based on their username
        session['user_checkin_date'] = user_checkin_date # creates a session with the attribute pulled from html
        session['user_checkout_date'] = user_checkout_date # creates a session with the attribute pulled from html
        session.modified = True # sets it so sessions are modified
        return bookings_page(username, user_checkin_date, user_checkout_date) # returns the booking page with variables
    else:
        return render_template('pick-date.html', min_date=min_date, max_date=max_date) # returns the template  with variables
    
#--------------------PICK-DATE-PAGE--------------------#

#--------------------BOOKINGS-PAGE--------------------#

@app.route('/bookings', methods=['GET','POST'])
def bookings(): # A user is checked whether they are in session and then return to the appropriate page if they are, if they arent then they go to the login page
    if 'username' in session:
        return redirect(url_for('bookings_page', username=session['username']))
    else:
        return redirect(url_for('login'))

@app.route('/bookings/<username>/<user_checkin_date>/<user_checkout_date>', methods=['GET','POSTS']) # This is the rotes for the bookings page
def bookings_page(username, user_checkin_date, user_checkout_date): # this funtion holds all the logic for the bookings page
    room_bookings = db.session.query(Bookings.room_id).filter( # this variable finds room bookings based on the selected user checkin and checkout dates
        or_(
        and_(Bookings.arrival_date <= user_checkin_date, Bookings.leaving_date >= user_checkin_date),
        and_(Bookings.arrival_date <= user_checkout_date, Bookings.leaving_date >= user_checkout_date),
        and_(Bookings.arrival_date >= user_checkin_date, Bookings.leaving_date <= user_checkout_date)
    )).all()
    room_bookings_ids = [room[0] for room in room_bookings] #find the ids in the rooms that are in the variable
    all_rooms = Rooms.query.all() # query to find all rooms
    free_rooms = [room for room in all_rooms if room.id not in room_bookings_ids ] # finds the free rooms by iterating through the rooms 
    room_names = [] # creates a list for room names
    room_descriptions = [] # creates a list for room descritpions
    room_capacitys = [] # creates a list for room capacitys
    room_prices = [] # creates a list for room prices
    for room in free_rooms: # iterates through the rooms in free rooms
        room_name = room.name # adds the attribute of the room to a variable
        room_description = room.description # adds the attribute of the room to a variable
        room_capacity = room.capacity # adds the attribute of the room to a variable
        room_price = room.price # adds the attribute of the room to a variable
        room_names.append(room_name) # adds the attribute of the rooms to the list
        room_descriptions.append(room_description) # adds the attribute of the rooms to the list
        room_capacitys.append(room_capacity) # adds the attribute of the rooms to the list
        room_prices.append(room_price) # adds the attribute of the rooms to the list
    return render_template('bookings.html', username=username, user_checkout_date=user_checkout_date, user_checkin_date=user_checkin_date, room_names=room_names,
                           room_descriptions=room_descriptions, room_capacitys=room_capacitys, room_prices=room_prices)# This returns the html template with all the variables

#--------------------BOOKINGS-PAGE--------------------#

#--------------------BOOK-ACTION--------------------#

@app.route('/book/<username>/<room_name>', methods=['GET','POST']) # This is the route which provides the logic of adding the selected room to the basket
def book(room_name, username): # this holds the logic for this action
        rooms = Rooms.query.filter_by(name=room_name).first() # finds the rooms by the room name
        room_price = rooms.price # gets the price of the room as a variable
        room_id = rooms.id #gets the room id as a variable
        username=session['username'] # gets the users username from the session
        session['basket'] = [] # sets the basket as empty
        session['basket'] = ['Hotel'] # adds hotel to the basket (this is used in checkout)
        session['basket'].append(room_name) # adds the room name onto the end
        session['basket'].append(room_price) # adds the room price onto the end
        session['basket'].append(room_id) # adds the room id onto the end
        session.modified = True # sets the session as modifyable
        return redirect(url_for('order_confirm', username=username)) # redirects the user to the order confirmation page

#--------------------BOOK-ACTION--------------------#

#--------------------ANIMALS-PAGE--------------------#

@app.route('/animal/<animal_name>', methods=['GET','POST']) # This is the page route for each animal
def animal(animal_name): #this holds the logic for the animal function
    animal = Animals.query.filter_by(name=animal_name).first() # gets the animal based on the name selected in the link
    animal_description = animal.wikidescription # gets the description of this animal from the query
    animal_image = animal.image_location # gets the unique image for this animal
    return render_template('animal.html', animal_name=animal_name, animal_description=animal_description, animal_image=animal_image) # renders the template with the unique variables

#--------------------ANIMALS-PAGE--------------------#

#--------------------RUN--------------------#
if __name__ == '__main__': # this runs the program is the name is main
    app.run() #the main run sequence
#--------------------RUN--------------------#
