#!/usr/bin/env python3
"""ORBIPERA: runnable educational SaaS prototype with real SQLite persistence.
No external Python packages required. All people and company data are fictional.
"""
from __future__ import annotations
import json, os, sqlite3, hashlib, secrets, hmac, re, mimetypes, time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote
from http.cookies import SimpleCookie

BASE=Path(__file__).resolve().parent
DB=Path(os.getenv('ORBIPERA_DB', str(BASE/'orbipera.sqlite3')))
HOST=os.getenv('ORBIPERA_HOST','127.0.0.1')
PORT=int(os.getenv('ORBIPERA_PORT',os.getenv('PORT','8765')))
COURSES=[
 ('c1','Komunikasi Efektif di Tempat Kerja','Komunikasi','4 jam','Latihan komunikasi profesional, mendengarkan aktif, dan menyampaikan ide.','Dasar'),
 ('c2','Kolaborasi & Kerja Sama Tim','Kerja Sama','3 jam','Bangun koordinasi, kepercayaan, dan tanggung jawab kerja lintas fungsi.','Dasar'),
 ('c3','Pemecahan Masalah Praktis','Problem Solving','5 jam','Pelajari analisis akar masalah dan solusi praktis berbasis data.','Menengah'),
 ('c4','Peningkatan Kompetensi Teknis','Kompetensi Teknis','6 jam','Terapkan SOP, keterampilan teknis, dan evaluasi kualitas.','Menengah'),
 ('c5','Dasar-Dasar Kepemimpinan','Kepemimpinan','4 jam','Mengembangkan arahan, coaching, feedback, dan delegasi.','Dasar'),
]
STANDARD={'Komunikasi':4.3,'Kerja Sama':4.2,'Problem Solving':4.1,'Kompetensi Teknis':4.5,'Kepemimpinan':4.0}
DEPTS=['Operasional','Teknologi','Human Capital','Pemasaran','Keuangan','Layanan Pelanggan','Penjualan','Strategi']
ROLES=['Staff Operasional','Data Analyst','HR Officer','Marketing Specialist','Finance Officer','Customer Success','Sales Executive','Business Analyst']
QUESTIONS={
 'c1':[
  ('Apa ciri utama komunikasi dua arah yang efektif?',['Mendominasi pembicaraan','Mendengarkan dan mengonfirmasi pemahaman','Mengirim pesan sebanyak mungkin','Menghindari pertanyaan'],1,'Komunikasi efektif menggabungkan penyampaian pesan dan konfirmasi pemahaman.'),
  ('Saat menerima kritik dari rekan kerja, langkah terbaik adalah…',['Langsung membantah','Mengabaikan pesan','Meminta contoh konkret dan mendengarkan','Membicarakannya di grup umum'],2,'Umpan balik lebih berguna ketika dipahami secara spesifik.'),
  ('Agar instruksi kerja tidak disalahpahami, sebaiknya…',['Memberi instruksi singkat tanpa konteks','Menetapkan tujuan, tenggat, dan konfirmasi','Menghindari catatan tertulis','Menyampaikan sekali saja'],1,'Tujuan, tenggat, dan konfirmasi mengurangi miskomunikasi.'),
  ('Dalam presentasi kerja, gunakan bahasa yang…',['Rumit agar terlihat ahli','Jelas dan sesuai audiens','Penuh singkatan tanpa penjelasan','Sangat panjang'],1,'Pesan yang mudah dipahami mendukung tindakan.'),
  ('Apa yang dimaksud active listening?',['Menunggu giliran bicara','Mendengarkan penuh perhatian dan mengklarifikasi','Mengulang semua ucapan tanpa memahami','Mengalihkan topik'],1,'Active listening berarti memahami dan menanggapi dengan tepat.')],
 'c2':[
  ('Tujuan pembagian peran dalam tim adalah…',['Membatasi kontribusi anggota','Memperjelas tanggung jawab dan koordinasi','Menghindari komunikasi','Menambah rapat'],1,'Peran yang jelas membuat kolaborasi lebih efisien.'),
  ('Saat anggota tim mengalami hambatan, tindakan terbaik adalah…',['Menyalahkan rekan','Membiarkan sampai selesai','Membantu mencari solusi dan menyepakati tindak lanjut','Mengambil seluruh pekerjaannya'],2,'Dukungan dan tindak lanjut menjaga target bersama.'),
  ('Bagaimana menyelesaikan perbedaan pendapat?',['Gunakan data dan tujuan bersama','Memilih pendapat paling keras','Menghindari semua konflik','Membagikan kritik di media sosial'],0,'Data dan tujuan bersama membantu mencapai keputusan.'),
  ('Apa fungsi feedback dalam kolaborasi?',['Menilai pribadi rekan','Meningkatkan kinerja dan proses kerja','Mencari kesalahan','Menghentikan diskusi'],1,'Umpan balik yang konstruktif berorientasi pada perbaikan.'),
  ('Kolaborasi lintas divisi membutuhkan…',['Komunikasi dan kesepakatan target','Semua bekerja sendiri','Satu divisi mengambil seluruh keputusan','Minim dokumentasi'],0,'Koordinasi lintas fungsi bergantung pada kesepakatan bersama.')],
 'c3':[
  ('Langkah pertama problem solving yang tepat adalah…',['Langsung membeli alat','Merumuskan masalah secara spesifik','Menyalahkan orang','Membuat laporan akhir'],1,'Definisi masalah menentukan ketepatan solusi.'),
  ('Metode 5 Why digunakan untuk…',['Menentukan gaji','Menelusuri akar penyebab','Mengukur kepuasan','Membuat jadwal'],1,'5 Why menanyakan penyebab berulang kali secara terstruktur.'),
  ('Sebelum memilih solusi, lakukan…',['Perbandingan dampak, biaya, dan risiko','Voting tanpa informasi','Mengabaikan data','Memilih solusi tercepat selalu'],0,'Solusi dipilih dengan memperhatikan manfaat dan konsekuensi.'),
  ('Setelah solusi diterapkan, lakukan…',['Hentikan pemantauan','Evaluasi hasil berdasarkan indikator','Lupakan masalah','Ubah tujuan tanpa alasan'],1,'Evaluasi menunjukkan apakah solusi berhasil.'),
  ('Apa itu hipotesis kerja?',['Asumsi yang perlu diuji','Kesimpulan final','Perintah tetap','Opini tanpa bukti'],0,'Hipotesis perlu dikonfirmasi dengan fakta.')],
 'c4':[
  ('SOP dalam pekerjaan berfungsi untuk…',['Menghambat inovasi','Menstandarkan langkah dan kualitas kerja','Menghilangkan pelatihan','Menambah dokumen tanpa tujuan'],1,'SOP membantu konsistensi dan mutu kerja.'),
  ('Jika SOP tidak sesuai situasi lapangan, sebaiknya…',['Mengabaikannya diam-diam','Laporkan dan usulkan perbaikan ke pihak berwenang','Menghapus dokumen','Meminta semua rekan melanggar'],1,'Perubahan SOP sebaiknya melalui evaluasi dan persetujuan.'),
  ('Apa fungsi checklist kualitas?',['Memastikan langkah penting tidak terlewat','Menggantikan seluruh keahlian','Menambah lembur','Membatasi komunikasi'],0,'Checklist mendukung kepatuhan pada standar.'),
  ('Dokumentasi kesalahan teknis bermanfaat untuk…',['Mencari orang untuk disalahkan','Pembelajaran dan pencegahan kesalahan berulang','Menghapus jejak','Menghambat diskusi'],1,'Catatan yang baik menjadi dasar perbaikan proses.'),
  ('Kompetensi teknis perlu dinilai ulang setelah pelatihan untuk…',['Mengonfirmasi dampak pengembangan','Menambah biaya','Mengurangi informasi','Mengganti jabatan otomatis'],0,'Asesmen ulang melihat perubahan kemampuan secara terukur.')],
 'c5':[
  ('Pemimpin yang efektif sebaiknya…',['Memberi arahan jelas dan mendengarkan tim','Mengambil semua keputusan tanpa masukan','Mengabaikan kendala anggota','Hanya fokus target pribadi'],0,'Kejelasan arah dan mendengarkan tim sama-sama penting.'),
  ('Feedback konstruktif berfokus pada…',['Perilaku dan perbaikan spesifik','Kepribadian negatif','Kesalahan masa lalu saja','Perbandingan antarkaryawan'],0,'Gunakan observasi, dampak, dan langkah perbaikan.'),
  ('Delegasi efektif berarti…',['Melepas tanggung jawab total','Menentukan hasil, kewenangan, dan pemantauan','Memberi tugas tanpa informasi','Menghindari evaluasi'],1,'Delegasi memerlukan ekspektasi dan dukungan.'),
  ('Coaching bertujuan untuk…',['Membantu anggota menemukan solusi dan berkembang','Memberi hukuman','Menghindari pertanyaan','Menambah kontrol tanpa dialog'],0,'Coaching mendukung pengembangan kemampuan.'),
  ('Saat target tim meleset, pemimpin sebaiknya…',['Mengevaluasi hambatan bersama tim','Menyalahkan satu orang','Menyembunyikan data','Mengabaikan target'],0,'Evaluasi terbuka membantu perbaikan berikutnya.')],
}


