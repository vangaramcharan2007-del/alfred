"""
Elden Ring God-Mode Save Enhancer
==================================
Fully automated tool for unlocking God-Tier status in Elden Ring (ER0000.sl2):
- Max level (713) with all stats at 99 (Vigor, Mind, End, Str, Dex, Int, Fai, Arc)
- 999,999,999 Runes
- Max Flasks: 30x Golden Seeds, 12x Sacred Tears (14 Flasks +12 potency)
- Max DLC Blessings: 50x Scadutree Fragments, 25x Revered Spirit Ashes
- All 154 Talismans unlocked
- All 163 Sorceries and Incantations unlocked
- All 33 Bell Bearings unlocked (unlimited merchant materials)
- 100x of all regular Smithing Stones (1-8 + Ancient Dragon)
- 100x of all Somber Smithing Stones (1-9 + Somber Ancient Dragon)
- 50x Great Grave and Ghost Gloveworts
- 99x Rune Arcs, 50x Larval Tears, 20x Celestial Dew, 99x Lord's Runes
- S-Tier God Weapons: Rivers of Blood, Blasphemous Blade, Moonveil, Dark Moon Greatsword,
  Bolt of Gransax, Hand of Malenia, Starscourge Greatsword, Giant-Crusher,
  Fingerprint Stone Shield, Azur's Glintstone Staff, Clawmark Seal
- S-Tier Armor Sets: Bull-Goat Set, Radahn's Set, Veteran's Set, Black Knife Set, Malenia's Set
- Automatic MD5 checksum recalculation and timestamped safety backups.
"""

from __future__ import annotations

import os
import sys
import shutil
import datetime
from pathlib import Path

# Add EldenSave package path
SAVE_EDITOR_DIR = Path(r"E:\Games\Elden Ring\Save_Editor\EldenSave-main")
if str(SAVE_EDITOR_DIR) not in sys.path:
    sys.path.insert(0, str(SAVE_EDITOR_DIR))

from eldensave.savefile import EldenRingSave, STAT_OFFSETS
from eldensave.items import (
    WEAPONS_FULL,
    ARMOR_FULL,
    TALISMANS_FULL,
    GOODS_FULL,
    SPELLS_FULL,
    BELL_BEARINGS,
    item_id_bytes,
    find,
)


