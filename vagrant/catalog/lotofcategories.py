from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Categories, Base, Item, User

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# User
user1 = User(name="Alan Marrone", email="marone.alan@gmail.com")

session.add(user1)
session.commit()

# Menu for Soccer
category1 = Categories(user_id=1, name="Soccer")

session.add(category1)
session.commit()

# Itens for Soccer
item1 = Item(user_id=1, name="Soccer item 1", description="Item1 from category"
             " Soccer", categories=category1)

session.add(item1)
session.commit()

item2 = Item(user_id=1, name="Soccer item 2", description="Item2 from category"
             " Soccer", categories=category1)

session.add(item2)
session.commit()

item3 = Item(user_id=1, name="Soccer item 3", description="Item3 from category"
             " Soccer", categories=category1)

session.add(item3)
session.commit()

item4 = Item(user_id=1, name="Soccer item 4", description="Item4 from category"
             " Soccer", categories=category1)


session.add(item4)
session.commit()

# Menu for Basketball
category2 = Categories(user_id=1, name="Basketball")

session.add(category2)
session.commit()

# Itens for Basketball
item1 = Item(user_id=1, name="Basketball item 1",
             description="Item1 from category Basketball",
             categories=category2)

session.add(item1)
session.commit()

item2 = Item(user_id=1, name="Basketball item 2",
             description="Item2 from category Basketball",
             categories=category2)

session.add(item2)
session.commit()

item3 = Item(user_id=1, name="Basketball item 3",
             description="Item3 from category Basketball",
             categories=category2)

session.add(item3)
session.commit()

# Menu for Skating
category3 = Categories(user_id=1, name="Skating")

session.add(category3)
session.commit()

# Itens for Skating
item1 = Item(user_id=1, name="Skating item 1", description="Item1 from"
             " category Skating", categories=category3)

session.add(item1)
session.commit()

item2 = Item(user_id=1, name="Skating item 2", description="Item2 from"
             " category Skating", categories=category3)

session.add(item2)
session.commit()

# Menu for Rock Climbing
category4 = Categories(user_id=1, name="Rock Climbing")

session.add(category4)
session.commit()

# Itens for Rock Climbing
item1 = Item(user_id=1, name="Rock Climbing item 1",
             description="Item1 from category Rock Climbing",
             categories=category4)

session.add(item1)
session.commit()


print "added menu items!"
