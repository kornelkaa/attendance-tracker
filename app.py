import os
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from icalendar import Calendar

app = Flask(__name__)
app.config['SECRET_KEY'] = 'YOUR_SECRET_KEY_HERE'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Kérjük, jelentkezzen be az oldal megtekintéséhez.'
login_manager.login_message_category = 'info'

# Modellek
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    theme = db.Column(db.String(20), default='light')
    accent_color = db.Column(db.String(7), default='#4F46E5')
    semester = db.Column(db.String(50), default='2026/27 I.')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    courses = db.relationship('Course', backref='user', lazy=True, cascade="all, delete-orphan")

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    teacher = db.Column(db.String(200))
    max_absences = db.Column(db.Integer, default=3)
    day_of_week = db.Column(db.String(20))
    start_time = db.Column(db.String(5))
    end_time = db.Column(db.String(5))
    room = db.Column(db.String(50))
    color = db.Column(db.String(7), default='#4F46E5')
    course_type = db.Column(db.String(20), default='Előadás')
    credits = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    absences = db.relationship('Absence', backref='course', lazy=True, cascade="all, delete-orphan")
    
    @property
    def absence_count(self):
        return len(self.absences)
        
    @property
    def absence_percentage(self):
        if self.max_absences == 0:
            return 0
        return (self.absence_count / self.max_absences) * 100
        
    @property
    def status_color(self):
        pct = self.absence_percentage
        if pct < 50:
            return 'green'
        elif pct <= 80:
            return 'yellow'
        else:
            return 'red'

class Absence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    reason = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Útvonalak (Routes)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Sikeres bejelentkezés!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Érvénytelen felhasználónév vagy jelszó.', 'danger')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('A felhasználónév már foglalt.', 'danger')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            flash('Az email cím már regisztrálva van.', 'danger')
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Sikeres regisztráció! Most már bejelentkezhet.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sikeresen kijelentkezett.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    courses = Course.query.filter_by(user_id=current_user.id).all()
    
    total_courses = len(courses)
    total_absences = sum(c.absence_count for c in courses)
    courses_in_danger = sum(1 for c in courses if c.absence_percentage > 80)
    courses_ok = sum(1 for c in courses if c.absence_percentage < 50)
    
    return render_template('dashboard.html', 
                           courses=courses, 
                           total_courses=total_courses,
                           total_absences=total_absences,
                           courses_in_danger=courses_in_danger,
                           courses_ok=courses_ok)

