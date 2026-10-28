from flask import Flask, render_template, jsonify, request, session
from pathlib import Path
import sqlite3, uuid, os

app = Flask(__name__)
app.secret_key = os.environ.get('ORANGO_SECRET_KEY', 'orango-local-demo-change-me')
DB_PATH = Path(__file__).resolve().with_name('orango_game.db')
ACHIEVEMENTS = [
 {'key':'first_game','name':'Primeira aventura','icon':'🎮','description':'Inicie sua primeira partida.','points':20,'field':'games','target':1},
 {'key':'safe_10','name':'Passos seguros','icon':'🧭','description':'Revele 10 casas seguras.','points':30,'field':'safe_tiles','target':10},
 {'key':'first_reward','name':'Caçador de tesouros','icon':'🪙','description':'Encontre sua primeira recompensa.','points':40,'field':'rewards','target':1},
 {'key':'three_rewards','name':'Colecionador','icon':'🎁','description':'Encontre 3 recompensas no total.','points':60,'field':'rewards','target':3},
 {'key':'first_win','name':'Primeira vitória','icon':'🏆','description':'Vença uma partida.','points':100,'field':'wins','target':1},
 {'key':'five_games','name':'Explorador','icon':'🔥','description':'Jogue 5 partidas.','points':75,'field':'games','target':5},
 {'key':'master_500','name':'Mestre Orango','icon':'👑','description':'Acumule 500 pontos em partidas.','points':150,'field':'earned_points','target':500},
]

