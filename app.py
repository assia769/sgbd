from flask import Flask,jsonify, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os
import MySQLdb.cursors


app = Flask(__name__)
app.secret_key = os.urandom(24)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'assia2004'
app.config['MYSQL_DB'] = 'bibliothequ'

mysql = MySQL(app)

# Testez la connexion à la base de données
@app.before_request
def test_db_connection():
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT 1')
        print("Connexion à la base de données réussie!")
    except Exception as e:
        print(f"Erreur de connexion à la base de données: {str(e)}")
    finally:
        if 'cur' in locals():
            cur.close()

# Routes
@app.route('/')
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT d.*, l.auteurs, l.ISBN FROM documents d LEFT JOIN livres l ON d.reference = l.reference WHERE d.type_document = 'livre' ")
    books = cur.fetchall()
    cur.close()
    return render_template('home.html', books=books)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        nom = request.form['nom']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        telephone = request.form['telephone']
        adresse = request.form['adresse']
        categorie = 'occasionnel'  # Default category for new users
        
        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO utilisateurs (nom, email, mot_de_passe, telephone, adresse, categorie) VALUES (%s, %s, %s, %s, %s, %s)",
                       (nom, email, password, telephone, adresse, categorie))
            mysql.connection.commit()
            flash('Inscription réussie!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Erreur lors de l\'inscription. Email peut-être déjà utilisé.', 'error')
        finally:
            cur.close()
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        
        # Check user credentials
        cur.execute("SELECT * FROM utilisateurs WHERE email = %s", (email,))
        user = cur.fetchone()
        
        if user and check_password_hash(user[3], password): 
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            return redirect(url_for('user_dashboard'))
        else:
            # Assuming there is only one admin, redirect to admin dashboard
            session['admin_id'] = 1
            session['admin_name'] = 'Admin Principal'
            return redirect(url_for('admin_dashboard'))
        
        flash('Email ou mot de passe incorrect', 'error')
        cur.close()
        
    return render_template('login.html')
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()
    
    # Récupérer les documents avec plus d'informations
    cur.execute("""
        SELECT d.reference, d.titre, d.type_document, d.annee_publication, 
               d.editeur, d.description 
        FROM documents d
    """)
    documents = cur.fetchall()
    
    # Récupérer les utilisateurs avec les informations nécessaires
    cur.execute("""
        SELECT id_utilisateur, nom, categorie 
        FROM utilisateurs
    """)
    utilisateurs = cur.fetchall()
    
    # Récupérer les emprunts en cours avec détails
    cur.execute("""
        SELECT e.id_emprunt, u.nom as nom_utilisateur, d.titre as titre_document,
               e.date_debut, e.date_fin, e.statut
        FROM emprunts e
        JOIN utilisateurs u ON e.id_utilisateur = u.id_utilisateur
        JOIN exemplaires ex ON e.id_exemplaire = ex.id_exemplaire
        JOIN documents d ON ex.reference_document = d.reference
        WHERE e.statut IN ('en cours', 'retard')
    """)
    emprunts = cur.fetchall()
    
    cur.close()
    return render_template('admin_dashboard.html', 
                         documents=documents,
                         utilisateurs=utilisateurs,
                         emprunts=emprunts)

@app.route('/add_document', methods=['POST'])
def add_document():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        titre = request.form['titre']
        annee = request.form['annee']
        editeur = request.form['editeur']
        type_document = request.form['type_document']
        description = request.form['description']
        
        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO documents (titre, annee_publication, editeur, type_document, description) VALUES (%s, %s, %s, %s, %s)",
                       (titre, annee, editeur, type_document, description))
            mysql.connection.commit()
            flash('Document ajouté avec succès!', 'success')
        except Exception as e:
            flash('Erreur lors de l\'ajout du document', 'error')
        finally:
            cur.close()
            
    return redirect(url_for('admin_dashboard'))

@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()
    
    # Get user's borrowed documents
    cur.execute("""
        SELECT d.titre, e.date_debut, e.date_fin, e.statut
        FROM emprunts e
        JOIN exemplaires ex ON e.id_exemplaire = ex.id_exemplaire
        JOIN documents d ON ex.reference_document = d.reference
        WHERE e.id_utilisateur = %s
    """, (session['user_id'],))
    
    emprunts = cur.fetchall()
    cur.close()
    
    return render_template('user_dashboard.html', emprunts=emprunts)

@app.route('/search')
def search():
    query = request.args.get('query', '')
    cur = mysql.connection.cursor()
    
    cur.execute("""
        SELECT d.*, l.auteurs, l.ISBN 
        FROM documents d 
        LEFT JOIN livres l ON d.reference = l.reference 
        WHERE d.titre LIKE %s OR l.auteurs LIKE %s
    """, (f'%{query}%', f'%{query}%'))
    
    results = cur.fetchall()
    cur.close()
    
    return render_template('search_results.html', results=results)

