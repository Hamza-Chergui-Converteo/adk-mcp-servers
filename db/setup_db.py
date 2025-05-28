# setup_db.py
import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker

# Setup
fake = Faker("fr_FR")
conn = sqlite3.connect("crm.db")
cursor = conn.cursor()

# Création des tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS prospects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    email TEXT,
    last_contact TEXT,
    status TEXT,
    last_activity TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prospect_name TEXT,
    type TEXT,
    contenu TEXT,
    date TEXT,
    FOREIGN KEY(prospect_name) REFERENCES prospects(name)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    industry TEXT,
    address TEXT,
    website TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS deals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prospect_id INTEGER,
    title TEXT,
    amount REAL,
    stage TEXT,
    close_date TEXT,
    FOREIGN KEY(prospect_id) REFERENCES prospects(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prospect_id INTEGER,
    title TEXT,
    due_date TEXT,
    completed BOOLEAN,
    FOREIGN KEY(prospect_id) REFERENCES prospects(id)
)
""")

# Génération de 100 prospects fictifs
statuses = ["Contacté", "En Négociation", "Client", "Perdu"]
activities = ["Appel téléphonique", "Email envoyé", "Réunion Zoom", "Démonstration produit"]

prospects_data = []
companies_raw = []
interactions_data = []
deals_data = []
tasks_data = []

for _ in range(100):
    name = fake.name()
    email = fake.email()
    last_contact = fake.date_between(start_date='-60d', end_date='today').isoformat()
    status = random.choice(statuses)
    last_activity = random.choice(activities)
    prospects_data.append((name, email, last_contact, status, last_activity))

    company_name = fake.company()
    industry = fake.job()
    address = fake.address().replace("\n", ", ")
    website = fake.url()
    companies_raw.append((company_name, industry, address, website))

    interactions_data.append((name, "Appel", fake.text(max_nb_chars=100), last_contact))

    amount = round(random.uniform(500, 5000), 2)
    close_date = (datetime.now() + timedelta(days=random.randint(10, 90))).isoformat()
    deals_data.append((None, f"Offre pour {company_name}", amount, "Proposition envoyée", close_date))

    due_date = (datetime.now() + timedelta(days=random.randint(1, 30))).isoformat()
    tasks_data.append((None, f"Suivre {name}", due_date, random.choice([True, False])))

# Insertion des prospects
cursor.executemany("""
INSERT OR IGNORE INTO prospects (name, email, last_contact, status, last_activity)
VALUES (?, ?, ?, ?, ?)
""", prospects_data)

# Récupération des IDs prospects
cursor.execute("SELECT id, name FROM prospects")
prospect_ids = {name: id_ for id_, name in cursor.fetchall()}

# Insertion des interactions
interactions_data_fixed = [
    (prospect_ids.get(name), ttype, contenu, date)
    for name, ttype, contenu, date in interactions_data if prospect_ids.get(name)
]
cursor.executemany("""
INSERT INTO interactions (prospect_name, type, contenu, date)
VALUES ((SELECT name FROM prospects WHERE id = ?), ?, ?, ?)
""", interactions_data_fixed)

# Suppression des doublons entreprises (même nom)
unique_companies = {}
for name, industry, address, website in companies_raw:
    if name not in unique_companies:
        unique_companies[name] = (name, industry, address, website)

# Filtrage entreprises déjà présentes
cursor.execute("SELECT name FROM companies")
existing_company_names = {row[0] for row in cursor.fetchall()}

companies_to_insert = [
    data for name, data in unique_companies.items()
    if name not in existing_company_names
]

cursor.executemany("""
INSERT INTO companies (name, industry, address, website)
VALUES (?, ?, ?, ?)
""", companies_to_insert)

# Insertion des deals
deals_data_fixed = [
    (random.choice(list(prospect_ids.values())), title, amount, stage, close_date)
    for _, title, amount, stage, close_date in deals_data
]
cursor.executemany("""
INSERT INTO deals (prospect_id, title, amount, stage, close_date)
VALUES (?, ?, ?, ?, ?)
""", deals_data_fixed)

# Insertion des tâches
tasks_data_fixed = [
    (random.choice(list(prospect_ids.values())), title, due_date, completed)
    for _, title, due_date, completed in tasks_data
]
cursor.executemany("""
INSERT INTO tasks (prospect_id, title, due_date, completed)
VALUES (?, ?, ?, ?)
""", tasks_data_fixed)

# Finalisation
conn.commit()
conn.close()

print("✅ Base CRM enrichie avec succès et 100 clients ajoutés.")
