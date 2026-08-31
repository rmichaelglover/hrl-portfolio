# ═══════════════════════════════════════════════════════════════
#  CHESS MAESTRO — the board as a Minecraft world  (generated from core.js)
#  King Me: mannyfresher 1-0 Lerouxdu74 · ply 39/39 (Qa8#)
#  HRL influence terrain + tactical-role wool totems.  By Manny Glover.
#  RUN in a CREATIVE superflat world:  /reload  ·  /function maestro:build  ·  /tp @s 4 -55 4
# ═══════════════════════════════════════════════════════════════

# --- influence terrain (water = contested seam, height = control strength) ---
fill 0 -60 0 0 -60 0 minecraft:white_concrete
fill 1 -60 0 1 -60 0 minecraft:gray_concrete
fill 2 -60 0 2 -60 0 minecraft:light_gray_concrete
fill 3 -60 0 3 -60 0 minecraft:light_blue_concrete
fill 4 -60 0 4 -60 0 minecraft:light_blue_concrete
fill 5 -60 0 5 -60 0 minecraft:light_blue_concrete
fill 6 -60 0 6 -60 0 minecraft:gray_concrete
fill 7 -60 0 7 -60 0 minecraft:light_blue_concrete
fill 0 -60 1 0 -60 1 minecraft:white_concrete
fill 1 -60 1 1 -60 1 minecraft:gray_concrete
fill 2 -60 1 2 -60 1 minecraft:gray_concrete
fill 3 -60 1 3 -60 1 minecraft:white_concrete
fill 4 -60 1 4 -60 1 minecraft:light_gray_concrete
fill 5 -60 1 5 -60 1 minecraft:white_concrete
fill 6 -60 1 6 -60 1 minecraft:white_concrete
fill 7 -60 1 7 -60 1 minecraft:light_gray_concrete
fill 0 -60 2 0 -60 2 minecraft:light_blue_concrete
fill 1 -60 2 1 -60 2 minecraft:light_gray_concrete
fill 2 -60 2 2 -60 2 minecraft:white_concrete
fill 3 -60 2 3 -60 2 minecraft:white_concrete
fill 4 -60 2 4 -58 2 minecraft:white_concrete
fill 5 -60 2 5 -59 2 minecraft:white_concrete
fill 6 -60 2 6 -60 2 minecraft:white_concrete
fill 7 -60 2 7 -60 2 minecraft:light_gray_concrete
fill 0 -60 3 0 -60 3 minecraft:light_blue_concrete
fill 1 -60 3 1 -60 3 minecraft:light_blue_concrete
fill 2 -60 3 2 -60 3 minecraft:gray_concrete
fill 3 -60 3 3 -60 3 minecraft:white_concrete
fill 4 -60 3 4 -60 3 minecraft:white_concrete
fill 5 -60 3 5 -60 3 minecraft:light_blue_concrete
fill 6 -60 3 6 -60 3 minecraft:light_gray_concrete
fill 7 -60 3 7 -60 3 minecraft:light_gray_concrete
fill 0 -60 4 0 -60 4 minecraft:white_concrete
fill 1 -60 4 1 -60 4 minecraft:light_gray_concrete
fill 2 -60 4 2 -60 4 minecraft:gray_concrete
fill 3 -60 4 3 -60 4 minecraft:white_concrete
fill 4 -60 4 4 -60 4 minecraft:light_gray_concrete
fill 5 -60 4 5 -60 4 minecraft:white_concrete
fill 6 -60 4 6 -60 4 minecraft:light_gray_concrete
fill 7 -60 4 7 -60 4 minecraft:white_concrete
fill 0 -60 5 0 -60 5 minecraft:white_concrete
fill 1 -60 5 1 -60 5 minecraft:light_gray_concrete
fill 2 -60 5 2 -60 5 minecraft:white_concrete
fill 3 -60 5 3 -60 5 minecraft:gray_concrete
fill 4 -60 5 4 -60 5 minecraft:gray_concrete
fill 5 -60 5 5 -60 5 minecraft:gray_concrete
fill 6 -60 5 6 -59 5 minecraft:gray_concrete
fill 7 -60 5 7 -60 5 minecraft:gray_concrete
fill 0 -60 6 0 -60 6 minecraft:light_blue_concrete
fill 1 -60 6 1 -60 6 minecraft:white_concrete
fill 2 -60 6 2 -60 6 minecraft:light_blue_concrete
fill 3 -60 6 3 -60 6 minecraft:white_concrete
fill 4 -60 6 4 -60 6 minecraft:light_blue_concrete
fill 5 -60 6 5 -60 6 minecraft:white_concrete
fill 6 -60 6 6 -60 6 minecraft:gray_concrete
fill 7 -60 6 7 -60 6 minecraft:gray_concrete
fill 0 -60 7 0 -60 7 minecraft:light_blue_concrete
fill 1 -60 7 1 -60 7 minecraft:white_concrete
fill 2 -60 7 2 -60 7 minecraft:gray_concrete
fill 3 -60 7 3 -60 7 minecraft:light_gray_concrete
fill 4 -60 7 4 -60 7 minecraft:light_gray_concrete
fill 5 -60 7 5 -60 7 minecraft:gray_concrete
fill 6 -60 7 6 -60 7 minecraft:gray_concrete
fill 7 -60 7 7 -60 7 minecraft:light_gray_concrete

