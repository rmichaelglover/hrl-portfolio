--!strict
--=====================================================================
--  THE CRITTER  —  a self-relaxing simplicial organism, in Roblox
--  A port of hrl-portfolio/genesis/critter (the autopoiesis toy).
--
--  HOW TO RUN
--    1. Open Roblox Studio, new Baseplate.
--    2. In Explorer, right-click ServerScriptService -> Insert Object -> Script.
--    3. Delete the default line, paste ALL of this in.
--    4. Press Play.  A living, colour-shifting organism grows above spawn;
--       walk up and CLICK a cell to poke it (an avalanche ripples out).
--
--  It runs our engine on itself: cells relaxation-label toward their
--  neighbours (E-step), then the body grows where coherent, grooms the
--  undecided, buds children when whole, and self-tunes its temperature
--  to the critical edge (self-organized criticality).
--=====================================================================

local COLORS = {
	Color3.fromRGB(95, 227, 160),   -- cell type 1
	Color3.fromRGB(192, 96, 255),   -- cell type 2
	Color3.fromRGB(232, 207, 112),  -- cell type 3
}
local K       = 3
local SPACING = 2.6      -- rest distance between neighbouring cells
local RNB     = 3.7      -- neighbour radius
local NMAX    = 120      -- carrying capacity
local NMIN    = 10
local ORIGIN  = Vector3.new(0, 26, 0)
local TICK    = 0.14     -- seconds per step

type Cell = { pos: Vector3, p: { number }, part: Part, age: number }

local cells: { Cell } = {}
local T = 0.5            -- temperature (self-tuned toward criticality)

local folder = Instance.new("Folder")
folder.Name = "Critter"
folder.Parent = workspace

local function rndp(): { number }
	local a, b, c = math.random(), math.random(), math.random()
	local s = a + b + c
	return { a / s, b / s, c / s }
end

local function dom(p: { number }): number
	local m, mi = 0, 1
	for l = 1, K do if p[l] > m then m = p[l]; mi = l end end
	return mi
end

local function makeCell(pos: Vector3, p: { number }): Cell
	local pt = Instance.new("Part")
	pt.Shape = Enum.PartType.Ball
	pt.Size = Vector3.new(1.5, 1.5, 1.5)
	pt.Anchored = true
	pt.CanCollide = false
	pt.Material = Enum.Material.Neon
	pt.Position = pos
	pt.Color = COLORS[dom(p)]
	pt.Parent = folder
	local cell: Cell = { pos = pos, p = p, part = pt, age = 0 }
	local cd = Instance.new("ClickDetector")
	cd.MaxActivationDistance = 1000
	cd.Parent = pt
	cd.MouseClick:Connect(function()
		for _, o in cells do
			if (o.pos - cell.pos).Magnitude < RNB * 1.6 then o.p = rndp() end
		end
	end)
	return cell
end

local function seed()
	for _, c in cells do c.part:Destroy() end
	cells = {}
	for i = 0, 5 do
		local ang = i * (math.pi * 2 / 6)
		local pos = ORIGIN + Vector3.new(math.cos(ang) * SPACING, 0, math.sin(ang) * SPACING)
		table.insert(cells, makeCell(pos, rndp()))
	end
	table.insert(cells, makeCell(ORIGIN, rndp()))
	T = 0.5
end

local function neighbours(i: number): { number }
	local res = {}
	local ci = cells[i]
	for j, cj in cells do
		if j ~= i and (cj.pos - ci.pos).Magnitude < RNB then
			table.insert(res, j)
		end
	end
	return res
end

local function centroid(): Vector3
	local s = Vector3.zero
	for _, c in cells do s += c.pos end
	return #cells > 0 and s / #cells or ORIGIN
end