@app.route('/course/add', methods=['GET', 'POST'])
@login_required
def add_course():
    if request.method == 'POST':
        name = request.form.get('name')
        teacher = request.form.get('teacher')
        max_absences = request.form.get('max_absences', type=int, default=3)
        day_of_week = request.form.get('day_of_week')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        room = request.form.get('room')
        color = request.form.get('color', '#4F46E5')
        course_type = request.form.get('course_type', 'Előadás')
        credits = request.form.get('credits', type=int, default=0)
        notes = request.form.get('notes')
        
        new_course = Course(
            user_id=current_user.id,
            name=name, teacher=teacher, max_absences=max_absences,
            day_of_week=day_of_week, start_time=start_time, end_time=end_time,
            room=room, color=color, course_type=course_type,
            credits=credits, notes=notes
        )
        db.session.add(new_course)
        db.session.commit()
        
        flash('Tárgy sikeresen hozzáadva!', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('add_course.html')

@app.route('/course/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(id):
    course = Course.query.get_or_404(id)
    if course.user_id != current_user.id:
        flash('Nincs jogosultsága ehhez a tárgyhoz.', 'danger')
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        course.name = request.form.get('name')
        course.teacher = request.form.get('teacher')
        course.max_absences = request.form.get('max_absences', type=int, default=3)
        course.day_of_week = request.form.get('day_of_week')
        course.start_time = request.form.get('start_time')
        course.end_time = request.form.get('end_time')
        course.room = request.form.get('room')
        course.color = request.form.get('color', '#4F46E5')
        course.course_type = request.form.get('course_type', 'Előadás')
        course.credits = request.form.get('credits', type=int, default=0)
        course.notes = request.form.get('notes')
        
        db.session.commit()
        flash('Tárgy sikeresen frissítve!', 'success')
        return redirect(url_for('course_detail', id=course.id))
        
    return render_template('add_course.html', course=course)

@app.route('/course/<int:id>/delete', methods=['POST'])
@login_required
def delete_course(id):
    course = Course.query.get_or_404(id)
    if course.user_id != current_user.id:
        flash('Nincs jogosultsága ehhez a művelethez.', 'danger')
        return redirect(url_for('dashboard'))
        
    db.session.delete(course)
    db.session.commit()
    flash('Tárgy sikeresen törölve.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/course/<int:id>')
@login_required
def course_detail(id):
    course = Course.query.get_or_404(id)
    if course.user_id != current_user.id:
        flash('Nincs jogosultsága ehhez a tárgyhoz.', 'danger')
        return redirect(url_for('dashboard'))
        
    return render_template('course_detail.html', course=course, today=date.today().isoformat())

@app.route('/course/<int:id>/absence/add', methods=['POST'])
@login_required
def add_absence(id):
    course = Course.query.get_or_404(id)
    if course.user_id != current_user.id:
        flash('Nincs jogosultsága ehhez a művelethez.', 'danger')
        return redirect(url_for('dashboard'))
        
    absence_date_str = request.form.get('date')
    reason = request.form.get('reason')
    
    try:
        if absence_date_str:
            absence_date = datetime.strptime(absence_date_str, '%Y-%m-%d').date()
        else:
            absence_date = date.today()
            
        new_absence = Absence(course_id=course.id, date=absence_date, reason=reason)
        db.session.add(new_absence)
        db.session.commit()
        flash('Hiányzás sikeresen rögzítve.', 'success')
    except ValueError:
        flash('Érvénytelen dátum formátum.', 'danger')
        
    return redirect(url_for('course_detail', id=course.id))

@app.route('/absence/<int:id>/delete', methods=['POST'])
@login_required
def delete_absence(id):
    absence = Absence.query.get_or_404(id)
    course = absence.course
    if course.user_id != current_user.id:
        flash('Nincs jogosultsága ehhez a művelethez.', 'danger')
        return redirect(url_for('dashboard'))
        
    db.session.delete(absence)
    db.session.commit()
    flash('Hiányzás sikeresen törölve.', 'success')
    return redirect(url_for('course_detail', id=course.id))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'appearance':
            current_user.theme = 'dark' if request.form.get('theme') == 'dark' else 'light'
            current_user.accent_color = request.form.get('accent_color', '#4F46E5')
            current_user.semester = request.form.get('semester')
            db.session.commit()
            flash('Beállítások sikeresen mentve!', 'success')
            
        elif action == 'password':
            old_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            
            if check_password_hash(current_user.password_hash, old_password):
                current_user.password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
                db.session.commit()
                flash('Jelszó sikeresen megváltoztatva!', 'success')
            else:
                flash('A jelenlegi jelszó helytelen.', 'danger')
                
        return redirect(url_for('settings'))
        
    return render_template('settings.html')

@app.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    user = current_user
    logout_user()
    db.session.delete(user)
    db.session.commit()
    flash('A fiók sikeresen törölve lett.', 'info')
    return redirect(url_for('login'))

# Naptár importálás segédfüggvények
DAY_MAP = {
    0: 'Hétfő',
    1: 'Kedd',
    2: 'Szerda',
    3: 'Csütörtök',
    4: 'Péntek',
    5: 'Szombat',
    6: 'Vasárnap'
}

def parse_ics_events(file_content):
    """ICS fájl feldolgozása és az események kinyerése."""
    cal = Calendar.from_ical(file_content)
    events = []
    seen = set()  # Duplikátumok szűrése név alapján
    
    for component in cal.walk():
        if component.name != 'VEVENT':
            continue
        
        summary = str(component.get('summary', ''))
        if not summary or summary in seen:
            continue
        seen.add(summary)
        
        # Időpont kinyerése
        dtstart = component.get('dtstart')
        dtend = component.get('dtend')
        location = str(component.get('location', '')) if component.get('location') else ''
        description = str(component.get('description', '')) if component.get('description') else ''
        
        start_time = ''
        end_time = ''
        day_of_week = ''
        
        if dtstart:
            dt = dtstart.dt
            if hasattr(dt, 'hour'):
                start_time = dt.strftime('%H:%M')
                day_of_week = DAY_MAP.get(dt.weekday(), '')
            elif hasattr(dt, 'weekday'):
                day_of_week = DAY_MAP.get(dt.weekday(), '')
        
        if dtend:
            dt = dtend.dt
            if hasattr(dt, 'hour'):
                end_time = dt.strftime('%H:%M')
        
        # Oktató keresése a leírásban (heurisztika)
        teacher = ''
        if description:
            lines = description.strip().split('\n')
            for line in lines:
                line = line.strip()
                lower = line.lower()
                if any(k in lower for k in ['oktató', 'tanár', 'teacher', 'instructor', 'előadó']):
                    # "Oktató: Dr. Kiss János" -> "Dr. Kiss János"
                    if ':' in line:
                        teacher = line.split(':', 1)[1].strip()
                    else:
                        teacher = line
                    break
        
        # Kurzus típus felismerés a névből
        course_type = 'Előadás'
        lower_summary = summary.lower()
        if any(k in lower_summary for k in ['gyak', 'practice', 'tutorial']):
            course_type = 'Gyakorlat'
        elif any(k in lower_summary for k in ['szem', 'semin']):
            course_type = 'Szeminárium'
        elif any(k in lower_summary for k in ['labor', 'lab ']):
            course_type = 'Labor'
        
        events.append({
            'name': summary,
            'teacher': teacher,
            'day_of_week': day_of_week,
            'start_time': start_time,
            'end_time': end_time,
            'room': location,
            'course_type': course_type,
            'notes': description[:500] if description else '',
        })
    
    return events

@app.route('/import', methods=['GET', 'POST'])
@login_required
def import_calendar():
    if request.method == 'POST':
        file = request.files.get('ics_file')
        
        if not file or not file.filename:
            flash('Kérlek válassz ki egy fájlt!', 'danger')
            return redirect(url_for('import_calendar'))
        
        if not file.filename.lower().endswith('.ics'):
            flash('Csak .ics kiterjesztésű fájlok támogatottak!', 'danger')
            return redirect(url_for('import_calendar'))
        
        try:
            content = file.read()
            events = parse_ics_events(content)
            
            if not events:
                flash('Nem találtam eseményeket az ICS fájlban.', 'warning')
                return redirect(url_for('import_calendar'))
            
            # Események mentése session-be az előnézet számára
            session['import_events'] = events
            return render_template('import_preview.html', events=events)
            
        except Exception as e:
            flash(f'Hiba az ICS fájl feldolgozásakor: {str(e)}', 'danger')
            return redirect(url_for('import_calendar'))
    
    return render_template('import_calendar.html')

@app.route('/import/confirm', methods=['POST'])
@login_required
def import_confirm():
    events = session.get('import_events', [])
    if not events:
        flash('Nincs importálandó esemény.', 'warning')
        return redirect(url_for('import_calendar'))
    
    # Kiválasztott események indexeinek lekérése
    selected = request.form.getlist('selected_events')
    max_absences = request.form.get('default_max_absences', type=int, default=3)
    
    imported = 0
    for idx_str in selected:
        try:
            idx = int(idx_str)
            if idx < 0 or idx >= len(events):
                continue
            event = events[idx]
            
            # Ellenőrizzük, hogy már létezik-e ilyen nevű kurzus
            existing = Course.query.filter_by(
                user_id=current_user.id, 
                name=event['name']
            ).first()
            if existing:
                continue
            
            new_course = Course(
                user_id=current_user.id,
                name=event['name'],
                teacher=event.get('teacher', ''),
                day_of_week=event.get('day_of_week', ''),
                start_time=event.get('start_time', ''),
                end_time=event.get('end_time', ''),
                room=event.get('room', ''),
                course_type=event.get('course_type', 'Előadás'),
                notes=event.get('notes', ''),
                max_absences=max_absences,
            )
            db.session.add(new_course)
            imported += 1
        except (ValueError, IndexError):
            continue
    
    db.session.commit()
    session.pop('import_events', None)
    
    if imported > 0:
        flash(f'{imported} kurzus sikeresen importálva!', 'success')
    else:
        flash('Nem lett új kurzus importálva (lehet, hogy már léteznek).', 'info')
    
    return redirect(url_for('dashboard'))

@app.route('/api/quick-absence/<int:course_id>', methods=['POST'])
@login_required
def quick_absence(course_id):
    course = Course.query.get_or_404(course_id)
    if course.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    new_absence = Absence(course_id=course.id, date=date.today())
    db.session.add(new_absence)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Hiányzás rögzítve',
        'absence_count': course.absence_count,
        'absence_percentage': course.absence_percentage,
        'status': course.status_color
    })

@app.route('/api/stats', methods=['GET'])
@login_required
def stats():
    courses = Course.query.filter_by(user_id=current_user.id).all()
    total_absences = sum(c.absence_count for c in courses)
    at_risk_courses = sum(1 for c in courses if c.absence_percentage > 80)
    
    return jsonify({
        'total_courses': len(courses),
        'total_absences': total_absences,
        'at_risk_courses': at_risk_courses
    })

if __name__ == '__main__':
    with app.app_context():
        # Létrehozzuk az instance könyvtárat, ha nem létezik
        os.makedirs('instance', exist_ok=True)
        db.create_all()
    app.run(debug=True, port=5000)
