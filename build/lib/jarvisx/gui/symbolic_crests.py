"""
Symbolic Crests for Jarvis X Dual-Hero HUD:
==========================================
- Spider Crest (E-V): Cyberpunk Arachnid Neon Emblem (#00f0ff Cyan / #ff003c Crimson)
- Bat Crest (Alfred): Dark Knight Gothic Shield (#ffd700 Gold / #0a0e17 Obsidian)
"""

SPIDER_CREST_SVG = """<svg viewBox="0 0 100 100" class="crest-svg spider-crest-svg" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="spiderGlow" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ff003c" />
      <stop offset="50%" stop-color="#00f0ff" />
      <stop offset="100%" stop-color="#ff003c" />
    </linearGradient>
    <filter id="spiderNeon" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>
  <!-- Cyber Spider Body & Head -->
  <ellipse cx="50" cy="40" rx="9" ry="12" fill="url(#spiderGlow)" filter="url(#spiderNeon)" />
  <circle cx="50" cy="24" r="6" fill="#00f0ff" filter="url(#spiderNeon)" />
  <ellipse cx="50" cy="62" rx="14" ry="18" fill="url(#spiderGlow)" filter="url(#spiderNeon)" />
  <!-- Spidey Eyes -->
  <polygon points="46,22 49,25 46,26" fill="#ffffff" />
  <polygon points="54,22 51,25 54,26" fill="#ffffff" />
  <!-- Upper Arachnid Legs -->
  <path d="M43,36 Q25,18 18,32 Q14,40 10,48" stroke="#00f0ff" stroke-width="3.5" fill="none" stroke-linecap="round" filter="url(#spiderNeon)"/>
  <path d="M57,36 Q75,18 82,32 Q86,40 90,48" stroke="#00f0ff" stroke-width="3.5" fill="none" stroke-linecap="round" filter="url(#spiderNeon)"/>
  <path d="M42,42 Q20,32 15,48 Q12,58 8,66" stroke="#ff003c" stroke-width="3.5" fill="none" stroke-linecap="round" filter="url(#spiderNeon)"/>
  <path d="M58,42 Q80,32 85,48 Q88,58 92,66" stroke="#ff003c" stroke-width="3.5" fill="none" stroke-linecap="round" filter="url(#spiderNeon)"/>
  <!-- Lower Arachnid Legs -->
  <path d="M42,54 Q22,58 18,72 Q15,82 12,92" stroke="#ff003c" stroke-width="3.5" fill="none" stroke-linecap="round" filter="url(#spiderNeon)"/>
  <path d="M58,54 Q78,58 82,72 Q85,82 88,92" stroke="#ff003c" stroke-width="3.5" fill="none" stroke-linecap="round" filter="url(#spiderNeon)"/>
  <path d="M44,66 Q30,76 26,88 Q24,94 20,98" stroke="#00f0ff" stroke-width="3" fill="none" stroke-linecap="round" filter="url(#spiderNeon)"/>
  <path d="M56,66 Q70,76 74,88 Q76,94 80,98" stroke="#00f0ff" stroke-width="3" fill="none" stroke-linecap="round" filter="url(#spiderNeon)"/>
</svg>"""

BAT_CREST_SVG = """<svg viewBox="0 0 120 70" class="crest-svg bat-crest-svg" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="batGlow" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffd700" />
      <stop offset="50%" stop-color="#ffb700" />
      <stop offset="100%" stop-color="#d4af37" />
    </linearGradient>
    <filter id="batNeon" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2.5" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>
  <!-- Batman Gotham Emblem Silhouette -->
  <path d="M60,18 
           L64,8 L68,16 
           C78,12 94,14 116,4 
           C112,24 98,34 94,54 
           C84,46 74,48 60,66 
           C46,48 36,46 26,54 
           C22,34 8,24 4,4 
           C26,14 42,12 52,16 
           L56,8 Z" 
        fill="url(#batGlow)" 
        stroke="#ffd700" 
        stroke-width="2" 
        filter="url(#batNeon)" />
  <!-- Cyber Bat Head Details -->
  <polygon points="56,8 58,16 54,16" fill="#0a0e17" />
  <polygon points="64,8 66,16 62,16" fill="#0a0e17" />
</svg>"""

CREST_CSS = """
.crest-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    background: rgba(18, 26, 43, 0.85);
    border: 2px solid var(--border-glow);
    border-radius: 12px;
    padding: 8px 18px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(10px);
}
.crest-btn:hover {
    transform: translateY(-3px) scale(1.03);
}
.crest-btn.spider-btn {
    border-color: #00f0ff;
}
.crest-btn.spider-btn:hover {
    box-shadow: 0 0 25px rgba(0, 240, 255, 0.6), 0 0 40px rgba(255, 0, 60, 0.4);
    border-color: #ff003c;
}
.crest-btn.bat-btn {
    border-color: #ffd700;
}
.crest-btn.bat-btn:hover {
    box-shadow: 0 0 25px rgba(255, 215, 0, 0.6), 0 0 40px rgba(212, 175, 55, 0.3);
    border-color: #ffffff;
}
.crest-svg {
    transition: transform 0.3s ease;
}
.spider-crest-svg {
    width: 32px;
    height: 32px;
}
.bat-crest-svg {
    width: 40px;
    height: 24px;
}
.crest-btn:hover .crest-svg {
    transform: scale(1.15);
}
.crest-label {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    letter-spacing: 1px;
    text-transform: uppercase;
}
"""