-- E-STEP: relaxation labelling at temperature T
local function relax()
	local beta = 1 / math.max(0.12, T)
	local changed, cnt = 0, 0
	for i, c in cells do
		local nb = neighbours(i)
		if #nb == 0 then continue end
		local sup = { 0, 0, 0 }
		for _, j in nb do
			local pj = cells[j].p
			sup[1] += pj[1]; sup[2] += pj[2]; sup[3] += pj[3]
		end
		local inv = 1 / #nb
		sup[1] *= inv; sup[2] *= inv; sup[3] *= inv
		local h = {
			sup[1] + 0.35 * (sup[2] + sup[3]),
			sup[2] + 0.35 * (sup[1] + sup[3]),
			sup[3] + 0.35 * (sup[1] + sup[2]),
		}
		local mx = math.max(h[1], h[2], h[3])
		local d0 = dom(c.p)
		local np = { 0, 0, 0 }
		local z = 0
		for l = 1, K do np[l] = (c.p[l] ^ 0.2) * math.exp(beta * (h[l] - mx)); z += np[l] end
		for l = 1, K do np[l] /= z end
		for l = 1, K do np[l] = math.max(1e-4, np[l] + (math.random() - 0.5) * 0.55 * T) end
		local s = np[1] + np[2] + np[3]
		np[1] /= s; np[2] /= s; np[3] /= s
		c.p = np; c.age += 1; cnt += 1
		if dom(np) ~= d0 then changed += 1 end
		c.part.Color = COLORS[dom(np)]
	end
	local activity = cnt > 0 and changed / cnt or 0
	-- self-organized criticality: homeostatic annealing toward the critical edge
	if activity < 0.03 then
		T = math.min(1.2, T * 1.03)
	elseif activity > 0.12 then
		T = math.max(0.15, T * 0.97)
	end
end

-- gentle spring so the body keeps its shape and wriggles
local function relaxPositions()
	local n = #cells
	local disp = table.create(n, Vector3.zero)
	for i = 1, n do
		local ci = cells[i]
		for j = i + 1, n do
			local d = ci.pos - cells[j].pos
			local dist = d.Magnitude
			if dist > 0.01 and dist < RNB * 1.3 then
				local force = (SPACING - dist) * 0.12
				local push = (d / dist) * force
				disp[i] += push; disp[j] -= push
			end
		end
	end
	for i, c in cells do
		c.pos += disp[i]
		c.part.Position = c.pos
	end
end

-- M-STEP: morphogenesis — grow / groom / reproduce
local function morph()
	local N = #cells
	local ctr = centroid()
	-- GROOM: prune undecided cells (the "cannot")
	local groomP = 0.02 + 0.06 * (N / NMAX)
	for i = #cells, 1, -1 do
		local c = cells[i]
		local maxp = math.max(c.p[1], c.p[2], c.p[3])
		if N > NMIN and maxp < 0.45 and c.age > 6 and math.random() < groomP then
			c.part:Destroy(); table.remove(cells, i)
		end
	end
	-- GROW: sprout at coherent boundary cells (the "can" — morphogenesis)
	local growP = 0.5 * (1 - #cells / NMAX)
	if growP > 0 then
		local snapshot = #cells
		for i = 1, snapshot do
			local c = cells[i]
			if c and #neighbours(i) <= 3 and math.random() < growP * 0.3 then
				local outward = c.pos - ctr
				if outward.Magnitude < 0.1 then
					outward = Vector3.new(math.random() - 0.5, 0, math.random() - 0.5)
				end
				outward = outward.Unit
				local jitter = Vector3.new(math.random() - 0.5, (math.random() - 0.5) * 0.5, math.random() - 0.5)
				local pos = c.pos + outward * SPACING + jitter * 0.7
				table.insert(cells, makeCell(pos, table.clone(c.p)))
				if #cells >= NMAX then break end
			end
		end
	end
	-- REPRODUCE: a whole, coherent body buds a peripheral cluster into a child
	if #cells > NMAX * 0.72 and math.random() < 0.05 then
		local far, fd = 1, -1
		for i, c in cells do
			local d = (c.pos - ctr).Magnitude
			if d > fd then fd = d; far = i end
		end
		local seedPos = cells[far].pos
		local kick = (seedPos - ctr).Unit * 8
		for _, c in cells do
			if (c.pos - seedPos).Magnitude < RNB * 2 then
				c.pos += kick
				c.part.Position = c.pos
			end
		end
	end
	-- never let it die
	if #cells < NMIN then
		local base = cells[1] and cells[1].pos or ORIGIN
		table.insert(cells, makeCell(base + Vector3.new(1, 0, 0.7), rndp()))
	end
end

seed()
task.spawn(function()
	local frame = 0
	while true do
		frame += 1
		relax()
		relaxPositions()
		if frame % 4 == 0 then morph() end
		task.wait(TICK)
	end
end)
print("[Critter] alive — click a cell to poke it. Cells cap at " .. NMAX .. ".")