def conn():
 c=sqlite3.connect(DB,timeout=20,check_same_thread=False)
 c.row_factory=sqlite3.Row
 c.execute('PRAGMA journal_mode=WAL')
 c.execute('PRAGMA foreign_keys=ON')
 return c

def pw_hash(value, salt=None):
 salt=salt or secrets.token_bytes(16)
 key=hashlib.pbkdf2_hmac('sha256',value.encode(),salt,220000)
 return salt.hex()+':'+key.hex()

def pw_check(raw, encoded):
 try:
  salt,key=encoded.split(':')
  return hmac.compare_digest(pw_hash(raw,bytes.fromhex(salt)).split(':')[1],key)
 except: return False

def init_db():
 DB.parent.mkdir(parents=True, exist_ok=True)
 with conn() as c:
  c.executescript('''
  CREATE TABLE IF NOT EXISTS company(id INTEGER PRIMARY KEY, name TEXT NOT NULL, industry TEXT, address TEXT, description TEXT, plan TEXT NOT NULL DEFAULT 'Enterprise');
  CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT NOT NULL,email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('hr','employee')),position TEXT,department TEXT);
  CREATE TABLE IF NOT EXISTS scores(user_id INTEGER,competency TEXT,score REAL NOT NULL CHECK(score>=1 AND score<=5),updated_at TEXT DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY(user_id,competency),FOREIGN KEY(user_id) REFERENCES users(id));
  CREATE TABLE IF NOT EXISTS courses(id TEXT PRIMARY KEY,title TEXT NOT NULL,competency TEXT NOT NULL,duration TEXT,description TEXT,level TEXT);
  CREATE TABLE IF NOT EXISTS progress(user_id INTEGER,course_id TEXT,percent INTEGER NOT NULL DEFAULT 0 CHECK(percent BETWEEN 0 AND 100),updated_at TEXT DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY(user_id,course_id),FOREIGN KEY(user_id) REFERENCES users(id),FOREIGN KEY(course_id) REFERENCES courses(id));
  CREATE TABLE IF NOT EXISTS questions(id INTEGER PRIMARY KEY AUTOINCREMENT,course_id TEXT,prompt TEXT,choices TEXT,correct INTEGER,reason TEXT,FOREIGN KEY(course_id) REFERENCES courses(id));
  CREATE TABLE IF NOT EXISTS quiz_attempts(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,course_id TEXT,percent INTEGER,answers TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(user_id) REFERENCES users(id));
  CREATE TABLE IF NOT EXISTS tickets(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,subject TEXT NOT NULL,description TEXT,status TEXT DEFAULT 'Baru',reply TEXT DEFAULT '',created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(user_id) REFERENCES users(id));
  CREATE TABLE IF NOT EXISTS feedback(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,course_id TEXT,rating INTEGER,comment TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
  CREATE TABLE IF NOT EXISTS learning_events(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,course_id TEXT,kind TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(user_id) REFERENCES users(id));
  CREATE TABLE IF NOT EXISTS sessions(token_hash TEXT PRIMARY KEY,user_id INTEGER,expires INTEGER,FOREIGN KEY(user_id) REFERENCES users(id));
  ''')
  if c.execute('SELECT COUNT(*) FROM users').fetchone()[0]:return
  c.execute('INSERT INTO company(id,name,industry,address,description,plan) VALUES(1,?,?,?,?,?)',('PT Maju Bersama (Data Fiktif)','Teknologi & Jasa','Jakarta, Indonesia (contoh)','Perusahaan contoh untuk pengujian platform pengembangan kompetensi ORBIPERA.','Enterprise'))
  c.execute('INSERT INTO users VALUES(?,?,?,?,?,?,?)',(1,'Admin HR','admin@orbipera.demo',pw_hash('Admin123!'),'hr','HR Administrator','Human Capital'))
  familiar=[('Andi Rahman','Customer Service','Layanan Pelanggan','andi.rahman@orbipera.demo'),('Dewi Prameswari','Learning Specialist','Human Capital','dewi.prameswari@orbipera.demo'),('Rizky Saputra','Software Engineer','Teknologi','rizky.saputra@orbipera.demo'),('Sinta Lestari','Sales Executive','Penjualan','sinta.lestari@orbipera.demo'),('Budi Santoso','Customer Service','Layanan Pelanggan','budi.santoso@orbipera.demo')]
  for course in COURSES: c.execute('INSERT INTO courses VALUES(?,?,?,?,?,?)',course)
  # 360 fictional employees; ID 2 is Andi
  for j in range(360):
   name,pos,dept,email=familiar[j] if j<len(familiar) else (f'Karyawan {j+1:03d}',ROLES[j%len(ROLES)],DEPTS[j%len(DEPTS)],f'karyawan{j+1:03d}@orbipera.demo')
   uid=j+2
   c.execute('INSERT INTO users VALUES(?,?,?,?,?,?,?)',(uid,name,email,pw_hash('Karyawan123!'),'employee',pos,dept))
   for k,comp in enumerate(STANDARD):
    score=round(2.5+(((j*17+k*11)%23)/20),1)
    c.execute('INSERT INTO scores(user_id,competency,score) VALUES(?,?,?)',(uid,comp,min(score,4.8)))
   for i,course in enumerate(COURSES):
    pct=(j*13+i*17)%8*10
    c.execute('INSERT INTO progress(user_id,course_id,percent) VALUES(?,?,?)',(uid,course[0],min(pct,100)))
  for cid,items in QUESTIONS.items():
   for prompt,options,correct,reason in items:
    c.execute('INSERT INTO questions(course_id,prompt,choices,correct,reason) VALUES(?,?,?,?,?)',(cid,prompt,json.dumps(options,ensure_ascii=False),correct,reason))
  for j in range(37):
   c.execute('INSERT INTO tickets(user_id,subject,description,status,reply) VALUES(?,?,?,?,?)',(j+2,['Kesulitan mengakses video','Pertanyaan modul','Butuh panduan belajar'][j%3],'Mohon bantuan terkait materi pembelajaran.',['Baru','Diproses','Selesai'][j%3],''))
  for j in range(52):
   c.execute('INSERT INTO feedback(user_id,course_id,rating,comment) VALUES(?,?,?,?)',(j+2,COURSES[j%5][0],3+j%3,'Materi membantu meningkatkan pemahaman tugas.'))
  print('Database created:',DB,'(360 fictitious employees)')