def enhance_save(
    save_path: str | Path,
    slot_index: int = 0,
    dry_run: bool = False,
) -> dict:
    save_path = Path(save_path)
    if not save_path.exists():
        raise FileNotFoundError(f"Save file not found at: {save_path}")

    # 1. Create Timestamped Backup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = save_path.parent / f"{save_path.name}.backup_godmode_{timestamp}"
    if not dry_run:
        shutil.copy2(save_path, backup_path)
        print(f"[+] Safety backup created at: {backup_path}")

    # 2. Load Save File
    save = EldenRingSave.load(save_path)
    slot = save.slots[slot_index]

    char_name = slot.character_name()
    if not char_name:
        raise ValueError(f"Character slot {slot_index} appears empty!")

    print(f"[+] Processing Character: {char_name!r} (Slot {slot_index})")
    initial_stats = slot.all_stats()
    initial_runes = slot.runes()

    report = {
        "character": char_name,
        "slot": slot_index,
        "initial_level": initial_stats.get("level"),
        "initial_runes": initial_runes,
        "talismans_added": 0,
        "spells_added": 0,
        "bearings_added": 0,
        "materials_added": 0,
        "weapons_added": 0,
        "armors_added": 0,
    }

    # 3. Apply Max Stats & Runes
    slot.set_runes(999_999_999)
    god_stats = {
        "vigor": 99,
        "mind": 99,
        "endurance": 99,
        "strength": 99,
        "dexterity": 99,
        "intelligence": 99,
        "faith": 99,
        "arcane": 99,
        "level": 713,
    }
    for stat_name, val in god_stats.items():
        slot.set_stat(stat_name, val)
    print("[+] Stats set to 99 across all attributes (Level 713 God-Mode)")
    print("[+] Runes set to 999,999,999")

    # 4. Add All 154 Talismans
    print("[*] Injecting all Talismans...")
    for name, hex_id in TALISMANS_FULL.items():
        try:
            slot.add_good(item_id_bytes(hex_id), quantity=1)
            report["talismans_added"] += 1
        except Exception:
            pass
    print(f"[+] Added {report['talismans_added']} Talismans.")

    # 5. Add All 163 Spells (Sorceries & Incantations)
    print("[*] Injecting all Sorceries and Incantations...")
    for name, hex_id in SPELLS_FULL.items():
        try:
            slot.add_good(item_id_bytes(hex_id), quantity=1)
            report["spells_added"] += 1
        except Exception:
            pass
    print(f"[+] Added {report['spells_added']} Spells.")

    # 6. Add All 33 Bell Bearings
    print("[*] Injecting all Bell Bearings...")
    for name, hex_id in BELL_BEARINGS.items():
        try:
            slot.add_good(item_id_bytes(hex_id), quantity=1)
            report["bearings_added"] += 1
        except Exception:
            pass
    print(f"[+] Added {report['bearings_added']} Bell Bearings.")

    # 7. Add Max Upgrade Materials (Smithing & Somber Stones, Gloveworts)
    print("[*] Injecting Smithing & Somber Stones + Gloveworts...")
    materials_list = [
        # Regular Smithing Stones
        *[(f"Smithing Stone [{i}]", 100) for i in range(1, 9)],
        ("Ancient Dragon Smithing Stone", 100),
        # Somber Smithing Stones
        *[(f"Somber Smithing Stone [{i}]", 100) for i in range(1, 10)],
        ("Somber Ancient Dragon Smithing Stone", 100),
        # Gloveworts
        *[(f"Grave Glovewort [{i}]", 50) for i in range(1, 10)],
        ("Great Grave Glovewort", 50),
        *[(f"Ghost Glovewort [{i}]", 50) for i in range(1, 10)],
        ("Great Ghost Glovewort", 50),
        # Flasks
        ("Golden Seed", 30),
        ("Sacred Tear", 12),
        # DLC
        ("Scadutree Fragment", 50),
        ("Revered Spirit Ash", 25),
        # Consumables
        ("Larval Tear", 50),
        ("Rune Arc", 99),
        ("Celestial Dew", 20),
        ("Lord's Rune", 99),
        ("Boiled Crab", 99),
    ]

    for name, qty in materials_list:
        try:
            hex_id = find(name, GOODS_FULL)
            slot.add_good(item_id_bytes(hex_id), quantity=qty)
            report["materials_added"] += 1
        except Exception:
            pass
    print(f"[+] Added {report['materials_added']} Material & Consumable stacks.")

    # 8. Add Top-Tier Weapons
    print("[*] Injecting S-Tier Legendary Weapons...")
    target_weapons = [
        "Rivers of Blood",
        "Blasphemous Blade",
        "Moonveil",
        "Dark Moon Greatsword",
        "Bolt of Gransax",
        "Hand of Malenia",
        "Starscourge Greatsword",
        "Giant-Crusher",
        "Fingerprint Stone Shield",
        "Azur's Glintstone Staff",
        "Clawmark Seal",
    ]
    for wep_name in target_weapons:
        try:
            hex_id = find(wep_name, WEAPONS_FULL)
            slot.add_weapon(item_id_bytes(hex_id))
            report["weapons_added"] += 1
        except Exception as e:
            print(f"    [-] Skipped weapon {wep_name}: {e}")
    print(f"[+] Added {report['weapons_added']} Legendary Weapons.")

    # 9. Add Top-Tier Armor Sets
    print("[*] Injecting Legendary Armor Sets...")
    target_armors = [
        # Bull-Goat Set
        "Bull-Goat Helm",
        "Bull-Goat Armor",
        "Bull-Goat Gauntlets",
        "Bull-Goat Greaves",
        # Radahn's Set
        "Radahn's Redmane Helm",
        "Radahn's Lion Armor",
        "Radahn's Gauntlets",
        "Radahn's Greaves",
        # Veteran's Set
        "Veteran's Helm",
        "Veteran's Armor",
        "Veteran's Gauntlets",
        "Veteran's Greaves",
        # Black Knife Set
        "Black Knife Hood",
        "Black Knife Armor",
        "Black Knife Gauntlets",
        "Black Knife Greaves",
        # Malenia's Set
        "Malenia's Winged Helm",
        "Malenia's Armor",
        "Malenia's Gauntlet",
        "Malenia's Greaves",
    ]
    for armor_name in target_armors:
        try:
            hex_id = find(armor_name, ARMOR_FULL)
            slot.add_armor(item_id_bytes(hex_id))
            report["armors_added"] += 1
        except Exception as e:
            print(f"    [-] Skipped armor {armor_name}: {e}")
    print(f"[+] Added {report['armors_added']} Legendary Armor pieces.")

    # 10. Save and Recalculate Checksums
    if not dry_run:
        print("[*] Recalculating MD5 checksums and writing save...")
        save.save(save_path, backup=False)
        print("[+] Save file successfully updated and signed!")

    report["final_level"] = 713
    report["final_runes"] = 999_999_999
    return report


def main():
    target_save = Path(r"C:\Users\vanga\AppData\Roaming\EldenRing\76561197960271872\ER0000.sl2")
    if not target_save.exists():
        print(f"[!] Error: Target save file not found at {target_save}")
        sys.exit(1)

    print("=" * 65)
    print("       JARVIS X: ELDEN RING GOD-MODE ENGINE (OPTION 2)")
    print("=" * 65)

    res = enhance_save(target_save, slot_index=0, dry_run=False)

    print("\n" + "=" * 65)
    print("               ENHANCEMENT SUMMARY REPORT")
    print("=" * 65)
    print(f"Character:          {res['character']} (Slot {res['slot']})")
    print(f"Level:              {res['initial_level']} -> {res['final_level']} (MAX LEVEL 713)")
    print(f"Runes:              {res['initial_runes']:,} -> {res['final_runes']:,}")
    print(f"Vigor / Mind / End: 99 / 99 / 99")
    print(f"Str / Dex / Int:    99 / 99 / 99")
    print(f"Faith / Arcane:     99 / 99")
    print(f"Talismans Added:    {res['talismans_added']} (All Talismans in Elden Ring)")
    print(f"Spells Added:       {res['spells_added']} (All Sorceries & Incantations)")
    print(f"Bell Bearings:      {res['bearings_added']} (All Merchant Bells for Unlimited Materials)")
    print(f"Material Stacks:    {res['materials_added']} (100x Smithing/Somber 1-9 & Ancient Dragon)")
    print(f"Legendary Weapons:  {res['weapons_added']} (Rivers of Blood, Blasphemous Blade, etc.)")
    print(f"Legendary Armor:    {res['armors_added']} (Bull-Goat, Radahn, Veteran, Black Knife, Malenia)")
    print("=" * 65)
    print("[SUCCESS] Elden Ring save is now God-Tier. Ready to launch!")


if __name__ == "__main__":
    main()
