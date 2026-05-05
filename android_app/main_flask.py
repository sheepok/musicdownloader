"""
音乐批量下载器 - Android Termux版
通过 Flask Web 服务器在 Android 上运行
"""
import os
import sys
import shutil
import threading
import json
import re
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5000
SAVE_DIR = "/sdcard/MusicDownloads"
os.makedirs(SAVE_DIR, exist_ok=True)

# ---------- 加载 musicdl ----------
try:
    from musicdl.musicdl import MusicClient
    MUSICDL_OK = True
except ImportError:
    MUSICDL_OK = False
    print("musicdl not installed. Run: pip install musicdl")

# ---------- Flask ----------
try:
    from flask import Flask, request, jsonify
    FLASK_OK = True
except ImportError:
    FLASK_OK = False
    print("flask not installed. Run: pip install flask")

if not MUSICDL_OK or not FLASK_OK:
    print("Missing dependencies!")
    sys.exit(1)

app = Flask(__name__)

SOURCES = {
    "netease": "NeteaseMusicClient",
    "qq": "QQMusicClient",
    "kuwo": "KuwoMusicClient",
    "kugou": "KugouMusicClient",
    "migu": "MiguMusicClient",
}

AUDIO_EXTS = {".mp3", ".flac", ".wav", ".m4a", ".aac", ".ogg", ".wma", ".ape", ".opus"}

_client = None
_download_status = {"running": False, "progress": 0, "total": 0, "log": [], "found": 0}


def get_client(sources):
    global _client
    if _client is None:
        src_names = [v for k, v in SOURCES.items() if k in sources]
        cfg = {}
        for sn in src_names:
            cfg[sn] = {"search_size_per_source": 5, "work_dir": SAVE_DIR}
        _client = MusicClient(music_sources=src_names, init_music_clients_cfg=cfg)
    return _client


def flatten_downloads(root_dir):
    """将子目录中的文件移到根目录"""
    moved = 0
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        if os.path.samefile(dirpath, root_dir):
            continue
        for filename in filenames:
            src = os.path.join(dirpath, filename)
            ext = os.path.splitext(filename)[1].lower()
            if ext not in AUDIO_EXTS:
                continue
            dst = os.path.join(root_dir, filename)
            if os.path.exists(dst):
                base, e = os.path.splitext(filename)
                c = 1
                while True:
                    dst = os.path.join(root_dir, f"{base}_{c}{e}")
                    if not os.path.exists(dst):
                        break
                    c += 1
            try:
                shutil.move(src, dst)
                moved += 1
            except Exception:
                pass
        try:
            if not os.listdir(dirpath):
                os.rmdir(dirpath)
        except Exception:
            pass
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        if os.path.samefile(dirpath, root_dir):
            continue
        try:
            if not os.listdir(dirpath):
                os.rmdir(dirpath)
        except Exception:
            pass
    return moved


