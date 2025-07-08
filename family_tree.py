

# Full working script: family_tree.py
# Features: Add person, relationship, event, memo, search, view, visualize
# Requirements: sqlalchemy, graphviz

from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import graphviz

Base = declarative_base()

class Person(Base):
    __tablename__ = 'persons'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    dob = Column(Date, nullable=True)
    dod = Column(Date, nullable=True)
    events = relationship("Event", back_populates="person")
    memos = relationship("Memo", back_populates="person")

class Relationship(Base):
    __tablename__ = 'relationships'
    id = Column(Integer, primary_key=True)
    person1_id = Column(Integer, ForeignKey('persons.id'))
    person2_id = Column(Integer, ForeignKey('persons.id'))
    relation_type = Column(String)
    person1 = relationship("Person", foreign_keys=[person1_id], backref="rel1")
    person2 = relationship("Person", foreign_keys=[person2_id], backref="rel2")

class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('persons.id'))
    event_type = Column(String)
    event_date = Column(Date)
    description = Column(Text)
    person = relationship("Person", back_populates="events")

class Memo(Base):
    __tablename__ = 'memos'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('persons.id'))
    content = Column(Text)
    person = relationship("Person", back_populates="memos")

engine = create_engine('sqlite:///family_tree.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        return None

def add_person():
    name = input("Name: ")
    dob = parse_date(input("Date of Birth (YYYY-MM-DD): "))
    dod = parse_date(input("Date of Death (YYYY-MM-DD or blank): "))
    person = Person(name=name, dob=dob, dod=dod)
    session.add(person)
    session.commit()
    print(f"Added person with ID: {person.id}")

def add_relationship():
    id1 = int(input("Person 1 ID: "))
    id2 = int(input("Person 2 ID: "))
    relation = input("Relation type (parent/child/spouse/etc.): ")
    rel = Relationship(person1_id=id1, person2_id=id2, relation_type=relation)
    session.add(rel)
    session.commit()
    print("Relationship added.")

def add_event():
    pid = int(input("Person ID: "))
    etype = input("Event type (birth/marriage/etc.): ")
    edate = parse_date(input("Date (YYYY-MM-DD): "))
    desc = input("Description: ")
    event = Event(person_id=pid, event_type=etype, event_date=edate, description=desc)
    session.add(event)
    session.commit()
    print("Event added.")

def add_memo():
    pid = int(input("Person ID: "))
    text = input("Memo text: ")
    memo = Memo(person_id=pid, content=text)
    session.add(memo)
    session.commit()
    print("Memo added.")

def search_person():
    name = input("Enter name to search: ")
    people = session.query(Person).filter(Person.name.contains(name)).all()
    for p in people:
        print(f"{p.id}: {p.name} (DOB: {p.dob}, DOD: {p.dod})")

def view_person():
    pid = int(input("Enter Person ID: "))
    person = session.query(Person).get(pid)
    if not person:
        print("Not found.")
        return
    print(f"\nName: {person.name}\nDOB: {person.dob}\nDOD: {person.dod}")
    print("\nEvents:")
    for e in person.events:
        print(f"  {e.event_type} on {e.event_date}: {e.description}")
    print("\nMemos:")
    for m in person.memos:
        print(f"  {m.content}")
    print("\nRelationships:")
    rels = session.query(Relationship).filter(
        (Relationship.person1_id == pid) | (Relationship.person2_id == pid)).all()
    for r in rels:
        print(f"  {r.person1.name} -[{r.relation_type}]-> {r.person2.name}")

def visualize_family_tree():
    pid = int(input("Enter Person ID to visualize: "))
    depth = int(input("Enter depth (e.g., 2): ") or 2)
    dot = graphviz.Digraph(comment='Family Tree')
    visited = set()

    def dfs(current_id, current_depth):
        if current_depth > depth or current_id in visited:
            return
        person = session.query(Person).get(current_id)
        if not person:
            return
        label = f"{person.name}\n({person.dob} - {person.dod or 'Alive'})"
        dot.node(str(current_id), label)
        visited.add(current_id)
        relationships = session.query(Relationship).filter(
            (Relationship.person1_id == current_id) | (Relationship.person2_id == current_id)).all()
        for rel in relationships:
            other_id = rel.person2_id if rel.person1_id == current_id else rel.person1_id
            dfs(other_id, current_depth + 1)
            dot.edge(str(current_id), str(other_id), label=rel.relation_type)

    dfs(pid, 0)
    dot.render('family_tree', format='png', cleanup=True)
    print("Family tree saved as 'family_tree.png'.")

def menu():
    while True:
        print("\n--- Family Tree Menu ---")
        print("1. Add person")
        print("2. Add relationship")
        print("3. Add event")
        print("4. Add memo")
        print("5. Search person")
        print("6. View person details")
        print("7. Visualize family tree")
        print("0. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            add_person()
        elif choice == "2":
            add_relationship()
        elif choice == "3":
            add_event()
        elif choice == "4":
            add_memo()
        elif choice == "5":
            search_person()
        elif choice == "6":
            view_person()
        elif choice == "7":
            visualize_family_tree()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")

menu()

if __name__ == "__main__":
    menu()
