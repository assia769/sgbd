-- Réinitialisation de la base de données
DROP DATABASE IF EXISTS bibliothequ;
CREATE DATABASE bibliothequ;
USE bibliothequ;

-- Suppression des tables dans l'ordre correct (pour éviter les problèmes de clés étrangères)
DROP TABLE IF EXISTS emprunts;
DROP TABLE IF EXISTS exemplaires;
DROP TABLE IF EXISTS periodiques;
DROP TABLE IF EXISTS livres;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS utilisateurs;
DROP TABLE IF EXISTS admine;

-- Création des tables
CREATE TABLE utilisateurs (
    id_utilisateur INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    mot_de_passe VARCHAR(255) NOT NULL,
    telephone VARCHAR(15),
    adresse TEXT,
    categorie ENUM('occasionnel', 'abonne', 'abonne_privilegie') NOT NULL,
    date_inscription DATE DEFAULT (CURRENT_DATE)
) ENGINE=InnoDB;

CREATE TABLE admine (
    id_admin INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    mot_de_passe VARCHAR(255) NOT NULL,
    telephone VARCHAR(15),
    adresse TEXT,
    date_creation DATE DEFAULT (CURRENT_DATE)
) ENGINE=InnoDB;

CREATE TABLE documents (
    reference INT AUTO_INCREMENT PRIMARY KEY,
    titre VARCHAR(255) NOT NULL,
    annee_publication INT,
    editeur VARCHAR(255),
    type_document ENUM('livre', 'periodique') NOT NULL,
    description TEXT,
    langue VARCHAR(50) DEFAULT 'français',
    date_ajout DATE DEFAULT (CURRENT_DATE)
) ENGINE=InnoDB;

