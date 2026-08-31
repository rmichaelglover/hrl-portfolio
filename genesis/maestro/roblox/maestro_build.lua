-- ═══════════════════════════════════════════════════════════════
--  CHESS MAESTRO — the board as a Roblox world  (generated from core.js)
--  King Me: mannyfresher 1-0 Lerouxdu74 · ply 39/39 (Qa8#)
--  HRL influence terrain + tactical-role piece totems.  By Manny Glover.
--
--  RUN: Roblox Studio ▸ New ▸ Baseplate ▸ View ▸ Command Bar → paste → Enter
--       (or drop into a Script in ServerScriptService and press Play)
-- ═══════════════════════════════════════════════════════════════
local SIZE, LV = 8, 4
local old = workspace:FindFirstChild("ChessMaestro"); if old then old:Destroy() end
local root = Instance.new("Model"); root.Name = "ChessMaestro"; root.Parent = workspace

local function blk(fx, y, fz, color)
	local p = Instance.new("Part")
	p.Anchored = true
	p.Size = Vector3.new(SIZE, LV, SIZE)
	p.Position = Vector3.new(fx * SIZE + SIZE/2, y * LV + LV/2, fz * SIZE + SIZE/2)
	p.Color = color
	p.Material = Enum.Material.SmoothPlastic
	p.TopSurface = Enum.SurfaceType.Smooth
	p.Parent = root
	return p
end

-- influence terrain: {file, rank, height, color}
local TERR = { {0,0,1,Color3.fromRGB(228,228,220)}, {1,0,1,Color3.fromRGB(70,78,96)}, {2,0,1,Color3.fromRGB(120,130,128)}, {3,0,1,Color3.fromRGB(46,150,205)}, {4,0,1,Color3.fromRGB(46,150,205)}, {5,0,1,Color3.fromRGB(46,150,205)}, {6,0,1,Color3.fromRGB(70,78,96)}, {7,0,1,Color3.fromRGB(46,150,205)}, {0,1,1,Color3.fromRGB(228,228,220)}, {1,1,1,Color3.fromRGB(70,78,96)}, {2,1,1,Color3.fromRGB(70,78,96)}, {3,1,1,Color3.fromRGB(228,228,220)}, {4,1,1,Color3.fromRGB(120,130,128)}, {5,1,1,Color3.fromRGB(228,228,220)}, {6,1,1,Color3.fromRGB(228,228,220)}, {7,1,1,Color3.fromRGB(120,130,128)}, {0,2,1,Color3.fromRGB(46,150,205)}, {1,2,1,Color3.fromRGB(120,130,128)}, {2,2,1,Color3.fromRGB(228,228,220)}, {3,2,1,Color3.fromRGB(228,228,220)}, {4,2,3,Color3.fromRGB(228,228,220)}, {5,2,2,Color3.fromRGB(228,228,220)}, {6,2,1,Color3.fromRGB(228,228,220)}, {7,2,1,Color3.fromRGB(120,130,128)}, {0,3,1,Color3.fromRGB(46,150,205)}, {1,3,1,Color3.fromRGB(46,150,205)}, {2,3,1,Color3.fromRGB(70,78,96)}, {3,3,1,Color3.fromRGB(228,228,220)}, {4,3,1,Color3.fromRGB(228,228,220)}, {5,3,1,Color3.fromRGB(46,150,205)}, {6,3,1,Color3.fromRGB(120,130,128)}, {7,3,1,Color3.fromRGB(120,130,128)}, {0,4,1,Color3.fromRGB(228,228,220)}, {1,4,1,Color3.fromRGB(120,130,128)}, {2,4,1,Color3.fromRGB(70,78,96)}, {3,4,1,Color3.fromRGB(228,228,220)}, {4,4,1,Color3.fromRGB(120,130,128)}, {5,4,1,Color3.fromRGB(228,228,220)}, {6,4,1,Color3.fromRGB(120,130,128)}, {7,4,1,Color3.fromRGB(228,228,220)}, {0,5,1,Color3.fromRGB(228,228,220)}, {1,5,1,Color3.fromRGB(120,130,128)}, {2,5,1,Color3.fromRGB(228,228,220)}, {3,5,1,Color3.fromRGB(70,78,96)}, {4,5,1,Color3.fromRGB(70,78,96)}, {5,5,1,Color3.fromRGB(70,78,96)}, {6,5,2,Color3.fromRGB(70,78,96)}, {7,5,1,Color3.fromRGB(70,78,96)}, {0,6,1,Color3.fromRGB(46,150,205)}, {1,6,1,Color3.fromRGB(228,228,220)}, {2,6,1,Color3.fromRGB(46,150,205)}, {3,6,1,Color3.fromRGB(228,228,220)}, {4,6,1,Color3.fromRGB(46,150,205)}, {5,6,1,Color3.fromRGB(228,228,220)}, {6,6,1,Color3.fromRGB(70,78,96)}, {7,6,1,Color3.fromRGB(70,78,96)}, {0,7,1,Color3.fromRGB(46,150,205)}, {1,7,1,Color3.fromRGB(228,228,220)}, {2,7,1,Color3.fromRGB(70,78,96)}, {3,7,1,Color3.fromRGB(120,130,128)}, {4,7,1,Color3.fromRGB(120,130,128)}, {5,7,1,Color3.fromRGB(70,78,96)}, {6,7,1,Color3.fromRGB(70,78,96)}, {7,7,1,Color3.fromRGB(120,130,128)} }
for _, t in ipairs(TERR) do
	for y = 0, t[3] - 1 do blk(t[1], y, t[2], t[4]) end
end

-- pieces: {file, rank, base, height, roleColor, capColor}
local PCS = { {1,0,1,2,Color3.fromRGB(74,120,224),Color3.fromRGB(232,238,244)}, {2,0,1,3,Color3.fromRGB(224,84,70),Color3.fromRGB(38,42,52)}, {3,1,1,1,Color3.fromRGB(74,120,224),Color3.fromRGB(232,238,244)}, {4,1,1,3,Color3.fromRGB(74,120,224),Color3.fromRGB(232,238,244)}, {5,1,1,1,Color3.fromRGB(74,120,224),Color3.fromRGB(232,238,244)}, {2,2,1,1,Color3.fromRGB(245,197,66),Color3.fromRGB(232,238,244)}, {4,2,3,1,Color3.fromRGB(245,197,66),Color3.fromRGB(232,238,244)}, {6,3,1,1,Color3.fromRGB(132,142,152),Color3.fromRGB(232,238,244)}, {1,4,1,1,Color3.fromRGB(132,142,152),Color3.fromRGB(38,42,52)}, {4,4,1,1,Color3.fromRGB(245,197,66),Color3.fromRGB(38,42,52)}, {0,6,1,2,Color3.fromRGB(224,84,70),Color3.fromRGB(232,238,244)}, {5,6,1,1,Color3.fromRGB(132,142,152),Color3.fromRGB(38,42,52)}, {6,6,1,1,Color3.fromRGB(132,142,152),Color3.fromRGB(38,42,52)}, {7,6,1,1,Color3.fromRGB(132,142,152),Color3.fromRGB(38,42,52)}, {0,7,1,3,Color3.fromRGB(224,84,70),Color3.fromRGB(232,238,244)}, {1,7,1,3,Color3.fromRGB(224,84,70),Color3.fromRGB(38,42,52)}, {5,7,1,2,Color3.fromRGB(74,120,224),Color3.fromRGB(38,42,52)}, {7,7,1,2,Color3.fromRGB(74,120,224),Color3.fromRGB(38,42,52)} }
for _, p in ipairs(PCS) do
	for y = 0, p[4] - 1 do blk(p[1], p[3] + y, p[2], p[5]) end
	blk(p[1], p[3] + p[4], p[2], p[6])
end

local spawn = Instance.new("SpawnLocation")
spawn.Anchored = true
spawn.Size = Vector3.new(SIZE, 1, SIZE)
spawn.Position = Vector3.new(4 * SIZE, 60, -SIZE)
spawn.Neutral = true
spawn.Parent = root

print("Chess Maestro built — " .. #root:GetChildren() .. " objects · King Me (Qa8#)")