# --- pieces, tinted by relaxed tactical role, capped by side ---
fill 1 -59 0 1 -58 0 minecraft:blue_wool
setblock 1 -57 0 minecraft:white_wool
fill 2 -59 0 2 -57 0 minecraft:red_wool
setblock 2 -56 0 minecraft:black_wool
fill 3 -59 1 3 -59 1 minecraft:blue_wool
setblock 3 -58 1 minecraft:white_wool
fill 4 -59 1 4 -57 1 minecraft:blue_wool
setblock 4 -56 1 minecraft:white_wool
fill 5 -59 1 5 -59 1 minecraft:blue_wool
setblock 5 -58 1 minecraft:white_wool
fill 2 -59 2 2 -59 2 minecraft:yellow_wool
setblock 2 -58 2 minecraft:white_wool
fill 4 -57 2 4 -57 2 minecraft:yellow_wool
setblock 4 -56 2 minecraft:white_wool
fill 6 -59 3 6 -59 3 minecraft:gray_wool
setblock 6 -58 3 minecraft:white_wool
fill 1 -59 4 1 -59 4 minecraft:gray_wool
setblock 1 -58 4 minecraft:black_wool
fill 4 -59 4 4 -59 4 minecraft:yellow_wool
setblock 4 -58 4 minecraft:black_wool
fill 0 -59 6 0 -58 6 minecraft:red_wool
setblock 0 -57 6 minecraft:white_wool
fill 5 -59 6 5 -59 6 minecraft:gray_wool
setblock 5 -58 6 minecraft:black_wool
fill 6 -59 6 6 -59 6 minecraft:gray_wool
setblock 6 -58 6 minecraft:black_wool
fill 7 -59 6 7 -59 6 minecraft:gray_wool
setblock 7 -58 6 minecraft:black_wool
fill 0 -59 7 0 -57 7 minecraft:red_wool
setblock 0 -56 7 minecraft:white_wool
fill 1 -59 7 1 -57 7 minecraft:red_wool
setblock 1 -56 7 minecraft:black_wool
fill 5 -59 7 5 -58 7 minecraft:blue_wool
setblock 5 -57 7 minecraft:black_wool
fill 7 -59 7 7 -58 7 minecraft:blue_wool
setblock 7 -57 7 minecraft:black_wool

tellraw @a ["",{"text":"\u265f Chess Maestro — ","color":"gold","bold":true},{"text":"the board as a world · King Me (Qa8#)","color":"gray"}]