CREATE TABLE livres (
    reference INT PRIMARY KEY,
    auteurs VARCHAR(255) NOT NULL,
    ISBN VARCHAR(20) NOT NULL UNIQUE,
    genre VARCHAR(100),
    nombre_pages INT,
    FOREIGN KEY (reference) REFERENCES documents(reference) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE periodiques (
    reference INT PRIMARY KEY,
    volume INT,
    numero INT,
    ISSN VARCHAR(20) NOT NULL UNIQUE,
    periodicite VARCHAR(50),
    FOREIGN KEY (reference) REFERENCES documents(reference) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE exemplaires (
    id_exemplaire INT AUTO_INCREMENT PRIMARY KEY,
    reference_document INT NOT NULL,
    date_achat DATE,
    etat ENUM('neuf', 'très bon état', 'bon état', 'usagé', 'endommagé') DEFAULT 'neuf',
    statut ENUM('en rayon', 'en prêt', 'en retard', 'en réserve', 'en travaux') DEFAULT 'en rayon',
    localisation VARCHAR(50),
    FOREIGN KEY (reference_document) REFERENCES documents(reference)
) ENGINE=InnoDB;

CREATE TABLE emprunts (
    id_emprunt INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT NOT NULL,
    id_exemplaire INT NOT NULL,
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    date_retour DATE,
    statut ENUM('en cours', 'retard', 'rendu') DEFAULT 'en cours',
    commentaire TEXT,
    FOREIGN KEY (id_utilisateur) REFERENCES utilisateurs(id_utilisateur),
    FOREIGN KEY (id_exemplaire) REFERENCES exemplaires(id_exemplaire)
) ENGINE=InnoDB;

-- Insertion des administrateurs
INSERT INTO admine (nom, email, mot_de_passe, telephone, adresse) VALUES
('Admin Principal', 'admin@biblio.fr', 'admin123', '0123456789', '123 Rue Admin');

-- Insertion des utilisateurs
INSERT INTO utilisateurs (nom, email, mot_de_passe, telephone, adresse, categorie) VALUES
('Marie Dupont', 'marie@biblio.fr', 'marie123', '0234567890', '45 Rue des Fleurs', 'abonne'),
('Jean Martin', 'jean@biblio.fr', 'jean123', '0345678901', '78 Avenue République', 'abonne_privilegie'),
('Sarah Bernard', 'sarah@biblio.fr', 'sarah123', '0456789012', '12 Boulevard Arts', 'occasionnel'),
('Pierre Dubois', 'pierre@biblio.fr', 'pierre123', '0567890123', '34 Rue Commerce', 'abonne'),
('Sophie Laurent', 'sophie@biblio.fr', 'sophie123', '0678901234', '56 Avenue Liberté', 'abonne'),
('Lucas Petit', 'lucas@biblio.fr', 'lucas123', '0789012345', '89 Rue Victor Hugo', 'abonne_privilegie'),
('Emma Rousseau', 'emma@biblio.fr', 'emma123', '0890123456', '23 Boulevard Pasteur', 'occasionnel');


select * from utilisateurs;

-- Insertion de documents variés
INSERT INTO documents (titre, annee_publication, editeur, type_document, description, langue) VALUES
('Les Misérables', 1862, 'Albert Lacroix et Cie', 'livre', 'Chef-d''œuvre de Victor Hugo', 'français'),
('Le Petit Prince', 1943, 'Gallimard', 'livre', 'Conte poétique et philosophique', 'français'),
('1984', 1949, 'Secker and Warburg', 'livre', 'Roman dystopique', 'français'),
('Science & Vie', 2023, 'Mondadori', 'periodique', 'Magazine scientifique mensuel', 'français'),
('L''Étranger', 1942, 'Gallimard', 'livre', 'Roman d''Albert Camus', 'français'),
('Madame Bovary', 1857, 'Michel Lévy', 'livre', 'Roman de Gustave Flaubert', 'français'),
('Le Monde', 2023, 'Groupe Le Monde', 'periodique', 'Journal quotidien', 'français'),
('Don Quichotte', 1605, 'Francisco de Robles', 'livre', 'Roman de Cervantes', 'français'),
('Nature', 2023, 'Nature Publishing Group', 'periodique', 'Revue scientifique', 'anglais'),
('Harry Potter à l''école des sorciers', 1997, 'Gallimard Jeunesse', 'livre', 'Roman fantastique', 'français');

-- Insertion des détails des livres
INSERT INTO livres (reference, auteurs, ISBN, genre, nombre_pages) VALUES
(1, 'Victor Hugo', '9780140444308', 'Roman historique', 1488),
(2, 'Antoine de Saint-Exupéry', '9782070612758', 'Conte', 96),
(3, 'George Orwell', '9780451524935', 'Science-fiction', 328),
(5, 'Albert Camus', '9782070360024', 'Roman', 184),
(6, 'Gustave Flaubert', '9782070368051', 'Roman', 528),
(8, 'Miguel de Cervantes', '9782070399528', 'Roman classique', 864),
(10, 'J.K. Rowling', '9782070541270', 'Fantastique', 305);

-- Insertion des périodiques
INSERT INTO periodiques (reference, volume, numero, ISSN, periodicite) VALUES
(4, 304, 1, '0036-8369', 'Mensuel'),
(7, 23760, 1, '0395-2037', 'Quotidien'),
(9, 614, 1, '0028-0836', 'Hebdomadaire');

-- Insertion d'exemplaires multiples pour chaque document
INSERT INTO exemplaires (reference_document, date_achat, etat, statut, localisation) VALUES
(1, '2023-01-15', 'neuf', 'en rayon', 'Section Classiques A1'),
(1, '2023-01-15', 'très bon état', 'en rayon', 'Section Classiques A1'),
(1, '2023-01-15', 'bon état', 'en prêt', 'Section Classiques A1'),
(2, '2023-02-20', 'neuf', 'en prêt', 'Section Jeunesse B2'),
(2, '2023-02-20', 'bon état', 'en rayon', 'Section Jeunesse B2'),
(3, '2023-03-10', 'neuf', 'en rayon', 'Section Science-Fiction C3'),
(3, '2023-03-10', 'très bon état', 'en prêt', 'Section Science-Fiction C3'),
(4, '2023-12-01', 'neuf', 'en rayon', 'Section Périodiques D4'),
(5, '2023-04-15', 'neuf', 'en rayon', 'Section Romans E5'),
(5, '2023-04-15', 'très bon état', 'en prêt', 'Section Romans E5'),
(6, '2023-05-20', 'neuf', 'en rayon', 'Section Classiques A1'),
(7, '2023-12-01', 'neuf', 'en rayon', 'Section Périodiques D4'),
(8, '2023-06-25', 'très bon état', 'en rayon', 'Section Classiques A1'),
(9, '2023-12-01', 'neuf', 'en rayon', 'Section Périodiques D4'),
(10, '2023-07-30', 'neuf', 'en rayon', 'Section Fantastique F6'),
(10, '2023-07-30', 'très bon état', 'en prêt', 'Section Fantastique F6');

-- Insertion d'emprunts variés
INSERT INTO emprunts (id_utilisateur, id_exemplaire, date_debut, date_fin, statut) VALUES
(2, 3, CURRENT_DATE - INTERVAL 10 DAY, CURRENT_DATE + INTERVAL 5 DAY, 'en cours'),
(3, 4, CURRENT_DATE - INTERVAL 15 DAY, CURRENT_DATE - INTERVAL 1 DAY, 'retard'),
(4, 7, CURRENT_DATE - INTERVAL 5 DAY, CURRENT_DATE + INTERVAL 10 DAY, 'en cours'),
(5, 10, CURRENT_DATE - INTERVAL 20 DAY, CURRENT_DATE - INTERVAL 5 DAY, 'rendu'),
(6, 16, CURRENT_DATE - INTERVAL 2 DAY, CURRENT_DATE + INTERVAL 13 DAY, 'en cours');

-- Création des index pour optimiser les recherches
CREATE INDEX idx_documents_titre ON documents(titre);
CREATE INDEX idx_livres_auteurs ON livres(auteurs);
CREATE INDEX idx_emprunts_dates ON emprunts(date_debut, date_fin);
CREATE INDEX idx_exemplaires_statut ON exemplaires(statut);