import logging
import threading
import time
import json
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

class MidasOracle:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread = None

    def _push_to_ui(self, event_type: str, data: dict):
        try:
            from jarvisx.dashboard.hud_server import push_event_sync
            push_event_sync(event_type, data)
        except Exception:
            pass

    def start(self):
        if self._running:
            return
        self._running = True
        logger.info("[Midas] DeFi Sentiment Oracle online.")
        self._thread = threading.Thread(target=self._loop, daemon=True, name="MidasOracle")
        self._thread.start()

    def _loop(self):
        while self._running:
            try:
                # Fetch recent Reddit WSB titles (Reddit JSON API)
                req = urllib.request.Request(
                    "https://www.reddit.com/r/wallstreetbets/hot.json?limit=10",
                    headers={'User-Agent': 'JarvisX/1.0'}
                )
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode())
                
                titles = [child['data']['title'] for child in data['data']['children']]
                
                # Simple heuristic sentiment analysis (Simulating LLM for speed/reliability in background)
                bull_keywords = ['call', 'moon', 'bull', 'buy', 'yolo', 'tendies']
                bear_keywords = ['put', 'bear', 'sell', 'crash', 'drop', 'guh']
                
                bull_score = sum(1 for t in titles for k in bull_keywords if k in t.lower())
                bear_score = sum(1 for t in titles for k in bear_keywords if k in t.lower())
                
                if bull_score > bear_score:
                    sentiment = "BULLISH 🚀"
                elif bear_score > bull_score:
                    sentiment = "BEARISH 🐻"
                else:
                    sentiment = "NEUTRAL 📊"
                    
                logger.info(f"[Midas] Market Sentiment Analysis complete. Current mood: {sentiment}")
                self._push_to_ui("sentiment_event", {"sentiment": sentiment, "bull": bull_score, "bear": bear_score})
            except urllib.error.HTTPError as e:
                if e.code == 429: # Rate limit
                    pass
            except Exception as e:
                logger.debug(f"[Midas] Loop error: {e}")
                
            time.sleep(900) # Check every 15 minutes