@app.route("/")
def index():
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no">
<title>音乐下载器</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#0d1117;color:#c9d1d9;padding:16px;max-width:500px;margin:0 auto}
h1{text-align:center;font-size:22px;margin-bottom:16px;color:#58a6ff}
.card{background:#161b22;border-radius:12px;padding:16px;margin-bottom:12px;border:1px solid #30363d}
.card h2{font-size:15px;margin-bottom:10px;color:#e6edf3}
.source-row{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px}
.chip{display:flex;align-items:center;gap:4px;padding:8px 12px;background:#21262d;border-radius:20px;font-size:13px;cursor:pointer;border:1px solid #30363d;user-select:none}
.chip.active{background:#1f6feb33;border-color:#58a6ff;color:#58a6ff}
.chip input{display:none}
textarea{width:100%;min-height:120px;background:#0d1117;color:#c9d1d9;border:1px solid #30363d;border-radius:8px;padding:12px;font-size:14px;resize:vertical;font-family:inherit}
textarea:focus{outline:none;border-color:#58a6ff}
.btn{width:100%;padding:14px;border:none;border-radius:10px;font-size:16px;font-weight:bold;cursor:pointer;margin-bottom:8px;color:#fff}
.btn-primary{background:#238636}
.btn-primary:disabled{background:#30363d;color:#888}
.btn-secondary{background:#21262d;border:1px solid #30363d}
#log{background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:12px;height:200px;overflow-y:auto;font-size:12px;font-family:monospace;white-space:pre-wrap;line-height:1.6}
.progress-bar{height:6px;background:#21262d;border-radius:3px;margin:8px 0;overflow:hidden}
.progress-fill{height:100%;background:#58a6ff;border-radius:3px;transition:width .3s;width:0%}
.status{text-align:center;font-size:13px;color:#8b949e;margin:8px 0}
</style>
</head>
<body>
<h1>音乐批量下载器</h1>

<div class="card">
  <h2>音乐来源</h2>
  <div class="source-row" id="sources">
    <label class="chip active"><input type="checkbox" value="netease" checked> 网易云</label>
    <label class="chip active"><input type="checkbox" value="qq" checked> QQ</label>
    <label class="chip active"><input type="checkbox" value="kuwo" checked> 酷我</label>
    <label class="chip active"><input type="checkbox" value="kugou" checked> 酷狗</label>
    <label class="chip active"><input type="checkbox" value="migu" checked> 咪咕</label>
  </div>
</div>

<div class="card">
  <h2>歌曲名称（每行一首）</h2>
  <textarea id="songs" placeholder="晴天&#10;稻香&#10;夜曲&#10;青花瓷&#10;..."></textarea>
</div>

<button class="btn btn-primary" id="btnDownload" onclick="startDownload()">开始下载</button>
<button class="btn btn-secondary" onclick="clearLog()">清空日志</button>

<div class="progress-bar"><div class="progress-fill" id="progressBar"></div></div>
<div class="status" id="status">就绪 | 保存到: /sdcard/MusicDownloads</div>
<div id="log">等待操作...</div>

<script>
var chips=document.querySelectorAll('.chip');
chips.forEach(function(c){c.addEventListener('click',function(){this.classList.toggle('active');this.querySelector('input').checked=this.classList.contains('active')})});

function startDownload(){
  var songs=document.getElementById('songs').value.trim();
  if(!songs){alert('请输入歌曲名称');return}
  var sources=[];
  document.querySelectorAll('#sources input:checked').forEach(function(c){sources.push(c.value)});
  if(sources.length===0){alert('请选择音乐来源');return}
  var btn=document.getElementById('btnDownload');
  btn.disabled=true;
  btn.textContent='下载中...';
  document.getElementById('log').textContent='正在处理...\\n';
  document.getElementById('progressBar').style.width='0%';
  fetch('/api/download',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({songs:songs, sources:sources})
  }).then(function(r){return r.json()}).then(function(data){
    if(data.error){document.getElementById('log').textContent+='[ERR] '+data.error+'\\n'}
    btn.disabled=false;
    btn.textContent='开始下载';
    document.getElementById('status').textContent='完成';
  });
}

function clearLog(){
  document.getElementById('log').textContent='';
  document.getElementById('progressBar').style.width='0%';
  document.getElementById('status').textContent='就绪 | 保存到: /sdcard/MusicDownloads';
}

setInterval(function(){
  fetch('/api/status').then(function(r){return r.json()}).then(function(d){
    if(d.running){
      document.getElementById('progressBar').style.width=(d.progress/d.total*100)+'%';
      document.getElementById('status').textContent=d.progress+'/'+d.total;
      document.getElementById('log').textContent=d.log.join('\\n');
      document.getElementById('log').scrollTop=document.getElementById('log').scrollHeight;
      if(!document.getElementById('btnDownload').disabled){
        document.getElementById('btnDownload').disabled=true;
        document.getElementById('btnDownload').textContent='下载中...';
      }
    }
  });
},1000);
</script>
</body>
</html>"""


@app.route("/api/download", methods=["POST"])
def api_download():
    global _download_status
    if _download_status["running"]:
        return jsonify({"error": "已有下载任务在运行"})

    data = request.json
    raw_songs = data.get("songs", "")
    sources = data.get("sources", ["netease", "qq", "kuwo", "kugou", "migu"])

    keywords = []
    for line in raw_songs.split("\n"):
        line = line.strip()
        if not line:
            continue
        for ch in ["，", "；", ";"]:
            line = line.replace(ch, ",")
        for p in line.split(","):
            p = p.strip()
            if p:
                keywords.append(p)
    seen = set()
    keywords = [k for k in keywords if not (k in seen or seen.add(k))]

    if not keywords:
        return jsonify({"error": "未识别到有效歌曲名称"})

    _download_status = {
        "running": True, "progress": 0, "total": len(keywords),
        "log": [f"共 {len(keywords)} 首歌曲", ""], "found": 0,
    }

    thread = threading.Thread(target=_run_download, args=(keywords, sources), daemon=True)
    thread.start()
    return jsonify({"ok": True, "total": len(keywords)})


def _run_download(keywords, sources):
    global _download_status
    try:
        client = get_client(sources)
        songs = []
        for i, kw in enumerate(keywords):
            _download_status["progress"] = i + 1
            _download_status["log"].append(f"搜索 ({i+1}/{len(keywords)}): {kw}")
            try:
                results = client.search(keyword=kw)
                best = None
                for sr in results.values():
                    if sr and len(sr) > 0:
                        best = sr[0]
                        break
                if best:
                    name = best.song_name or kw
                    singers = best.singers or ""
                    if isinstance(singers, list):
                        singers = ", ".join(singers)
                    songs.append(best)
                    _download_status["log"].append(f"  [OK] {name} - {singers}")
                    _download_status["found"] += 1
                else:
                    _download_status["log"].append(f"  [NO] 未找到")
            except Exception as e:
                _download_status["log"].append(f"  [ERR] 失败: {e}")

        if songs:
            _download_status["log"].append("")
            _download_status["log"].append(f"下载中... {len(songs)} 首")
            client.download(song_infos=songs)
            moved = flatten_downloads(SAVE_DIR)
            _download_status["log"].append(f"完成！共 {len(songs)} 首")
            _download_status["log"].append(f"保存: {SAVE_DIR}")
        else:
            _download_status["log"].append("未找到任何匹配歌曲")
    except Exception as e:
        _download_status["log"].append(f"[ERR] 错误: {e}")
    finally:
        _download_status["running"] = False


@app.route("/api/status")
def api_status():
    return jsonify(_download_status)


if __name__ == "__main__":
    print("=" * 50)
    print("  音乐批量下载器 (Android Termux版)")
    print("=" * 50)
    print()
    print(f"  请在手机浏览器中打开:")
    print(f"  http://localhost:{PORT}")
    print()
    print(f"  保存目录: {SAVE_DIR}")
    print()
    app.run(host=HOST, port=PORT, debug=False)
