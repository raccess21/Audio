import tkinter as tk
from tkinter import filedialog, simpledialog, ttk
import pygame
import os
import re
import bisect

TIMESTAMP_RE = re.compile(r"\[(\d{2}):(\d{2}\.\d{2})\]\s*(.*)")

class LyricLine(tk.Frame):
    def __init__(self, master, syncer, line_text, line_index):
        super().__init__(master, bg="#f5f5f5", padx=5, pady=2)
        self.syncer = syncer
        self.line_text = line_text
        self.line_index = line_index
        self.timestamp_str = ""
        self.lyric_text = ""

        self.parse_line()
        self.create_widgets()

    def parse_line(self):
        match = re.match(r"\[(\d{2}:\d{2}\.\d{2})\](.*)", self.line_text)
        if match:
            self.timestamp_str = match.group(1)
            self.lyric_text = match.group(2).strip()
        else:
            self.lyric_text = self.line_text.strip()

    def create_widgets(self):
        # Left controls
        left_control_frame = tk.Frame(self, bg="#f5f5f5")
        left_control_frame.pack(side=tk.LEFT, padx=(0, 5))
        
        style = ttk.Style()
        style.configure("Control.TButton", padding=2, font=("Segoe UI", 8))
        
        self.play_button = ttk.Button(left_control_frame, text="▶", width=2,
                                      command=self.play_from_here, style="Control.TButton")
        self.play_button.pack(side=tk.LEFT, padx=1)
        
        self.add_button = ttk.Button(left_control_frame, text="+", width=2,
                                     command=lambda: self.add_time_to_timestamp(sign=1), style="Control.TButton")
        self.add_button.pack(side=tk.LEFT, padx=1)
        
        self.sub_button = ttk.Button(left_control_frame, text="-", width=2,
                                     command=lambda: self.add_time_to_timestamp(sign=-1), style="Control.TButton")
        self.sub_button.pack(side=tk.LEFT, padx=1)

        # Timestamp
        self.timestamp_label = tk.Label(self, text=f"{self.timestamp_str}", width=12,
                                        bg="#e9ecef", fg="#495057", font=("Consolas", 10),
                                        relief="flat", padx=5, pady=3)
        self.timestamp_label.pack(side=tk.LEFT, padx=5)
        self.timestamp_label.bind("<Button-1>", self.update_timestamp)

        # Lyric text
        self.lyric_label = tk.Label(
            self,
            text=self.lyric_text,
            anchor="w",
            wraplength=400,
            justify="left",
            bg="#ffffff",
            fg="#212529",
            font=("Segoe UI", 10),
            padx=10,
            pady=8,
            relief="flat"
        )
        self.lyric_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.lyric_label.bind("<Button-1>", self.edit_lyric)

        # Right controls
        right_control_frame = tk.Frame(self, bg="#f5f5f5")
        right_control_frame.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.delete_button = ttk.Button(right_control_frame, text="✕", width=2,
                                        command=self.delete_timestamp, style="Control.TButton")
        self.delete_button.pack(side=tk.TOP, pady=1)
        
        self.insert_button = ttk.Button(right_control_frame, text="↓", width=2,
                                        command=self.insert_empty_line, style="Control.TButton")
        self.insert_button.pack(side=tk.TOP, pady=1)

    # --- actions on this line ---
    def play_from_here(self):
        if self.timestamp_str:
            minutes, seconds = map(float, self.timestamp_str.split(':'))
            time_in_seconds = minutes * 60 + seconds
            self.syncer.play_audio(start_time=time_in_seconds)

    def delete_timestamp(self):
        if 0 <= self.line_index < len(self.syncer.lyrics):
            del self.syncer.lyrics[self.line_index]
            self.syncer.save_lrc_file()
        self.syncer.display_lyrics()  # rebuild GUI & timeline

    def insert_empty_line(self):
        idx = self.line_index + 1
        self.syncer.lyrics.insert(idx, "\n")
        self.syncer.save_lrc_file()
        self.syncer.display_lyrics()  # rebuild GUI & timeline

    def add_time_to_timestamp(self, sign):
        self._shift_timestamp(sign * 0.2)
        self.play_from_here()

    def _shift_timestamp(self, delta):
        if self.timestamp_str:
            minutes, seconds = map(float, self.timestamp_str.split(':'))
            time_in_seconds = minutes * 60 + seconds + delta
            if time_in_seconds < 0:
                time_in_seconds = 0
            minutes = int(time_in_seconds // 60)
            seconds = time_in_seconds % 60
            self.timestamp_str = f"{minutes:02d}:{seconds:05.2f}"
            self.timestamp_label.config(text=f"{self.timestamp_str}")
            self.update_lrc_line()

    def update_timestamp(self, event):
        if not pygame.mixer.music.get_busy():
            return
        pos_ms = pygame.mixer.music.get_pos()
        if pos_ms < 0 and self.syncer.play_t0 is not None:
            elapsed = (pygame.time.get_ticks() - self.syncer.play_t0) / 1000.0
        else:
            elapsed = max(0.0, pos_ms / 1000.0)
        current_time = self.syncer.start_offset + elapsed
        minutes = int(current_time // 60)
        seconds = current_time % 60
        self.timestamp_str = f"{minutes:02d}:{seconds:05.2f}"
        self.timestamp_label.config(text=f"{self.timestamp_str}")
        self.update_lrc_line()

    def edit_lyric(self, event):
        new_lyric = simpledialog.askstring("Edit Lyric", "Enter new lyric:", initialvalue=self.lyric_text)
        if new_lyric is not None:
            self.lyric_text = new_lyric
            self.lyric_label.config(text=self.lyric_text)
            self.update_lrc_line()
            
    def update_lrc_line(self):
        # persist this line back to lyrics buffer
        new_line = f"[{self.timestamp_str}] {self.lyric_text}\n" if self.timestamp_str else f"{self.lyric_text}\n"
        if 0 <= self.line_index < len(self.syncer.lyrics):
            self.syncer.lyrics[self.line_index] = new_line
            self.syncer.save_lrc_file()
            self.syncer.refresh_timeline()  # keep highlight search accurate
    
    def set_highlight(self, active: bool):
        if active:
            self.config(bg="#fff3cd")
            self.lyric_label.config(bg="#fff3cd", fg="#000000")
            self.timestamp_label.config(bg="#ffeeba", fg="#000000")
        else:
            self.config(bg="#f5f5f5")
            self.lyric_label.config(bg="#ffffff", fg="#212529")
            self.timestamp_label.config(bg="#e9ecef", fg="#495057")


class LyricSyncer:
    def __init__(self, master, audio_file=""):
        self.master = master
        master.title("Lyrics Sync")
        master.configure(bg="#f8f9fa")
        master.geometry("800x600")
        try:
            master.iconbitmap("icon.ico")
        except:
            pass
        
        self.audio_file = audio_file
        self.lrc_file = ""
        self.lyrics = []
        self.lyric_lines = []
        self.timeline = []          # list of (timestamp_seconds, line_index)
        self.timeline_times = []    # only timestamps for bisect
        self.current_highlight = -1
        self.start_offset = 0.0
        self.play_t0 = None

        self.create_widgets()

    def create_widgets(self):
        header_frame = tk.Frame(self.master, bg="#343a40", height=60)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        title_label = tk.Label(header_frame, text="Lyrics Sync", 
                               fg="white", bg="#343a40", font=("Segoe UI", 16, "bold"))
        title_label.pack(side=tk.LEFT, padx=20, pady=18)
        
        control_frame = tk.Frame(self.master, bg="#f8f9fa")
        control_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        style = ttk.Style()
        style.configure("Action.TButton", padding=6, font=("Segoe UI", 9))
        
        self.load_button = ttk.Button(control_frame, text="Load Audio", 
                                      command=self.load_audio, style="Action.TButton")
        self.load_button.pack(side=tk.LEFT, padx=5)
        
        self.play_button = ttk.Button(control_frame, text="Play", 
                                      command=self.play_audio, state=tk.DISABLED, style="Action.TButton")
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        self.load_lrc_button = ttk.Button(control_frame, text="Reload Lyrics", 
                                          command=self.load_lyrics, style="Action.TButton")
        self.load_lrc_button.pack(side=tk.LEFT, padx=5)
        
        self.delay_lrc_button = ttk.Button(control_frame, text="Delay All +0.2s", 
                                           command=lambda: self.sync_all_lyrics(sign=1), style="Action.TButton")
        self.delay_lrc_button.pack(side=tk.LEFT, padx=5)
        
        self.haste_lrc_button = ttk.Button(control_frame, text="Hasten All -0.2s", 
                                           command=lambda: self.sync_all_lyrics(sign=-1), style="Action.TButton")
        self.haste_lrc_button.pack(side=tk.LEFT, padx=5)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to load audio file")
        status_bar = tk.Label(self.master, textvariable=self.status_var, 
                              bg="#e9ecef", fg="#6c757d", font=("Segoe UI", 9), 
                              anchor="w", padx=10, pady=5)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        container = tk.Frame(self.master, bg="#dee2e6", padx=1, pady=1)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.canvas = tk.Canvas(container, bg="white", highlightthickness=0)
        self._bind_mousewheel()

        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f8f9fa")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self._canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=1, pady=1)
        self.scrollbar.pack(side="right", fill="y")

    def _bind_mousewheel(self):
        self.canvas.bind("<Enter>", lambda e: self._activate_mousewheel())
        self.canvas.bind("<Leave>", lambda e: self._deactivate_mousewheel())

    def _activate_mousewheel(self):
        # Windows / Linux
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # macOS
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _deactivate_mousewheel(self):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if event.num == 4:   # macOS scroll up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5: # macOS scroll down
            self.canvas.yview_scroll(1, "units")
        else:                # Windows / Linux
            self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    
    # --- data loading / saving ---
    def load_audio(self):
        self.audio_file = self.audio_file or filedialog.askopenfilename(
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg *.flac")],
            title="Select Audio File"
        )
        if self.audio_file:
            self.lrc_file = os.path.splitext(self.audio_file)[0] + ".lrc"
            self.status_var.set(f"Loaded: {os.path.basename(self.audio_file)}")
            self.load_lyrics()
            self.play_button.config(state=tk.NORMAL)

    def load_lyrics(self):
        if self.lrc_file and os.path.exists(self.lrc_file):
            with open(self.lrc_file, "r", encoding="utf-8") as f:
                self.lyrics = f.readlines()
            self.status_var.set(f"Loaded lyrics from: {os.path.basename(self.lrc_file)}")
        else:
            self.lyrics = [
                f"[00:00.00] Lyrics Not Found\n",
                f"[00:01.00] For File \n",
                f"[00:02.00] {self.lrc_file}\n",
            ]
            self.status_var.set("No lyric file found. Created placeholder lyrics.")
        self.display_lyrics()  # also rebuilds timeline

    def save_lrc_file(self):
        if self.lrc_file:
            with open(self.lrc_file, "w", encoding="utf-8") as f:
                f.writelines(self.lyrics)
            self.status_var.set(f"Saved lyrics to: {os.path.basename(self.lrc_file)}")

    # --- timeline / parsing ---
    def refresh_timeline(self):
        self.timeline = []
        for i, line in enumerate(self.lyrics):
            m = TIMESTAMP_RE.match(line)
            if not m:
                continue
            minutes = int(m.group(1))
            seconds = float(m.group(2))
            ts = minutes * 60 + seconds
            self.timeline.append((ts, i))
        self.timeline.sort(key=lambda x: x[0])
        self.timeline_times = [t for t, _ in self.timeline]

    # --- bulk shift ---
    def sync_all_lyrics(self, sign):
        delta = sign * 0.2
        # shift only lines that actually have timestamps
        for widget in self.lyric_lines:
            widget._shift_timestamp(delta)
        self.refresh_timeline()
        if self.lyric_lines:
            self.lyric_lines[0].play_from_here()
        self.status_var.set(f"All lyrics {'delayed' if sign > 0 else 'hastened'} by 0.2 seconds")

    # --- GUI rebuild ---
    def display_lyrics(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.lyric_lines = []
        
        header = tk.Frame(self.scrollable_frame, bg="#dee2e6", height=30)
        header.pack(fill=tk.X, pady=(0, 5))
        tk.Label(header, text="Controls", bg="#dee2e6", fg="#495057", 
                 font=("Segoe UI", 9, "bold"), width=10).pack(side=tk.LEFT, padx=(15, 0))
        tk.Label(header, text="Timestamp", bg="#dee2e6", fg="#495057", 
                 font=("Segoe UI", 9, "bold"), width=12).pack(side=tk.LEFT, padx=(15, 0))
        tk.Label(header, text="Lyric Text", bg="#dee2e6", fg="#495057", 
                 font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(15, 0))
        tk.Label(header, text="Edit", bg="#dee2e6", fg="#495057", 
                 font=("Segoe UI", 9, "bold"), width=8).pack(side=tk.RIGHT, padx=(0, 15))
        
        for i, line in enumerate(self.lyrics):
            lyric_line_widget = LyricLine(self.scrollable_frame, self, line, i)
            lyric_line_widget.pack(fill=tk.X, pady=1, padx=10)
            self.lyric_lines.append(lyric_line_widget)

        self.refresh_timeline()
        # clear any stale highlight since widgets were rebuilt
        self.current_highlight = -1

    # --- playback ---
    def play_audio(self, start_time=0):
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        self.start_offset = float(start_time)
        self.play_t0 = pygame.time.get_ticks()
        pygame.mixer.music.load(self.audio_file)
        pygame.mixer.music.play(start=start_time)
        self.status_var.set(f"Playing: {os.path.basename(self.audio_file)}")
        self.play_button.config(text="Pause", command=self.pause_audio)
        self.update_highlight()
        
    def pause_audio(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.play_button.config(text="Resume", command=self.resume_audio)
            self.status_var.set("Playback paused")
        else:
            self.resume_audio()
            
    def resume_audio(self):
        pygame.mixer.music.unpause()
        self.play_button.config(text="Pause", command=self.pause_audio)
        self.status_var.set("Resumed playback")
        self.update_highlight()

    # --- highlighting + scrolling ---
    def _scroll_line_into_view(self, idx, margin=20, lookahead=1):
        """
        Ensure the lyric line at idx (and next lines) are visible in the canvas.
        `lookahead` = how many lines ahead should also be visible.
        """
        if not (0 <= idx < len(self.lyric_lines)):
            return

        # Current + next line to consider
        last_idx = min(len(self.lyric_lines) - 1, idx + lookahead)
        widget = self.lyric_lines[idx]
        next_widget = self.lyric_lines[last_idx]

        self.canvas.update_idletasks()

        # Top & bottom of the current + next widget block
        y_top = widget.winfo_y()
        y_bottom = next_widget.winfo_y() + next_widget.winfo_height()

        # Current visible region
        top = self.canvas.canvasy(0)
        bottom = top + self.canvas.winfo_height()

        # Scroll up if current line is above
        if y_top < top + margin:
            target = max(0, y_top - margin)
            total = max(1, self.scrollable_frame.winfo_height())
            self.canvas.yview_moveto(min(1.0, max(0.0, target / total)))
        # Scroll down if next line is below
        elif y_bottom > (bottom - margin):
            target = y_bottom - self.canvas.winfo_height() + margin
            total = max(1, self.scrollable_frame.winfo_height())
            self.canvas.yview_moveto(min(1.0, max(0.0, target / total)))


    def update_highlight(self):
        # keep scheduling even if paused/stopped; if stopped, reset button text
        is_busy = pygame.mixer.music.get_busy()
        if not is_busy:
            self.play_button.config(text="Play", command=self.play_audio)

        # compute current playback time
        pos_ms = pygame.mixer.music.get_pos() if is_busy else -1
        if pos_ms < 0 and self.play_t0 is not None and is_busy:
            elapsed = (pygame.time.get_ticks() - self.play_t0) / 1000.0
        else:
            elapsed = max(0.0, pos_ms / 1000.0) if is_busy else 0.0
        current_time = self.start_offset + elapsed

        # find latest timestamp <= current_time via bisect
        idx = -1
        if self.timeline_times:
            i = bisect.bisect_right(self.timeline_times, current_time) - 1
            if i >= 0:
                idx = self.timeline[i][1]  # map to lyric line index

        # update visual highlight
        if self.current_highlight != idx:
            if 0 <= self.current_highlight < len(self.lyric_lines):
                self.lyric_lines[self.current_highlight].set_highlight(False)
            if 0 <= idx < len(self.lyric_lines):
                self.lyric_lines[idx].set_highlight(True)
                self._scroll_line_into_view(idx)
            self.current_highlight = idx

        # keep polling (even if paused, so resume continues seamlessly)
        self.master.after(100, self.update_highlight)


if __name__ == "__main__":
    pygame.init()
    root = tk.Tk()
    app = LyricSyncer(root, audio_file="Plus Rien Ne Metonne Tikon Jah Fakoly.mp3")
    root.mainloop()
    pygame.quit()
