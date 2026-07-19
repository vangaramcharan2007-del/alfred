import threading
import time
import logging
import os
import subprocess

from jarvisx.core.whatsapp.ui_controller import WhatsAppUIController
from jarvisx.core.whatsapp.listener import WhatsAppListener
from jarvisx.core.whatsapp.downloader import WhatsAppDownloader
from jarvisx.core.whatsapp.uploader import WhatsAppUploader
from jarvisx.core.document.storage import DocumentStorage
from jarvisx.core.document.word_to_excel import WordToExcelConverter

logger = logging.getLogger(__name__)

class WhatsAppAutomationManager:
    """Orchestrates the WhatsApp document automation workflow."""
    
    def __init__(self, tts_engine=None, storage_dir=None):
        self.storage = DocumentStorage(base_dir=storage_dir)
        self.ui = WhatsAppUIController()
        self.listener = WhatsAppListener(download_dir=self.storage.inbox_dir)
        self.downloader = WhatsAppDownloader(self.ui, self.storage.inbox_dir)
        self.uploader = WhatsAppUploader(self.ui)
        self.converter = WordToExcelConverter()
        self.tts = tts_engine
        
        self.is_running = False
        self.is_paused = False
        self._thread = None
        self.files_converted_today = 0
        
    def announce(self, message: str):
        logger.info(f"[VOICE] {message}")
        if self.tts:
            try:
                self.tts.speak(message)
            except Exception as e:
                logger.error(f"TTS failed: {e}")
                
    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.is_paused = False
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info("WhatsApp Automation Manager started.")
        
    def stop(self):
        self.is_running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            
    def pause(self):
        self.is_paused = True
        
    def resume(self):
        self.is_paused = False

    def _monitor_loop(self):
        while self.is_running:
            if self.is_paused:
                time.sleep(1)
                continue
                
            try:
                new_file = self.listener.check_for_new_file()
                if new_file and not self.storage.is_duplicate(new_file):
                    self.process_file(new_file)
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                
            time.sleep(2)
            
    def process_file(self, filepath: str):
        filename = os.path.basename(filepath)
        self.announce(f"I received a new document: {filename}")
        self.announce("Converting the document to Excel.")
        
        # Determine destination path
        dest_filename = os.path.splitext(filename)[0] + ".xlsx"
        dest_path = os.path.join(self.storage.outbox_dir, dest_filename)
        
        # Convert
        result = self.converter.convert(filepath, dest_path)
        
        if result["success"]:
            self.announce("Conversion completed successfully.")
            self.files_converted_today += 1
            
            # Open the file automatically
            self.announce("Opening the converted workbook for verification.")
            try:
                os.startfile(dest_path)
            except Exception as e:
                logger.error(f"Could not open file: {e}")
            
            # Move source to archive
            self.storage.archive_source(filepath)
            
            # Send back
            self.announce("Sending the Excel workbook back through WhatsApp.")
            
            # Select contact (fallback to 'Dad' if not specified)
            self.ui.select_chat("Dad")
            success = self.uploader.upload_file(dest_path)
            
            if success:
                self.announce("Done, sir. The converted file has been delivered.")
            else:
                self.announce("The conversion succeeded, but sending the file failed. Please check WhatsApp manually.")
                
        else:
            logger.error(f"Conversion failed: {result.get('error')}")
            if "No tables found" in str(result.get('error')):
                self.announce("The document doesn't contain any tables suitable for Excel conversion.")
            else:
                self.announce("I couldn't convert the document because it appears to be corrupted or invalid.")