def connect():
    db = sqlite3.connect(DB_PATH, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    return db

def init_db():
    with connect() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS players(
          id TEXT PRIMARY KEY, nickname TEXT NOT NULL DEFAULT 'Visitante',
          points INTEGER NOT NULL DEFAULT 0, earned_points INTEGER NOT NULL DEFAULT 0,
          games INTEGER NOT NULL DEFAULT 0, wins INTEGER NOT NULL DEFAULT 0,
          rewards INTEGER NOT NULL DEFAULT 0, safe_tiles INTEGER NOT NULL DEFAULT 0,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS game_history(
          id INTEGER PRIMARY KEY AUTOINCREMENT, player_id TEXT NOT NULL, event TEXT NOT NULL,
          points INTEGER NOT NULL DEFAULT 0, details TEXT, difficulty TEXT,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(player_id) REFERENCES players(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS achievements(
          key TEXT PRIMARY KEY, name TEXT NOT NULL, icon TEXT NOT NULL, description TEXT NOT NULL,
          points INTEGER NOT NULL, target INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS player_achievements(
          player_id TEXT NOT NULL, achievement_key TEXT NOT NULL, unlocked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          PRIMARY KEY(player_id,achievement_key), FOREIGN KEY(player_id) REFERENCES players(id) ON DELETE CASCADE,
          FOREIGN KEY(achievement_key) REFERENCES achievements(key));
        CREATE INDEX IF NOT EXISTS idx_players_rank ON players(points DESC, wins DESC, games DESC);
        CREATE INDEX IF NOT EXISTS idx_history_player ON game_history(player_id);
        ''')
        for a in ACHIEVEMENTS:
            c.execute('INSERT OR IGNORE INTO achievements VALUES(?,?,?,?,?,?)', (a['key'],a['name'],a['icon'],a['description'],a['points'],a['target']))

def current_player_id():
    if not session.get('player_id'): session['player_id'] = str(uuid.uuid4())
    pid = session['player_id']
    with connect() as c:
        c.execute("INSERT OR IGNORE INTO players(id,nickname) VALUES(?, 'Visitante')", (pid,))
    return pid

def pdata(c, pid):
    row = c.execute('SELECT * FROM players WHERE id=?', (pid,)).fetchone()
    return dict(row) if row else {}

def unlocked_count(c, pid):
    return c.execute('SELECT COUNT(*) FROM player_achievements WHERE player_id=?',(pid,)).fetchone()[0]

def check_achievements(c, pid, stats):
    new = []
    for a in ACHIEVEMENTS:
        if stats.get(a['field'], 0) >= a['target']:
            cur = c.execute('INSERT OR IGNORE INTO player_achievements(player_id,achievement_key) VALUES(?,?)',(pid,a['key']))
            if cur.rowcount:
                c.execute('UPDATE players SET points=points+? WHERE id=?',(a['points'],pid))
                c.execute('INSERT INTO game_history(player_id,event,points,details) VALUES(?,?,?,?)',(pid,'achievement',a['points'],a['name']))
                new.append({k:a[k] for k in ('key','name','icon','description','points')})
    return new

@app.get('/')
def index():
    current_player_id()
    return render_template('index.html')

@app.get('/api/profile')
def profile():
    pid=current_player_id()
    with connect() as c:
        p=pdata(c,pid); p['achievements_count']=unlocked_count(c,pid)
        p['safe_tiles']=p.get('safe_tiles',0)
        return jsonify(p)

@app.post('/api/player')
def update_player():
    pid=current_player_id(); body=request.get_json(silent=True) or {}
    nickname=' '.join(str(body.get('nickname','')).split())
    if not nickname or len(nickname)>24:
        return jsonify(error='Informe um apelido de 1 a 24 caracteres.'),400
    with connect() as c:
        c.execute('UPDATE players SET nickname=?,updated_at=CURRENT_TIMESTAMP WHERE id=?',(nickname,pid))
        return jsonify(pdata(c,pid))

@app.get('/api/achievements')
def achievements():
    pid=current_player_id()
    with connect() as c:
        got={a['key']:a for a in c.execute('SELECT a.key,a.name,a.icon,a.description,a.points,pa.unlocked_at FROM player_achievements pa JOIN achievements a ON a.key=pa.achievement_key WHERE pa.player_id=?',(pid,))}
        result=[]
        for r in c.execute('SELECT * FROM achievements ORDER BY points').fetchall():
            a=dict(r); a['unlocked']=a['key'] in got; a['unlocked_at']=got.get(a['key'],{}).get('unlocked_at'); result.append(a)
        return jsonify(result)

@app.get('/api/leaderboard')
def leaderboard():
    with connect() as c:
        rows=c.execute('''SELECT p.id,p.nickname,p.points,p.games,p.wins,
          COUNT(DISTINCT pa.achievement_key) achievements, p.created_at
          FROM players p LEFT JOIN player_achievements pa ON pa.player_id=p.id
          WHERE p.nickname != 'Visitante' GROUP BY p.id
          ORDER BY p.points DESC,p.wins DESC,p.games DESC,p.created_at ASC LIMIT 100''').fetchall()
        return jsonify([dict(r) for r in rows])

@app.delete('/api/players/<player_id>')
def delete_player(player_id):
    # Proteção básica para uso local: exige origem local quando o navegador envia Origin.
    origin=request.headers.get('Origin')
    if origin and not (origin.startswith('http://127.0.0.1:5000') or origin.startswith('http://localhost:5000')):
        return jsonify(error='Origem não permitida.'),403
    with connect() as c:
        cur=c.execute('DELETE FROM players WHERE id=?',(player_id,))
        if not cur.rowcount: return jsonify(error='Jogador não encontrado.'),404
        if session.get('player_id') == player_id: session.pop('player_id',None)
        return jsonify(message='Jogador e dados associados excluídos com sucesso.')

@app.get('/api/summary')
def summary():
    pid=current_player_id()
    with connect() as c:
        p=pdata(c,pid)
        p['achievements_count']=unlocked_count(c,pid)
        p['top_players']=[dict(r) for r in c.execute("SELECT nickname,points,wins,games FROM players WHERE nickname!='Visitante' ORDER BY points DESC,wins DESC,games DESC,created_at ASC LIMIT 3")]
        return jsonify(p)

@app.post('/api/event')
def event():
    pid=current_player_id(); body=request.get_json(silent=True) or {}; ev=str(body.get('event',''))[:40]
    allowed={'game_start','safe_tile','reward','win','mine_hit'}
    if ev not in allowed: return jsonify(error='Evento inválido.'),400
    # Pontuação por evento é definida no servidor, não pelo valor arbitrário enviado pelo navegador.
    points={'game_start':0,'safe_tile':10,'reward':{'Moeda Orango':40,'Selo Explorador':60,'Item surpresa':80,'Desconto de 20% em um curso':100,'Coroa Mestre':150},'win':50,'mine_hit':0}
    details=' '.join(str(body.get('details','')).split())[:120]
    amount=points[ev] if isinstance(points[ev],int) else points[ev].get(details,0)
    difficulty=str(body.get('difficulty','easy'))
    if difficulty not in {'easy','medium','hard'}: difficulty='easy'
    with connect() as c:
        # Evita que visitas sem apelido apareçam no placar.
        c.execute('UPDATE players SET points=points+?,earned_points=earned_points+?,updated_at=CURRENT_TIMESTAMP WHERE id=?',(amount,amount,pid))
        col={'game_start':'games','safe_tile':'safe_tiles','reward':'rewards','win':'wins'}.get(ev)
        if col: c.execute(f'UPDATE players SET {col}={col}+1 WHERE id=?',(pid,))
        c.execute('INSERT INTO game_history(player_id,event,points,details,difficulty) VALUES(?,?,?,?,?)',(pid,ev,amount,details,difficulty))
        new=check_achievements(c,pid,pdata(c,pid)); p=pdata(c,pid); p['new_achievements']=new; p['achievements_count']=unlocked_count(c,pid)
        return jsonify(p)

@app.get('/api/history')
def history():
    pid=current_player_id()
    with connect() as c: return jsonify([dict(r) for r in c.execute('SELECT event,points,details,created_at FROM game_history WHERE player_id=? ORDER BY id DESC LIMIT 30',(pid,)).fetchall()])

init_db()
if __name__=='__main__': app.run(host='127.0.0.1', port=5001, debug=False)
