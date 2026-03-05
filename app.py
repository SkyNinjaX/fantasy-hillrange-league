from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from firebase_config import db, verify_token
from firebase_admin import firestore  
import os
from functools import wraps
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- Firebase Web API Key  --- #
import os
FIREBASE_WEB_API_KEY = os.environ.get('FIREBASE_WEB_API_KEY', 'AIzaSyDQHhEuP2EqEQUPTz62LlFIclhVDAITsHk')

# --- Auth Decorators --- #
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---
@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        r = requests.post(url, json=payload)
        
        if r.status_code == 200:
            user_data = r.json()
            session['user'] = user_data['email']
            session['uid'] = user_data['localId']
            session['token'] = user_data['idToken']
            
            user_doc = db.collection('users').document(user_data['localId']).get()
            session['role'] = user_doc.to_dict().get('role', 'user') if user_doc.exists else 'user'
            
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_WEB_API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        r = requests.post(url, json=payload)
        
        if r.status_code == 200:
            user_data = r.json()
            db.collection('users').document(user_data['localId']).set({
                'email': email,
                'role': 'user',
                'created_at': firestore.SERVER_TIMESTAMP
            })
            flash('Account created! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Registration failed', 'error')
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_team = db.collection('user_teams').document(session['uid']).get()
    all_players = list(db.collection('players').stream())
    leaderboard = list(db.collection('leaderboard')
                       .order_by('total_points', direction='DESCENDING')
                       .limit(10)
                       .stream())
    
    return render_template('dashboard.html', 
                         user_team=user_team, 
                         players=all_players, 
                         leaderboard=leaderboard,
                         user=session['user'],
                         role=session['role'])

@app.route('/team-builder')
@login_required
def team_builder():
    players = list(db.collection('players').stream())
    user_team = db.collection('user_teams').document(session['uid']).get()
    return render_template('team_builder.html', players=players, user_team=user_team, user=session['user'])

@app.route('/save-team', methods=['POST'])
@login_required
def save_team():
    player_ids = request.form.getlist('players')
    
    if len(player_ids) != 11:
        flash('You must select exactly 11 players', 'error')
        return redirect(url_for('team_builder'))
    
    total_cost = 0
    for pid in player_ids:
        player = db.collection('players').document(pid).get()
        total_cost += player.to_dict().get('price', 0)
    
    if total_cost > 100:
        flash(f'Team exceeds budget! £{total_cost}m / £100m', 'error')
        return redirect(url_for('team_builder'))
    
    db.collection('user_teams').document(session['uid']).set({
        'players': player_ids,
        'budget_used': total_cost,
        'budget_remaining': 100 - total_cost,
        'team_name': request.form.get('team_name', 'My Team'),
        'gameweek_points': 0,
        'total_points': 0,
        'created_at': firestore.SERVER_TIMESTAMP
    }, merge=True)
    
    db.collection('leaderboard').document(session['uid']).set({
        'email': session['user'],
        'total_points': 0,
        'gameweek_points': 0,
        'rank': 0
    }, merge=True)
    
    flash('Team saved successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/leaderboard')
@login_required
def leaderboard():
    standings = list(db.collection('leaderboard')
                     .order_by('total_points', direction='DESCENDING')
                     .stream())
    return render_template('leaderboard.html', standings=standings, user=session['user'])

# --- Admin Routes ---
@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    players = list(db.collection('players').stream())
    fixtures = list(db.collection('fixtures').stream())
    return render_template('admin_panel.html', players=players, fixtures=fixtures, user=session['user'])

@app.route('/admin/update-stats', methods=['POST'])
@login_required
@admin_required
def update_player_stats():
    player_id = request.form['player_id']
    goals = int(request.form.get('goals', 0))
    assists = int(request.form.get('assists', 0))
    
    points = (goals * 4) + (assists * 3)
    
    player_ref = db.collection('players').document(player_id)
    player = player_ref.get().to_dict()
    
    new_total = player.get('total_points', 0) + points
    new_goals = player.get('goals', 0) + goals
    new_assists = player.get('assists', 0) + assists
    
    player_ref.update({
        'total_points': new_total,
        'goals': new_goals,
        'assists': new_assists
    })
    
    user_teams = db.collection('user_teams').stream()
    for team in user_teams:
        team_data = team.to_dict()
        if player_id in team_data.get('players', []):
            new_team_points = team_data.get('total_points', 0) + points
            db.collection('user_teams').document(team.id).update({
                'total_points': new_team_points,
                'gameweek_points': firestore.Increment(points)
            })
            
            db.collection('leaderboard').document(team.id).update({
                'total_points': new_team_points,
                'gameweek_points': firestore.Increment(points)
            })
    
    flash(f'Updated {player.get("name")} stats! +{points} points', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)