@app.route('/request_borrow/<int:document_id>', methods=['POST'])
def request_borrow(document_id):
    # Vérification de la connexion utilisateur
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Veuillez vous connecter'}), 401
    
    try:
        cur = mysql.connection.cursor()
        
        # 1. Vérification de la catégorie de l'utilisateur et du nombre d'emprunts en cours
        cur.execute("""
            SELECT categorie, 
                   (SELECT COUNT(*) FROM emprunts 
                    WHERE id_utilisateur = utilisateurs.id_utilisateur 
                    AND statut = 'en cours') as nb_emprunts
            FROM utilisateurs 
            WHERE id_utilisateur = %s
        """, (session['user_id'],))
        
        user_info = cur.fetchone()
        if not user_info:
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404
            
        # Vérification des limites d'emprunt selon la catégorie
        limite_emprunts = {
            'occasionnel': 3,
            'abonne': 5,
            'abonne_privilegie': 8
        }
        
        if user_info[1] >= limite_emprunts[user_info[0]]:
            return jsonify({
                'success': False, 
                'message': f'Limite d\'emprunts atteinte pour votre catégorie ({user_info[0]})'
            }), 400
        
        # 2. Vérification de la disponibilité d'un exemplaire
        cur.execute("""
            SELECT id_exemplaire 
            FROM exemplaires 
            WHERE reference_document = %s AND statut = 'en rayon' 
            LIMIT 1
        """, (document_id,))
        
        exemplaire = cur.fetchone()
        if not exemplaire:
            return jsonify({
                'success': False, 
                'message': 'Aucun exemplaire disponible pour ce document'
            }), 400
            
        # 3. Création de l'emprunt
        # Date de fin selon la catégorie
        duree_pret = {
            'occasionnel': 14,  # 2 semaines
            'abonne': 21,       # 3 semaines
            'abonne_privilegie': 28  # 4 semaines
        }
        
        cur.execute("""
            INSERT INTO emprunts 
                (id_utilisateur, id_exemplaire, date_debut, date_fin, statut) 
            VALUES 
                (%s, %s, CURRENT_DATE, DATE_ADD(CURRENT_DATE, INTERVAL %s DAY), 'en cours')
        """, (session['user_id'], exemplaire[0], duree_pret[user_info[0]]))
        
        # 4. Mise à jour du statut de l'exemplaire
        cur.execute("""
            UPDATE exemplaires 
            SET statut = 'en prêt' 
            WHERE id_exemplaire = %s
        """, (exemplaire[0],))
            
        mysql.connection.commit()
        cur.close()
        
        return jsonify({
            'success': True, 
            'message': f'Emprunt effectué avec succès. Retour prévu dans {duree_pret[user_info[0]]} jours.'
        })
        
    except Exception as e:
        mysql.connection.rollback()
        print(f"Erreur lors de l'emprunt: {str(e)}")  # Pour le debugging
        return jsonify({
            'success': False, 
            'message': 'Une erreur est survenue lors de l\'emprunt'
        }), 500
@app.route('/api/exemplaires-disponibles/<int:document_id>')
def get_exemplaires_disponibles(document_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id_exemplaire, etat 
        FROM exemplaires 
        WHERE reference_document = %s AND statut = 'en rayon'
    """, (document_id,))
    exemplaires = [{'id_exemplaire': e[0], 'etat': e[1]} for e in cur.fetchall()]
    cur.close()
    return jsonify({'exemplaires': exemplaires})

@app.route('/api/creer-emprunt', methods=['POST'])
def creer_emprunt():
    data = request.json
    try:
        cur = mysql.connection.cursor()
        
        # Vérifier si l'exemplaire est toujours disponible
        cur.execute("""
            SELECT statut FROM exemplaires 
            WHERE id_exemplaire = %s
        """, (data['id_exemplaire'],))
        if cur.fetchone()[0] != 'en rayon':
            return jsonify({
                'success': False,
                'message': 'Cet exemplaire n\'est plus disponible'
            })

        # Créer l'emprunt
        cur.execute("""
            INSERT INTO emprunts (id_utilisateur, id_exemplaire, date_debut, date_fin, statut)
            VALUES (%s, %s, CURRENT_DATE, DATE_ADD(CURRENT_DATE, INTERVAL 14 DAY), 'en cours')
        """, (data['id_utilisateur'], data['id_exemplaire']))
        
        # Mettre à jour le statut de l'exemplaire
        cur.execute("""
            UPDATE exemplaires SET statut = 'en prêt'
            WHERE id_exemplaire = %s
        """, (data['id_exemplaire'],))
        
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Erreur: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la création de l\'emprunt'
        })

@app.route('/api/marquer-rendu/<int:id_emprunt>', methods=['POST'])
def marquer_rendu(id_emprunt):
    try:
        cur = mysql.connection.cursor()
        
        # Mettre à jour l'emprunt
        cur.execute("""
            UPDATE emprunts 
            SET statut = 'rendu', date_retour = CURRENT_DATE
            WHERE id_emprunt = %s
        """, (id_emprunt,))
        
        # Récupérer l'id de l'exemplaire
        cur.execute("""
            SELECT id_exemplaire FROM emprunts
            WHERE id_emprunt = %s
        """, (id_emprunt,))
        id_exemplaire = cur.fetchone()[0]
        
        # Mettre à jour le statut de l'exemplaire
        cur.execute("""
            UPDATE exemplaires 
            SET statut = 'en rayon'
            WHERE id_exemplaire = %s
        """, (id_exemplaire,))
        
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Erreur: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erreur lors du retour'
        })
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