def rows(cur):return [dict(x) for x in cur.fetchall()]

def ok(x,status=200):return status, {'ok':True,'data':x}

def err(msg,status=400):return status, {'ok':False,'error':msg}

def user_for(req,c):
 cookies=SimpleCookie();cookies.load(req.headers.get('Cookie',''))
 morsel=cookies.get('orbipera_session')
 if not morsel:return None
 token=morsel.value
 found=c.execute('SELECT u.id,u.name,u.email,u.role,u.position,u.department FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token_hash=? AND s.expires>?',(hashlib.sha256(token.encode()).hexdigest(),int(time.time()))).fetchone()
 return dict(found) if found else None

class Handler(BaseHTTPRequestHandler):
 server_version='ORBIPERA/1.0'
 def log_message(self,format,*args):pass
 def write(self,status,payload,extra=None):
  raw=json.dumps(payload,ensure_ascii=False).encode()
  self.send_response(status)
  self.send_header('Content-Type','application/json; charset=utf-8')
  self.send_header('Cache-Control','no-store')
  self.send_header('X-Content-Type-Options','nosniff')
  self.send_header('X-Frame-Options','DENY')
  if extra:
   for k,v in extra.items():self.send_header(k,v)
  self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
 def serve_file(self,path):
  if not path.is_file():return self.send_error(404)
  if path.suffix=='.html':mime='text/html; charset=utf-8'
  else:mime=mimetypes.guess_type(str(path))[0] or 'application/octet-stream'
  size=path.stat().st_size
  first,last=0,size-1
  range_header=self.headers.get('Range','')
  partial=False
  if range_header:
   match=re.fullmatch(r'bytes=(\d*)-(\d*)',range_header)
   if not match:return self.send_error(416)
   a,b=match.groups()
   if not a and not b:return self.send_error(416)
   if not a:
    tail=int(b);first=max(0,size-tail);last=size-1
   else:
    first=int(a);last=min(size-1,int(b)) if b else size-1
   if first>=size or first>last:return self.send_error(416)
   partial=True
  self.send_response(206 if partial else 200)
  self.send_header('Content-Type',mime)
  self.send_header('Content-Length',str(last-first+1))
  self.send_header('Accept-Ranges','bytes')
  if partial:self.send_header('Content-Range',f'bytes {first}-{last}/{size}')
  self.send_header('Cache-Control','public, max-age=3600' if '/assets/' in str(path) else 'no-store')
  self.send_header('X-Content-Type-Options','nosniff')
  self.end_headers()
  with path.open('rb') as stream:
   stream.seek(first)
   remaining=last-first+1
   while remaining:
    chunk=stream.read(min(128*1024,remaining))
    if not chunk:break
    self.wfile.write(chunk)
    remaining-=len(chunk)
 def do_GET(self):
  path=urlparse(self.path).path
  if path=='/' or path=='/index.html':return self.serve_file(BASE/'index.html')
  if path.startswith('/assets/'):
   name=unquote(path[len('/assets/'):])
   if '/' in name or '\\' in name or name.startswith('.'):return self.send_error(403)
   return self.serve_file(BASE/'assets'/name)
  if path.startswith('/api/'):
   with conn() as c:
    u=user_for(self,c)
    if path=='/api/session':return self.write(*ok({'user':u,'online':True}))
    if path=='/api/catalog':return self.write(*ok(rows(c.execute('SELECT * FROM courses'))))
    if path=='/api/company':return self.write(*ok(dict(c.execute('SELECT * FROM company WHERE id=1').fetchone())))
    if not u:return self.write(*err('Login diperlukan',401))
    if path=='/api/dashboard':
     if u['role']=='hr':
      result={'total':c.execute("SELECT COUNT(*) FROM users WHERE role='employee'").fetchone()[0], 'score':round(c.execute('SELECT AVG(score) FROM scores').fetchone()[0] or 0,1),'progress':round(c.execute('SELECT AVG(percent) FROM progress').fetchone()[0] or 0), 'tickets':c.execute("SELECT COUNT(*) FROM tickets WHERE status!='Selesai'").fetchone()[0],'departments':rows(c.execute("SELECT department,COUNT(*) as count FROM users WHERE role='employee' GROUP BY department"))}
     else:
      result={'scores':rows(c.execute('SELECT competency,score FROM scores WHERE user_id=?',(u['id'],))), 'progress':rows(c.execute('SELECT course_id,percent FROM progress WHERE user_id=?',(u['id'],))), 'tickets':c.execute("SELECT COUNT(*) FROM tickets WHERE user_id=? AND status!='Selesai'",(u['id'],)).fetchone()[0]}
     return self.write(*ok(result))
    if path=='/api/employees':
     if u['role']!='hr':return self.write(*err('Hanya HR',403))
     q=parse_qs(urlparse(self.path).query)
     search=(q.get('q',[''])[0] or '').strip()[:80]
     page=max(1,min(50,int(q.get('page',['1'])[0] or '1')))
     limit=20
     crit="WHERE role='employee' AND (name LIKE ? OR email LIKE ? OR department LIKE ? OR position LIKE ?)"
     params=('%'+search+'%',)*4
     total=c.execute('SELECT COUNT(*) FROM users '+crit,params).fetchone()[0]
     peeps=rows(c.execute('SELECT id,name,email,position,department FROM users '+crit+' ORDER BY id LIMIT ? OFFSET ?',(*params,limit,(page-1)*limit)))
     for p in peeps:
      p['score']=round(c.execute('SELECT AVG(score) FROM scores WHERE user_id=?',(p['id'],)).fetchone()[0] or 0,1)
      p['progress']=round(c.execute('SELECT AVG(percent) FROM progress WHERE user_id=?',(p['id'],)).fetchone()[0] or 0)
     return self.write(*ok({'rows':peeps,'total':total,'page':page,'limit':limit}))
    if path=='/api/skills':
     q=parse_qs(urlparse(self.path).query)
     target=int(q.get('user_id',[str(u['id'])])[0])
     if u['role']!='hr' and target!=u['id']:return self.write(*err('Dilarang',403))
     scores=rows(c.execute('SELECT competency,score FROM scores WHERE user_id=? ORDER BY competency',(target,)))
     for item in scores:item['target']=STANDARD.get(item['competency'],4)
     return self.write(*ok(scores))
    if path=='/api/progress':
     q=parse_qs(urlparse(self.path).query);target=int(q.get('user_id',[str(u['id'])])[0])
     if u['role']!='hr' and target!=u['id']:return self.write(*err('Dilarang',403))
     return self.write(*ok(rows(c.execute('SELECT course_id,percent FROM progress WHERE user_id=?',(target,)))))
    if path=='/api/quizzes':
     q=parse_qs(urlparse(self.path).query);cid=q.get('course_id',[''])[0]
     if cid not in {a[0] for a in COURSES}:return self.write(*err('Kursus tidak ada',404))
     vals=rows(c.execute('SELECT id,prompt,choices FROM questions WHERE course_id=? ORDER BY id',(cid,)))
     for x in vals:x['choices']=json.loads(x['choices'])
     return self.write(*ok(vals))
    if path=='/api/attempts':return self.write(*ok(rows(c.execute('SELECT id,course_id,percent,created_at FROM quiz_attempts WHERE user_id=? ORDER BY id DESC LIMIT 40',(u['id'],)))))
    if path=='/api/tickets':
     query='SELECT t.id,t.user_id,t.subject,t.description,t.status,t.reply,t.created_at,u.name FROM tickets t JOIN users u ON u.id=t.user_id'
     if u['role']=='hr':items=rows(c.execute(query+' ORDER BY t.id DESC LIMIT 300'))
     else:items=rows(c.execute(query+' WHERE t.user_id=? ORDER BY t.id DESC',(u['id'],)))
     return self.write(*ok(items))
    if path=='/api/feedback':return self.write(*ok(rows(c.execute('SELECT f.id,f.course_id,f.rating,f.comment,f.created_at,u.name FROM feedback f JOIN users u ON u.id=f.user_id ORDER BY f.id DESC LIMIT 120'))))
    if path=='/api/hr-monitor':
     if u['role']!='hr':return self.write(*err('Hanya HR',403))
     items=rows(c.execute("SELECT u.id,u.name,u.department,ROUND(AVG(p.percent),0) as progress FROM users u LEFT JOIN progress p ON p.user_id=u.id WHERE u.role='employee' GROUP BY u.id ORDER BY progress DESC LIMIT 30"))
     return self.write(*ok(items))
    return self.write(*err('Endpoint tidak ditemukan',404))
  self.send_error(404)
 def do_POST(self):
  path=urlparse(self.path).path
  if not path.startswith('/api/'):return self.write(*err('Tidak ditemukan',404))
  length=int(self.headers.get('Content-Length','0') or 0)
  if length>65536:return self.write(*err('Data terlalu besar',413))
  try:body=json.loads(self.rfile.read(length).decode() or '{}')
  except:return self.write(*err('JSON tidak valid'))
  # CSRF defense for browser requests; support localhost origins only when available
  origin=self.headers.get('Origin','')
  host=self.headers.get('Host','')
  if origin and not origin.endswith(host):return self.write(*err('Origin ditolak',403))
  with conn() as c:
   if path=='/api/login':
    email=str(body.get('email','')).strip().lower()[:200]
    pwd=str(body.get('password',''))[:200]
    found=c.execute('SELECT * FROM users WHERE email=?',(email,)).fetchone()
    if not found or not pw_check(pwd,found['password_hash']):return self.write(*err('Email atau password salah',401))
    token=secrets.token_urlsafe(32)
    c.execute('INSERT INTO sessions VALUES(?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),found['id'],int(time.time())+86400))
    secure='; Secure' if self.headers.get('X-Forwarded-Proto','').lower()=='https' else ''
    return self.write(200,{'ok':True,'data':{'user':{'id':found['id'],'name':found['name'],'email':found['email'],'role':found['role'],'department':found['department']}}}, {'Set-Cookie':f'orbipera_session={token}; HttpOnly; SameSite=Lax; Path=/; Max-Age=86400{secure}'})
   u=user_for(self,c)
   if path=='/api/logout':
    cookie=SimpleCookie();cookie.load(self.headers.get('Cookie',''))
    if cookie.get('orbipera_session'):c.execute('DELETE FROM sessions WHERE token_hash=?',(hashlib.sha256(cookie['orbipera_session'].value.encode()).hexdigest(),))
    return self.write(200,{'ok':True,'data':None},{'Set-Cookie':'orbipera_session=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0'})
   if not u:return self.write(*err('Login diperlukan',401))
   if path=='/api/score':
    if u['role']!='hr':return self.write(*err('Hanya HR yang boleh menilai',403))
    uid=int(body.get('user_id',0));comp=body.get('competency');score=float(body.get('score',0))
    if comp not in STANDARD or not 1<=score<=5:return self.write(*err('Skor harus 1–5'))
    if not c.execute("SELECT id FROM users WHERE id=? AND role='employee'",(uid,)).fetchone():return self.write(*err('Karyawan tidak ada',404))
    c.execute('INSERT INTO scores(user_id,competency,score) VALUES(?,?,?) ON CONFLICT(user_id,competency) DO UPDATE SET score=excluded.score,updated_at=CURRENT_TIMESTAMP',(uid,comp,score))
    return self.write(*ok({'saved':True}))
   if path=='/api/progress':
    uid=int(body.get('user_id',u['id']));cid=str(body.get('course_id',''))
    if uid!=u['id'] and u['role']!='hr':return self.write(*err('Tidak diizinkan',403))
    value=int(body.get('percent',0))
    if cid not in {a[0] for a in COURSES} or not 0<=value<=100:return self.write(*err('Progres tidak valid'))
    passed=c.execute('SELECT 1 FROM quiz_attempts WHERE user_id=? AND course_id=? AND percent>=70 LIMIT 1',(uid,cid)).fetchone()
    if value>80 and not passed:return self.write(*err('Nilai progres maksimal 80% sebelum lulus kuis'))
    c.execute('INSERT INTO progress(user_id,course_id,percent) VALUES(?,?,?) ON CONFLICT(user_id,course_id) DO UPDATE SET percent=excluded.percent,updated_at=CURRENT_TIMESTAMP',(uid,cid,value))
    return self.write(*ok({'saved':True,'percent':value}))
   if path=='/api/learning-event':
    cid=str(body.get('course_id',''));kind=str(body.get('kind',''))
    if cid not in {a[0] for a in COURSES} or kind not in ('video_finished','module_opened'):return self.write(*err('Aktivitas belajar tidak valid'))
    c.execute('INSERT INTO learning_events(user_id,course_id,kind) VALUES(?,?,?)',(u['id'],cid,kind))
    limit=40 if kind=='video_finished' else 70
    c.execute('INSERT INTO progress(user_id,course_id,percent) VALUES(?,?,?) ON CONFLICT(user_id,course_id) DO UPDATE SET percent=MAX(percent,excluded.percent),updated_at=CURRENT_TIMESTAMP',(u['id'],cid,limit))
    return self.write(*ok({'saved':True,'kind':kind,'minimum_progress':limit}))
   if path=='/api/quiz-submit':
    cid=str(body.get('course_id',''));answers=body.get('answers',{})
    if cid not in {a[0] for a in COURSES} or not isinstance(answers,dict):return self.write(*err('Jawaban tidak valid'))
    q=rows(c.execute('SELECT id,prompt,choices,correct,reason FROM questions WHERE course_id=? ORDER BY id',(cid,)))
    grade=[];correct=0
    for item in q:
     answer=answers.get(str(item['id']),None)
     valid=isinstance(answer,int) and 0<=answer<4
     good=valid and answer==item['correct']
     correct+=int(good)
     grade.append({'id':item['id'],'your_answer':answer,'correct':item['correct'],'is_correct':good,'explanation':item['reason']})
    percent=round(correct/max(1,len(q))*100)
    c.execute('INSERT INTO quiz_attempts(user_id,course_id,percent,answers) VALUES(?,?,?,?)',(u['id'],cid,percent,json.dumps(answers)))
    if percent>=70:
     c.execute('UPDATE progress SET percent=MAX(percent,100),updated_at=CURRENT_TIMESTAMP WHERE user_id=? AND course_id=?',(u['id'],cid))
    return self.write(*ok({'score':percent,'passed':percent>=70,'correct':correct,'total':len(q),'details':grade}))
   if path=='/api/ticket-create':
    subject=str(body.get('subject','')).strip()[:100];description=str(body.get('description','')).strip()[:1000]
    if len(subject)<4 or len(description)<10:return self.write(*err('Isi subjek dan deskripsi lengkap'))
    c.execute('INSERT INTO tickets(user_id,subject,description) VALUES(?,?,?)',(u['id'],subject,description))
    return self.write(*ok({'saved':True}))
   if path=='/api/ticket-update':
    if u['role']!='hr':return self.write(*err('Hanya HR',403))
    tid=int(body.get('id',0));status=str(body.get('status',''))
    if status not in ('Baru','Diproses','Selesai'):return self.write(*err('Status tidak valid'))
    reply=str(body.get('reply',''))[:1000]
    c.execute('UPDATE tickets SET status=?,reply=? WHERE id=?',(status,reply,tid))
    return self.write(*ok({'saved':c.total_changes>0}))
   if path=='/api/feedback-create':
    cid=str(body.get('course_id',''));rating=int(body.get('rating',0));comment=str(body.get('comment','')).strip()[:500]
    if cid not in {a[0] for a in COURSES} or rating not in range(1,6) or len(comment)<5:return self.write(*err('Feedback tidak valid'))
    c.execute('INSERT INTO feedback(user_id,course_id,rating,comment) VALUES(?,?,?,?)',(u['id'],cid,rating,comment))
    return self.write(*ok({'saved':True}))
   if path=='/api/plan':
    if u['role']!='hr':return self.write(*err('Hanya HR',403))
    plan=str(body.get('plan',''))
    if plan not in ('Basic','Professional','Business','Enterprise'):return self.write(*err('Paket tidak dikenal'))
    c.execute('UPDATE company SET plan=? WHERE id=1',(plan,))
    return self.write(*ok({'plan':plan,'note':'Paket uji: tidak ada transaksi maupun pembatasan produksi'}))
   if path=='/api/company':
    if u['role']!='hr':return self.write(*err('Hanya HR',403))
    name=str(body.get('name','')).strip()[:90]
    if len(name)<3:return self.write(*err('Nama perusahaan minimal 3 karakter'))
    c.execute('UPDATE company SET name=?,industry=?,address=?,description=? WHERE id=1',(name,str(body.get('industry',''))[:120],str(body.get('address',''))[:200],str(body.get('description',''))[:500]))
    return self.write(*ok({'saved':True}))
   return self.write(*err('Endpoint tidak ada',404))

if __name__=='__main__':
 init_db()
 print(f'ORBIPERA website: http://{HOST}:{PORT}')
 print('HR: admin@orbipera.demo / Admin123!')
 print('Karyawan: andi.rahman@orbipera.demo / Karyawan123!')
 print('For internet deployment: set ORBIPERA_HOST=0.0.0.0 and put behind HTTPS reverse proxy.')
 ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
