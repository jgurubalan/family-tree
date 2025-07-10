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
    events = relationship("Event", back_populates="person", cascade="all, delete-orphan")
    memos = relationship("Memo", back_populates="person", cascade="all, delete-orphan")

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

def input_int(prompt):
    try:
        return int(input(prompt))
    except ValueError:
        print("Invalid input. Expected a number.")
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
    id1 = input_int("Person 1 ID: ")
    id2 = input_int("Person 2 ID: ")
    if id1 is None or id2 is None: return
    relation = input("Relation type (parent/child/spouse/etc.): ")
    rel = Relationship(person1_id=id1, person2_id=id2, relation_type=relation)
    session.add(rel)
    session.commit()
    print("Relationship added.")

def add_event():
    pid = input_int("Person ID: ")
    if pid is None: return
    print("Event types: birth, marriage, death, graduation, etc.")
    etype = input("Event type: ")
    edate = parse_date(input("Date (YYYY-MM-DD): "))
    desc = input("Description: ")
    event = Event(person_id=pid, event_type=etype, event_date=edate, description=desc)
    session.add(event)
    session.commit()
    print("Event added.")

def add_memo():
    pid = input_int("Person ID: ")
    if pid is None: return
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
    pid = input_int("Enter Person ID: ")
    if pid is None: return
    person = session.get(Person, pid)
    if not person:
        print("Not found.")
        return
    print(f"\nName: {person.name}\nDOB: {person.dob}\nDOD: {person.dod}")
    print("\nEvents:")
    for e in person.events:
        print(f"  {e.event_type} on {e.event_date}: {e.description}")
    print("\nMemos:")
    for m in person.memos:
        print(f"  {m.content[:80]}{'...' if len(m.content) > 80 else ''}")
    print("\nRelationships:")
    rels = session.query(Relationship).filter(
        (Relationship.person1_id == pid) | (Relationship.person2_id == pid)).all()
    for r in rels:
        p1 = r.person1.name if r.person1 else f"[Missing ID {r.person1_id}]"
        p2 = r.person2.name if r.person2 else f"[Missing ID {r.person2_id}]"
        print(f"  {p1} -[{r.relation_type}]-> {p2}")

def edit_person():
    pid = input_int("Enter Person ID to edit: ")
    if pid is None: return
    person = session.get(Person, pid)
    if not person:
        print("Person not found.")
        return
    print(f"Editing {person.name}...")
    name = input(f"New name (blank to keep '{person.name}'): ") or person.name
    dob = parse_date(input(f"New DOB (blank to keep '{person.dob}'): ") or str(person.dob))
    dod = parse_date(input(f"New DOD (blank to keep '{person.dod}'): ") or str(person.dod))
    person.name = name
    person.dob = dob
    person.dod = dod
    session.commit()
    print("Person updated.")

def delete_person():
    pid = input_int("Enter Person ID to delete: ")
    if pid is None: return
    person = session.get(Person, pid)
    if not person:
        print("Person not found.")
        return
    confirm = input(f"Are you sure you want to delete {person.name}? (y/n): ")
    if confirm.lower() == 'y':
        session.delete(person)
        session.commit()
        print("Person deleted.")

def edit_relationship():
    rid = input_int("Enter Relationship ID to edit: ")
    if rid is None: return
    rel = session.get(Relationship, rid)
    if not rel:
        print("Relationship not found.")
        return
    print(f"Editing: {rel.person1.name if rel.person1 else 'Unknown'} -[{rel.relation_type}]-> {rel.person2.name if rel.person2 else 'Unknown'}")
    new_type = input(f"New relation type (blank to keep '{rel.relation_type}'): ") or rel.relation_type
    rel.relation_type = new_type
    session.commit()
    print("Relationship updated.")

def delete_relationship():
    rid = input_int("Enter Relationship ID to delete: ")
    if rid is None: return
    rel = session.get(Relationship, rid)
    if not rel:
        print("Relationship not found.")
        return
    session.delete(rel)
    session.commit()
    print("Relationship deleted.")

def visualize_family_tree():
    pid = input_int("Enter Person ID to visualize: ")
    if pid is None: return
    depth = input_int("Enter depth (e.g., 2): ") or 2
    dot = graphviz.Digraph(comment='Family Tree')
    dot.attr(rankdir='TB')
    dot.attr('node', shape='box', style='filled', color='lightgrey')
    visited = set()

    def dfs(current_id, current_depth):
        if current_depth > depth or current_id in visited:
            return
        person = session.get(Person, current_id)
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

