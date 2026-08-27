from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
import sqlite3, os, json, secrets, string
from datetime import datetime

app=Flask(__name__)
app.secret_key=os.getenv('SECRET_KEY','CAMBIAR-ESTA-CLAVE-ANTES-DE-PRODUCCION')
ADMIN_PASSWORD=os.getenv('ADMIN_PASSWORD','cambiar-por-clave-segura')
DB='serums360.db'
with open('ranking.json',encoding='utf8') as f: RANKINGS=json.load(f)

def db():
    con=sqlite3.connect(DB); con.row_factory=sqlite3.Row; return con

def init_db():
    con=db(); con.execute('''CREATE TABLE IF NOT EXISTS codes(
        code TEXT PRIMARY KEY, max_uses INTEGER NOT NULL, uses INTEGER NOT NULL DEFAULT 0,
        active INTEGER NOT NULL DEFAULT 1, created_at TEXT, expires_at TEXT)'''); con.commit(); con.close()

def admin_required(): return session.get('admin') is True

def position_for(career, score):
    rows=RANKINGS[career]
    # position = after all rows strictly above the score + 1; ties take first tied position
    for row in rows:
        if score >= row['note']:
            return row['position'], row['note']
    return len(rows)+1, rows[-1]['note'] if rows else None

def validate_code(code):
    con=db(); row=con.execute('SELECT * FROM codes WHERE code=?',(code.strip().upper(),)).fetchone(); con.close()
    if not row or not row['active'] or row['uses']>=row['max_uses']: return None
    if row['expires_at'] and datetime.fromisoformat(row['expires_at'])<datetime.now(): return None
    return row

@app.route('/',methods=['GET','POST'])
def index():
    result=None
    if request.method=='POST':
        code=request.form.get('code','').upper().strip()
        if not validate_code(code):
            flash('Código inválido, vencido o sin consultas disponibles.','error'); return redirect(url_for('index'))
        try:
            career=request.form['career']; ppp=float(request.form['ppp']); nes=float(request.form['nes'])
            if career not in RANKINGS: raise ValueError
            score=ppp*.3+nes*.7
            position,ref=position_for(career,score)
            con=db(); con.execute('UPDATE codes SET uses=uses+1 WHERE code=?',(code,)); con.commit(); con.close()
            result={'career':career,'ppp':ppp,'nes':nes,'score':round(score,5),'position':position,'total':len(RANKINGS[career]),'reference':ref}
        except Exception:
            flash('Revisa la carrera y los valores ingresados.','error'); return redirect(url_for('index'))
    return render_template('index.html',careers=sorted(RANKINGS),result=result)

@app.route('/admin/login',methods=['GET','POST'])
def admin_login():
    if request.method=='POST':
        if request.form.get('password')==ADMIN_PASSWORD:
            session['admin']=True; return redirect(url_for('admin'))
        flash('Contraseña incorrecta.','error')
    return render_template('login.html')

@app.route('/admin')
def admin():
    if not admin_required(): return redirect(url_for('admin_login'))
    con=db(); codes=con.execute('SELECT * FROM codes ORDER BY created_at DESC').fetchall(); con.close()
    return render_template('admin.html',codes=codes,careers=len(RANKINGS),records=sum(map(len,RANKINGS.values())))

@app.route('/admin/create',methods=['POST'])
def create_code():
    if not admin_required(): return redirect(url_for('admin_login'))
    prefix=request.form.get('prefix','SR360').upper().replace(' ','')
    max_uses=max(1,int(request.form.get('max_uses',1)))
    expires=request.form.get('expires') or None
    alphabet=string.ascii_uppercase+string.digits
    code=f'{prefix}-'+''.join(secrets.choice(alphabet) for _ in range(8))
    con=db(); con.execute('INSERT INTO codes(code,max_uses,created_at,expires_at) VALUES(?,?,?,?)',(code,max_uses,datetime.now().isoformat(timespec='seconds'),expires)); con.commit(); con.close()
    flash(f'Código generado: {code}','success'); return redirect(url_for('admin'))

@app.route('/admin/toggle/<code>',methods=['POST'])
def toggle(code):
    if not admin_required(): return redirect(url_for('admin_login'))
    con=db(); con.execute('UPDATE codes SET active=CASE active WHEN 1 THEN 0 ELSE 1 END WHERE code=?',(code,)); con.commit(); con.close(); return redirect(url_for('admin'))

@app.route('/admin/logout')
def logout(): session.clear(); return redirect(url_for('index'))

if __name__=='__main__':
    init_db(); app.run(debug=True)
