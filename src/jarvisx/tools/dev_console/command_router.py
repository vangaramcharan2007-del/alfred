"""Command Router for parsing real-time commands using non-blocking msvcrt."""
import sys
import threading
import logging
from typing import Optional, Callable
from jarvisx.core.execution.background_worker import BackgroundWorker
from jarvisx.core.execution.persistent_queue import PersistentQueue
from jarvisx.core.execution.resume_engine import ResumeEngine

try:
    import msvcrt
    MSVCRT_AVAILABLE = True
except ImportError:
    MSVCRT_AVAILABLE = False

logger = logging.getLogger(__name__)

class CommandRouter:
    """Non-blocking keyboard listener mapping shortcuts and typed commands."""
    
    def __init__(self, 
                 worker: BackgroundWorker, 
                 queue: PersistentQueue, 
                 resume_engine: ResumeEngine,
                 on_exit: Callable[[], None],
                 on_simulate_crash: Callable[[], None],
                 on_export: Callable[[], None],
                 on_replay: Callable[[], None]):
        
        self.worker = worker
        self.queue = queue
        self.resume_engine = resume_engine
        self.on_exit = on_exit
        self.on_simulate_crash = on_simulate_crash
        self.on_export = on_export
        self.on_replay = on_replay
        
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        self.input_buffer = ""
        
        # Protect buffer access since dashboard reads it
        self.lock = threading.Lock()
        
    def start(self):
        if not MSVCRT_AVAILABLE:
            logger.error("msvcrt not available. Interactive commands disabled.")
            return
            
        if self._running:
            return
            
        self._running = True
        self._thread = threading.Thread(target=self._input_loop, daemon=True)
        self._thread.start()
        
    def stop(self):
        self._running = False
        
    def get_current_buffer(self) -> str:
        with self.lock:
            return self.input_buffer
            
    def _input_loop(self):
        while self._running:
            if msvcrt.kbhit():
                try:
                    char_bytes = msvcrt.getch()
                    if char_bytes in (b'\x00', b'\xe0'): # special keys like arrows
                        msvcrt.getch()
                        continue
                        
                    char = char_bytes.decode('utf-8')
                    
                    if char == '\r': # Enter
                        with self.lock:
                            cmd = self.input_buffer.strip().lower()
                            self.input_buffer = ""
                        self._process_command(cmd)
                    elif char == '\x08': # Backspace
                        with self.lock:
                            self.input_buffer = self.input_buffer[:-1]
                    elif char == '\x03': # Ctrl+C
                        self.on_exit()
                    else:
                        # Append character to buffer.
                        # Also handle single-key shortcuts if buffer is empty and it's a known hotkey
                        with self.lock:
                            if self.input_buffer == "":
                                hotkey = char.upper()
                                if hotkey in ['P', 'R', 'C', 'X', 'S', 'E', 'L', 'H', 'Q']:
                                    # Translate hotkey to command and execute immediately
                                    self._process_hotkey(hotkey)
                                    continue
                            
                            self.input_buffer += char
                except Exception as e:
                    logger.error(f"Error in input loop: {e}")
            else:
                import time
                time.sleep(0.05)
                
    def _process_hotkey(self, hotkey: str):
        mapping = {
            'P': 'pause',
            'R': 'resume',
            'C': 'crash',
            'X': 'cancel',
            'S': 'stats',
            'E': 'export',
            'L': 'replay',
            'H': 'help',
            'Q': 'quit'
        }
        cmd = mapping.get(hotkey)
        if cmd:
            self._process_command(cmd)
            
    def _process_command(self, cmd: str):
        if not cmd:
            return
            
        if cmd == 'pause':
            self.worker.pause()
        elif cmd == 'resume':
            self.worker.resume()
        elif cmd == 'cancel':
            self.worker.stop()
            # To strictly cancel, we would dequeue or mark FAILED
        elif cmd == 'crash':
            self.on_simulate_crash()
        elif cmd == 'restart':
            self.resume_engine.resume_unfinished_objectives()
            if not self.worker.is_running():
                self.worker.start()
        elif cmd == 'export':
            self.on_export()
        elif cmd == 'replay':
            self.on_replay()
        elif cmd in ['quit', 'q', 'exit']:
            self.on_exit()