def list_all_entries():
    print("\n--- People ---")
    people = session.query(Person).all()
    if not people:
        print("No people found.")
    else:
        for p in people:
            print(f"{p.id}: {p.name} (DOB: {p.dob}, DOD: {p.dod})")

    print("\n--- Relationships ---")
    rels = session.query(Relationship).all()
    if not rels:
        print("No relationships found.")
    else:
        for r in rels:
            p1_name = r.person1.name if r.person1 else f"[Missing ID {r.person1_id}]"
            p2_name = r.person2.name if r.person2 else f"[Missing ID {r.person2_id}]"
            print(f"{r.id}: {p1_name} -[{r.relation_type}]-> {p2_name}")

    broken = [r for r in rels if not r.person1 or not r.person2]
    if broken:
        print(f"\nFound {len(broken)} broken relationship(s).")
        confirm = input("Do you want to delete them? (y/n): ")
        if confirm.lower() == 'y':
            for r in broken:
                session.delete(r)
            session.commit()
            print("Broken relationships deleted.")

    print("\n--- Events ---")
    events = session.query(Event).all()
    if not events:
        print("No events found.")
    else:
        for e in events:
            print(f"{e.id}: Person ID {e.person_id}, Type: {e.event_type}, Date: {e.event_date}, Desc: {e.description}")

    print("\n--- Memos ---")
    memos = session.query(Memo).all()
    if not memos:
        print("No memos found.")
    else:
        for m in memos:
            print(f"{m.id}: Person ID {m.person_id}, Memo: {m.content[:80]}{'...' if len(m.content) > 80 else ''}")

def infer_parent_from_sibling_relationships():
    inferred = 0
    siblings = session.query(Relationship).filter(Relationship.relation_type.in_(['brother', 'sister'])).all()

    for rel in siblings:
        p1_id, p2_id = rel.person1_id, rel.person2_id

        # Find known parents of person1
        p1_parents = session.query(Relationship).filter_by(person1_id=p1_id, relation_type='child').all()
        p2_parents = session.query(Relationship).filter_by(person1_id=p2_id, relation_type='child').all()

        # If person1 has parents and person2 does not, assign those parents to person2
        if p1_parents and not p2_parents:
            for pr in p1_parents:
                already = session.query(Relationship).filter_by(
                    person1_id=p2_id, person2_id=pr.person2_id, relation_type='child').first()
                if not already:
                    session.add(Relationship(person1_id=p2_id, person2_id=pr.person2_id, relation_type='child'))
                    print(f"Inferred: {session.get(Person, p2_id).name} is also child of {session.get(Person, pr.person2_id).name}")
                    inferred += 1

        # Same logic in reverse
        elif p2_parents and not p1_parents:
            for pr in p2_parents:
                already = session.query(Relationship).filter_by(
                    person1_id=p1_id, person2_id=pr.person2_id, relation_type='child').first()
                if not already:
                    session.add(Relationship(person1_id=p1_id, person2_id=pr.person2_id, relation_type='child'))
                    print(f"Inferred: {session.get(Person, p1_id).name} is also child of {session.get(Person, pr.person2_id).name}")
                    inferred += 1

    session.commit()
    if inferred == 0:
        print("No parent relationships inferred.")
    else:
        print(f"{inferred} parent relationship(s) inferred.")


def menu():
    while True:
        print("\n--- Family Tree Menu ---")
        print("1. Add person\n2. Add relationship\n3. Add event\n4. Add memo")
        print("5. Search person\n6. View person details\n7. Visualize family tree")
        print("8. Edit person\n9. Delete person\n10. Edit relationship\n11. Delete relationship")
        print("12. List all entries")
        print("13. Infer parent-child from sibling relationships")
        print("0. Exit")
        choice = input("Enter your choice: ")
        actions = {
            "1": add_person, "2": add_relationship, "3": add_event, "4": add_memo,
            "5": search_person, "6": view_person, "7": visualize_family_tree,
            "8": edit_person, "9": delete_person, "10": edit_relationship,
            "11": delete_relationship, "12": list_all_entries, "13": infer_parent_from_sibling_relationships
        }
        if choice == "0":
            print("Goodbye!")
            break
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    menu()
