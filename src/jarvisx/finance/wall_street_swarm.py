import logging
import threading
import time
import yfinance as yf

logger = logging.getLogger(__name__)

class WallStreetSwarm:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._thread = None
        self._running = False
        self.trackers = ["BTC-USD", "NVDA", "AAPL"]
        self.last_prices = {}

    def _push_to_ui(self, event_type: str, data: dict):
        """Broadcast events to E.V. UI."""
        try:
            from jarvisx.dashboard.hud_server import push_event_sync
            push_event_sync(event_type, data)
        except Exception:
            pass

    def start(self):
        if self._running:
            return
            
        logger.info("[WallStreet] Initializing Finance Oracle...")
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while self._running:
            try:
                for ticker in self.trackers:
                    stock = yf.Ticker(ticker)
                    history = stock.history(period="1d")
                    if not history.empty:
                        current_price = history['Close'].iloc[-1]
                        
                        if ticker in self.last_prices:
                            last_price = self.last_prices[ticker]
                            change_pct = ((current_price - last_price) / last_price) * 100
                            
                            # Alert if it moves more than 1% in either direction
                            if abs(change_pct) >= 1.0:
                                direction = "UP" if change_pct > 0 else "DOWN"
                                msg = f"{ticker} is {direction} {abs(change_pct):.2f}% (Now: ${current_price:.2f})"
                                logger.info(f"[WallStreet] ALERT: {msg}")
                                self._push_to_ui("finance_event", {"ticker": ticker, "price": current_price, "change": change_pct})
                        
                        self.last_prices[ticker] = current_price
            except Exception as e:
                logger.debug(f"[WallStreet] Fetch failed: {e}")
                
            # Poll every 60 seconds
            time.sleep(60)
