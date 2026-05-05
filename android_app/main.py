"""
音乐批量下载器 - Android版 (Kivy)
"""
import os
import sys
import threading

# ---------- 依赖 ----------
try:
    from musicdl.musicdl import MusicClient
    MUSICDL_OK = True
except ImportError:
    MUSICDL_OK = False
    print("musicdl not installed")

# ---------- Kivy ----------
from kivy.config import Config
Config.set('kivy', 'window_title', '音乐下载器')
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex as C

# ---------- 配置 ----------
SOURCES = [
    ("netease", "网易云", True),
    ("qq", "QQ音乐", True),
    ("kuwo", "酷我", True),
    ("kugou", "酷狗", True),
    ("migu", "咪咕", True),
    ("qianqian", "千千", False),
    ("soda", "汽水", False),
    ("5sing", "5sing", False),
]

SAVE_DIR = "/sdcard/MusicDownloads"


class MusicApp(App):
    def build(self):
        Window.clearcolor = C("#121212")
        return MainScreen()


class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(16)
        self.spacing = dp(12)
        self.is_downloading = False
        self._build_ui()

    def _build_ui(self):
        # --- 标题 ---
        title = Label(
            text="音乐批量下载器",
            font_size=dp(22),
            color=C("#FFFFFF"),
            size_hint=(1, None),
            height=dp(50),
            halign="center",
            valign="middle",
        )
        self.add_widget(title)

        # --- 来源选择 ---
        src_label = Label(
            text="音乐来源（可多选）",
            font_size=dp(14),
            color=C("#AAAAAA"),
            size_hint=(1, None),
            height=dp(28),
            halign="left",
        )
        self.add_widget(src_label)

        self.source_grid = GridLayout(cols=4, spacing=dp(6), size_hint=(1, None), height=dp(80))
        self.source_checks = {}
        for key, name, default in SOURCES:
            box = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(36), spacing=dp(2))
            cb = CheckBox(active=default, size_hint=(None, None), size=(dp(24), dp(24)))
            lbl = Label(text=name, font_size=dp(11), color=C("#CCCCCC"), size_hint=(1, None), height=dp(36))
            lbl.bind(size=lambda lbl, s: setattr(lbl, 'text_size', (lbl.width, None)))
            box.add_widget(cb)
            box.add_widget(lbl)
            self.source_checks[key] = cb
            self.source_grid.add_widget(box)
        self.add_widget(self.source_grid)

        # --- 歌名输入 ---
        input_label = Label(
            text="输入歌曲名称（每行一首）",
            font_size=dp(14),
            color=C("#AAAAAA"),
            size_hint=(1, None),
            height=dp(28),
            halign="left",
        )
        self.add_widget(input_label)

        self.song_input = TextInput(
            hint_text="晴天\n稻香\n夜曲\n青花瓷\n...",
            multiline=True,
            font_size=dp(14),
            background_color=C("#1E1E1E"),
            foreground_color=C("#FFFFFF"),
            cursor_color=C("#FFFFFF"),
            size_hint=(1, 0.4),
            padding=(dp(12), dp(12)),
        )
        self.add_widget(self.song_input)

        # --- 保存目录 ---
        dir_row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(40), spacing=dp(8))
        dir_row.add_widget(Label(text="保存到:", font_size=dp(13), color=C("#AAAAAA"),
                                 size_hint=(None, None), size=(dp(60), dp(40))))
        self.dir_label = TextInput(
            text=SAVE_DIR,
            readonly=True,
            font_size=dp(12),
            background_color=C("#1E1E1E"),
            foreground_color=C("#888888"),
            size_hint=(1, None),
            height=dp(40),
        )
        dir_row.add_widget(self.dir_label)
        self.add_widget(dir_row)

        # --- 进度条 ---
        self.progress = ProgressBar(max=100, value=0, size_hint=(1, None), height=dp(6),
                                    background_color=C("#333333"))
        self.add_widget(self.progress)

        # --- 状态 ---
        self.status_label = Label(
            text="就绪",
            font_size=dp(12),
            color=C("#888888"),
            size_hint=(1, None),
            height=dp(24),
            halign="left",
        )
        self.add_widget(self.status_label)

        # --- 输出日志 ---
        self.output = TextInput(
            text="",
            readonly=True,
            font_size=dp(11),
            background_color=C("#1A1A1A"),
            foreground_color=C("#AAAAAA"),
            size_hint=(1, 0.35),
            padding=(dp(10), dp(10)),
        )
        self.add_widget(self.output)

        # --- 按钮 ---
        btn_row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(52), spacing=dp(12))
        self.btn_dl = Button(
            text="开始下载",
            font_size=dp(16),
            background_color=C("#0078D4"),
            background_normal="",
            color=C("#FFFFFF"),
            size_hint=(1, None),
            height=dp(52),
        )
        self.btn_dl.bind(on_press=self.on_download)
        self.btn_clear = Button(
            text="清空",
            font_size=dp(14),
            background_color=C("#333333"),
            background_normal="",
            color=C("#CCCCCC"),
            size_hint=(0.3, None),
            height=dp(52),
        )
        self.btn_clear.bind(on_press=lambda x: self._clear_output())
        btn_row.add_widget(self.btn_dl)
        btn_row.add_widget(self.btn_clear)
        self.add_widget(btn_row)

    def _log(self, msg):
        self.output.text += msg + "\n"
        self.output.cursor = (0, len(self.output.text))

    def _clear_output(self):
        self.output.text = ""
        self.song_input.text = ""
        self.progress.value = 0
        self.status_label.text = "就绪"

    def _disable_btn(self):
        self.btn_dl.text = "下载中..."
        self.btn_dl.disabled = True
        self.btn_dl.background_color = C("#555555")

    def _enable_btn(self):
        self.btn_dl.text = "开始下载"
        self.btn_dl.disabled = False
        self.btn_dl.background_color = C("#0078D4")

    def _get_selected_sources(self):
        src_map = {
            "netease": "NeteaseMusicClient",
            "qq": "QQMusicClient",
            "kuwo": "KuwoMusicClient",
            "kugou": "KugouMusicClient",
            "migu": "MiguMusicClient",
            "qianqian": "QianqianMusicClient",
            "soda": "SodaMusicClient",
            "5sing": "FiveSingMusicClient",
        }
        return [src_map[k] for k, cb in self.source_checks.items() if cb.active]

    def on_download(self, instance):
        if self.is_downloading:
            return
        if not MUSICDL_OK:
            self._log("musicdl 库未安装")
            return

        raw = self.song_input.text.strip()
        if not raw:
            self._log("请输入歌曲名称")
            return

        keywords = []
        for line in raw.split("\n"):
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
            self._log("未识别到有效歌曲名称")
            return

        sources = self._get_selected_sources()
        if not sources:
            self._log("请至少选择一个音乐来源")
            return

        self._log(f"共 {len(keywords)} 首歌曲")
        self._log(f"来源: {', '.join(sources)}")
        self._log("")

        self.is_downloading = True
        self._disable_btn()
        self.progress.value = 0
        self.progress.max = len(keywords)

        thread = threading.Thread(target=self._do_download, args=(keywords, sources), daemon=True)
        thread.start()

    def _do_download(self, keywords, sources):
        try:
            os.makedirs(SAVE_DIR, exist_ok=True)
            cfg = {}
            for src in sources:
                cfg[src] = {"search_size_per_source": 5, "work_dir": SAVE_DIR}
            client = MusicClient(music_sources=sources, init_music_clients_cfg=cfg)

            songs_to_download = []
            for i, kw in enumerate(keywords):
                Clock.schedule_once(
                    lambda dt, msg=f"搜索 ({i+1}/{len(keywords)}): {kw}": self.status_label.setter("text")(self.status_label, msg),
                    0)
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
                        src = best.source or "?"
                        songs_to_download.append(best)
                        Clock.schedule_once(
                            lambda dt, n=name, s=singers, sr=src: self._log(f"[OK] {n} - {s} [{sr}]"),
                            0,
                        )
                    else:
                        Clock.schedule_once(lambda dt, k=kw: self._log(f"[NO] {k} - 未找到"), 0)
                except Exception as e:
                    Clock.schedule_once(lambda dt, k=kw, e=e: self._log(f"[ERR] {k} 搜索失败: {e}"), 0)
                Clock.schedule_once(lambda dt, v=i+1: setattr(self.progress, 'value', v), 0)

            if not songs_to_download:
                Clock.schedule_once(lambda dt: self._on_done(0), 0)
                return

            Clock.schedule_once(lambda dt: self.status_label.setter("text")(self.status_label, f"下载中... {len(songs_to_download)} 首"), 0)
            try:
                client.download(song_infos=songs_to_download)
                Clock.schedule_once(lambda dt: self._on_done(len(songs_to_download)), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt, e=e: self._log(f"[ERR] 下载失败: {e}"), 0)
                Clock.schedule_once(lambda dt: self._on_done(0), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt, e=e: self._log(f"[ERR] 初始化失败: {e}"), 0)
            Clock.schedule_once(lambda dt: self._on_done(0), 0)

    def _on_done(self, count):
        self.is_downloading = False
        self._enable_btn()
        self.status_label.text = "完成"
        self._log("")
        self._log(f"下载完成！共 {count} 首歌曲")
        self._log(f"保存目录: {SAVE_DIR}")


if __name__ == "__main__":
    MusicApp().run()
