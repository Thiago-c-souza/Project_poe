const classes = {
  red: {
    name: "Vermelho",
    label: "Berserker das Brasas",
    startNode: "ember-core",
    flavor: "Início agressivo com força e dano de fogo.",
  },
  blue: {
    name: "Azul",
    label: "Teurgo da Safira",
    startNode: "sapphire-core",
    flavor: "Especialista em magia e gelo arcano.",
  },
  green: {
    name: "Verde",
    label: "Patrulheiro da Selva",
    startNode: "verdant-core",
    flavor: "Movimento veloz e venenos constantes.",
  },
};

const passiveNodes = [
  {
    id: "ember-core",
    name: "Núcleo de Brasas",
    description: "Vida + dano físico base para o início vermelho.",
    requires: [],
    effects: { vida: 20, dano: 4 },
    startFor: "red",
  },
  {
    id: "sapphire-core",
    name: "Núcleo de Safira",
    description: "Mana e dano elemental para o início azul.",
    requires: [],
    effects: { mana: 15, magia: 5 },
    startFor: "blue",
  },
  {
    id: "verdant-core",
    name: "Núcleo Esmeralda",
    description: "Velocidade e evasão para o início verde.",
    requires: [],
    effects: { agilidade: 8, evasao: 5 },
    startFor: "green",
  },
  {
    id: "steel-frame",
    name: "Armadura de Aço",
    description: "+10 de armadura e +10 de vida. Requer um núcleo inicial adjacente.",
    requires: ["ember-core", "verdant-core"],
    effects: { armadura: 10, vida: 10 },
  },
  {
    id: "glacial-control",
    name: "Controle Glacial",
    description: "+10 de magia e +8 de mana. Conecta no núcleo azul.",
    requires: ["sapphire-core"],
    effects: { magia: 10, mana: 8 },
  },
  {
    id: "venom-edge",
    name: "Lâmina Venenosa",
    description: "+6 de dano e +6 de veneno. Conecta no núcleo verde.",
    requires: ["verdant-core"],
    effects: { dano: 6, veneno: 6 },
  },
  {
    id: "flame-wheel",
    name: "Roda de Chamas",
    description: "Multiplica o dano de fogo em 10%. Requer Ember Core.",
    requires: ["ember-core"],
    effects: { danoPercent: 10 },
  },
  {
    id: "arcane-burst",
    name: "Rajada Arcana",
    description: "Multiplica magia em 12%. Requer Safira.",
    requires: ["sapphire-core"],
    effects: { magiaPercent: 12 },
  },
  {
    id: "wind-step",
    name: "Passo Vento",
    description: "Multiplica agilidade em 15%. Requer Esmeralda.",
    requires: ["verdant-core"],
    effects: { agilidadePercent: 15 },
  },
];

const maps = [
  {
    id: "ashes",
    name: "Ermos de Cinzas",
    color: "red",
    description: "Solo queimado com resquícios de guerra, favorece dano físico.",
    baseDifficulty: 11,
  },
  {
    id: "sapphire-caves",
    name: "Cavernas de Safira",
    color: "blue",
    description: "Grotas úmidas e arcanas, monstros usam magia gelada.",
    baseDifficulty: 13,
  },
  {
    id: "verdant-hollow",
    name: "Clareira Verdejante",
    color: "green",
    description: "Selva viva com venenos e emboscadas constantes.",
    baseDifficulty: 12,
  },
];

const encounterTypes = [
  { type: "normal", label: "Normal", multiplier: 1, xp: 16 },
  { type: "magic", label: "Mágico", multiplier: 1.3, xp: 24 },
  { type: "rare", label: "Raro", multiplier: 1.6, xp: 34 },
  { type: "boss", label: "Chefe", multiplier: 2.4, xp: 70 },
];

const STORAGE_KEY = "poe-characters";

const character = {
  id: null,
  name: null,
  classId: null,
  level: 1,
  xp: 0,
  xpToNext: 60,
  points: 0,
  allocated: new Set(),
  selectedMap: null,
};

let savedCharacters = [];

const creationStatus = document.getElementById("creation-status");
const savedContainer = document.getElementById("saved-characters");
const savedEmpty = document.getElementById("saved-empty");
const nameInput = document.getElementById("name-input");
const pointsTag = document.getElementById("points-tag");
const levelValue = document.getElementById("level-value");
const xpValue = document.getElementById("xp-value");
const powerValue = document.getElementById("power-value");
const treeContainer = document.getElementById("tree");
const mapContainer = document.getElementById("maps");
const logContainer = document.getElementById("log");
const overlay = document.getElementById("play-overlay");
const playArea = document.getElementById("play-area");
const playMapTitle = document.getElementById("play-map-title");
const playMapDesc = document.getElementById("play-map-desc");
const playMapLabel = document.getElementById("play-map-label");
const playEnemiesTag = document.getElementById("play-enemies-tag");
const playPowerTag = document.getElementById("play-power-tag");
const currentCharacterTag = document.getElementById("current-character-tag");

const playState = {
  active: false,
  map: null,
  grid: 12,
  player: { x: 0, y: 0 },
  enemies: [],
};

function loadCharacters() {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (!stored) return [];
  try {
    const parsed = JSON.parse(stored);
    return Array.isArray(parsed) ? parsed : [];
  } catch (error) {
    console.error("Falha ao ler banco de personagens", error);
    return [];
  }
}

function saveCharacters() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(savedCharacters));
}

function serializeCharacter(data) {
  return {
    id: data.id,
    name: data.name,
    classId: data.classId,
    level: data.level,
    xp: data.xp,
    xpToNext: data.xpToNext,
    points: data.points,
    allocated: Array.from(data.allocated),
    selectedMap: data.selectedMap || null,
  };
}

function setCharacter(data, silentLog = false) {
  character.id = data.id;
  character.name = data.name;
  character.classId = data.classId;
  character.level = data.level;
  character.xp = data.xp;
  character.xpToNext = data.xpToNext;
  character.points = data.points;
  character.selectedMap = data.selectedMap || null;
  character.allocated = new Set(data.allocated || []);

  updateSheet();
  renderTree();
  renderMaps();
  updateCurrentTag();
  document.getElementById("run-map").disabled = false;

  if (!silentLog) {
    logMessage(`Carregado personagem ${character.name} (${classes[character.classId].label}).`);
  }
}

function persistCurrentCharacter() {
  if (!character.id) return;
  const serialized = serializeCharacter(character);
  const index = savedCharacters.findIndex((c) => c.id === character.id);
  if (index >= 0) {
    savedCharacters[index] = serialized;
  } else {
    savedCharacters.push(serialized);
  }
  saveCharacters();
  renderSavedCharacters();
}

function createCharacter() {
  const selected = document.querySelector('input[name="class"]:checked');
  const name = nameInput.value.trim();
  if (!selected || !name) {
    creationStatus.textContent = "Informe um nome e escolha uma classe.";
    return;
  }

  const duplicate = savedCharacters.some((c) => c.name?.toLowerCase() === name.toLowerCase());
  if (duplicate) {
    creationStatus.textContent = "Já existe um personagem com esse nome.";
    return;
  }

  const classId = selected.value;
  const id = crypto.randomUUID();
  character.classId = classId;
  character.id = id;
  character.name = name;
  character.level = 1;
  character.xp = 0;
  character.xpToNext = 60;
  character.points = 1; // ponto inicial
  character.allocated = new Set([classes[classId].startNode]);
  character.selectedMap = null;

  const serialized = serializeCharacter(character);
  savedCharacters.push(serialized);
  saveCharacters();
  renderSavedCharacters();

  creationStatus.textContent = `${name} criado como ${classes[classId].label}. Você começa com 1 ponto e o nó inicial ativo.`;
  setCharacter(serialized, true);
  logMessage(`Personagem ${name} criado! Escolha um mapa e avance.`);
  document.getElementById("run-map").disabled = false;
}

function formatEffects(effects) {
  return Object.entries(effects)
    .map(([key, value]) => {
      const suffix = key.toLowerCase().includes("percent") ? "%" : "";
      return `${key}: +${value}${suffix}`;
    })
    .join(" · ");
}

function hasRequirements(node) {
  if (!node.requires?.length) return true;
  return node.requires.every((req) => character.allocated.has(req));
}

function renderTree() {
  treeContainer.innerHTML = "";
  passiveNodes.forEach((node) => {
    const card = document.createElement("article");
    card.className = "node";

    const header = document.createElement("header");
    const title = document.createElement("h3");
    title.textContent = node.name;
    const status = document.createElement("span");
    status.className = "tag";
    const isAllocated = character.allocated.has(node.id);
    const unlocked = hasRequirements(node);
    status.textContent = isAllocated ? "Alocado" : unlocked ? "Disponível" : "Bloqueado";
    if (unlocked) card.classList.add("unlocked");

    header.append(title, status);

    const description = document.createElement("p");
    description.className = "effects";
    description.textContent = node.description;

    const effects = document.createElement("p");
    effects.className = "effects";
    effects.textContent = formatEffects(node.effects);

    const button = document.createElement("button");
    button.textContent = isAllocated ? "Alocado" : "Comprar por 1 ponto";
    button.disabled = !unlocked || isAllocated || character.points < 1;
    button.addEventListener("click", () => allocateNode(node.id));

    card.append(header, description, effects, button);
    treeContainer.appendChild(card);
  });
}

function allocateNode(nodeId) {
  if (character.points < 1) return;
  const node = passiveNodes.find((n) => n.id === nodeId);
  if (!node || character.allocated.has(nodeId) || !hasRequirements(node)) return;
  character.points -= 1;
  character.allocated.add(nodeId);
  logMessage(`Você alocou ${node.name}.`);
  updateSheet();
  renderTree();
  persistCurrentCharacter();
}

function calculateStats() {
  const totals = { vida: 50, mana: 30, dano: 5, magia: 5, agilidade: 5, evasao: 0, armadura: 0, veneno: 0 };
  const percents = { dano: 0, magia: 0, agilidade: 0 };

  passiveNodes.forEach((node) => {
    if (character.allocated.has(node.id)) {
      Object.entries(node.effects).forEach(([key, value]) => {
        if (key.toLowerCase().includes("percent")) {
          const baseKey = key.replace("Percent", "");
          percents[baseKey] = (percents[baseKey] || 0) + value;
        } else {
          totals[key] = (totals[key] || 0) + value;
        }
      });
    }
  });

  // aplicar multiplicadores simples
  Object.entries(percents).forEach(([key, value]) => {
    if (totals[key] !== undefined) {
      totals[key] = Math.round(totals[key] * (1 + value / 100));
    }
  });

  const power = Math.round(
    totals.dano * 1.2 +
      totals.magia * 1.3 +
      totals.agilidade * 0.9 +
      totals.veneno * 0.8 +
      totals.vida * 0.1 +
      totals.armadura * 0.15
  );

  return { totals, power };
}

function updateSheet() {
  const { power } = calculateStats();
  pointsTag.textContent = `Pontos: ${character.points}`;
  levelValue.textContent = character.level;
  xpValue.textContent = `${character.xp}/${character.xpToNext}`;
  powerValue.textContent = power;
}

function renderMaps() {
  mapContainer.innerHTML = "";
  maps.forEach((map) => {
    const card = document.createElement("article");
    card.className = `map-card ${character.selectedMap === map.id ? "active" : ""}`;
    card.addEventListener("click", () => selectMap(map.id));

    const label = document.createElement("p");
    label.className = `label ${map.color}`;
    label.textContent = map.color.toUpperCase();

    const title = document.createElement("h3");
    title.textContent = map.name;

    const desc = document.createElement("p");
    desc.className = "effects";
    desc.textContent = map.description;

    card.append(label, title, desc);
    mapContainer.appendChild(card);
  });
}

function selectMap(mapId) {
  character.selectedMap = mapId;
  persistCurrentCharacter();
  renderMaps();
  logMessage(`Mapa escolhido: ${maps.find((m) => m.id === mapId).name}.`);
}

function runMap() {
  if (!character.classId || !character.selectedMap) {
    logMessage("Crie um personagem e escolha um mapa.");
    return;
  }

  const map = maps.find((m) => m.id === character.selectedMap);
  startInteractiveMap(map);
}

function gainXp(amount) {
  character.xp += amount;
  while (character.xp >= character.xpToNext) {
    character.xp -= character.xpToNext;
    levelUp();
  }
  updateSheet();
  persistCurrentCharacter();
}

function levelUp() {
  character.level += 1;
  character.points += 1;
  character.xpToNext = Math.round(character.xpToNext * 1.15);
  logMessage(`Subiu para o nível ${character.level}! Você ganhou 1 ponto de árvore.`);
  renderTree();
  persistCurrentCharacter();
}

function logMessage(message) {
  const p = document.createElement("p");
  p.textContent = message;
  logContainer.appendChild(p);
  logContainer.scrollTop = logContainer.scrollHeight;
}

function startInteractiveMap(map) {
  const { power } = calculateStats();
  playState.active = true;
  playState.map = map;
  playState.player = { x: Math.floor(playState.grid / 2), y: Math.floor(playState.grid / 2) };
  playState.enemies = spawnEnemies(map);

  playMapLabel.textContent = `Mapa: ${map.name}`;
  playMapTitle.textContent = map.name;
  playMapDesc.textContent = `${map.description} Mova-se com WASD/Setas e ataque com espaço.`;
  playPowerTag.textContent = `Poder: ${power}`;
  overlay.classList.remove("hidden");

  renderPlayfield();
  updateEnemyTag();
  logMessage(`Entrou em ${map.name}. Derrote todos os inimigos com WASD + Espaço.`);
}

function spawnEnemies(map) {
  const basePositions = new Set();
  const enemies = encounterTypes.map((encounter) => {
    let position = { x: 0, y: 0 };
    do {
      position = {
        x: Math.floor(Math.random() * playState.grid),
        y: Math.floor(Math.random() * playState.grid),
      };
    } while (basePositions.has(`${position.x},${position.y}`) || (position.x === playState.player?.x && position.y === playState.player?.y));

    basePositions.add(`${position.x},${position.y}`);
    const hp = Math.round(map.baseDifficulty * encounter.multiplier * 10);
    return {
      id: `${encounter.type}-${position.x}-${position.y}-${Date.now()}`,
      type: encounter.type,
      label: encounter.label,
      position,
      hp,
      maxHp: hp,
      xp: encounter.xp,
    };
  });
  return enemies;
}

function renderPlayfield() {
  playArea.innerHTML = "";
  const gridSize = 32;
  playArea.style.width = `${playState.grid * gridSize}px`;
  playArea.style.height = `${playState.grid * gridSize}px`;

  const bg = document.createElement("div");
  bg.className = "grid-bg";
  playArea.appendChild(bg);

  const player = document.createElement("div");
  player.className = `unit player ${character.classId}`;
  player.style.transform = `translate(${playState.player.x * gridSize + 2}px, ${playState.player.y * gridSize + 2}px)`;
  player.textContent = "P";
  playArea.appendChild(player);

  playState.enemies.forEach((enemy) => {
    const enemyEl = document.createElement("div");
    enemyEl.className = `unit enemy ${enemy.type}`;
    enemyEl.style.transform = `translate(${enemy.position.x * gridSize + 2}px, ${enemy.position.y * gridSize + 2}px)`;
    enemyEl.textContent = enemy.label[0];

    const hpBar = document.createElement("div");
    hpBar.className = "hp-bar";
    const hpFill = document.createElement("div");
    hpFill.className = "hp-fill";
    hpFill.style.width = `${Math.max(0, (enemy.hp / enemy.maxHp) * 100)}%`;
    hpBar.appendChild(hpFill);
    enemyEl.appendChild(hpBar);

    playArea.appendChild(enemyEl);
  });
}

function updateEnemyTag() {
  playEnemiesTag.textContent = `Inimigos: ${playState.enemies.length}`;
}

function handleInput(event) {
  if (!playState.active) return;
  const key = event.key.toLowerCase();
  if (["arrowup", "w"].includes(key)) {
    event.preventDefault();
    movePlayer(0, -1);
  } else if (["arrowdown", "s"].includes(key)) {
    event.preventDefault();
    movePlayer(0, 1);
  } else if (["arrowleft", "a"].includes(key)) {
    event.preventDefault();
    movePlayer(-1, 0);
  } else if (["arrowright", "d"].includes(key)) {
    event.preventDefault();
    movePlayer(1, 0);
  } else if (key === " " || key === "spacebar") {
    event.preventDefault();
    performAttack();
  }
}

function movePlayer(dx, dy) {
  const nextX = Math.min(playState.grid - 1, Math.max(0, playState.player.x + dx));
  const nextY = Math.min(playState.grid - 1, Math.max(0, playState.player.y + dy));
  playState.player = { x: nextX, y: nextY };
  renderPlayfield();
}

function performAttack() {
  if (!playState.enemies.length) {
    logMessage("Nenhum inimigo restante neste mapa.");
    return;
  }
  const { power } = calculateStats();
  const nearest = playState.enemies
    .map((enemy) => ({
      enemy,
      distance: Math.abs(enemy.position.x - playState.player.x) + Math.abs(enemy.position.y - playState.player.y),
    }))
    .sort((a, b) => a.distance - b.distance)[0];

  if (!nearest || nearest.distance > 2) {
    logMessage("Chegue mais perto do inimigo para atacar (distância máxima 2 casas).");
    return;
  }

  const damage = Math.max(4, Math.round(power * (0.35 + Math.random() * 0.25)));
  nearest.enemy.hp -= damage;
  logMessage(`Ataque contra ${nearest.enemy.label} (${nearest.enemy.type}): ${damage} de dano.`);

  if (nearest.enemy.hp <= 0) {
    logMessage(`Você derrotou um ${nearest.enemy.label}! +${nearest.enemy.xp} XP.`);
    playState.enemies = playState.enemies.filter((e) => e.id !== nearest.enemy.id);
    gainXp(nearest.enemy.xp);
    updateSheet();
  }

  renderPlayfield();
  updateEnemyTag();

  if (!playState.enemies.length) {
    finishMap();
  }
}

function finishMap() {
  logMessage(`Mapa ${playState.map.name} concluído!`);
  closeOverlay();
}

function closeOverlay() {
  overlay.classList.add("hidden");
  playState.active = false;
  playState.enemies = [];
}

function renderSavedCharacters() {
  savedContainer.innerHTML = "";
  if (!savedCharacters.length) {
    savedEmpty.style.display = "block";
    return;
  }
  savedEmpty.style.display = "none";

  savedCharacters.forEach((data) => {
    const card = document.createElement("article");
    card.className = "saved-card";

    const header = document.createElement("header");
    const title = document.createElement("h3");
    title.textContent = data.name;
    const classLabel = document.createElement("span");
    classLabel.className = `tag ${data.classId}`;
    classLabel.textContent = classes[data.classId].name;
    header.append(title, classLabel);

    const meta = document.createElement("div");
    meta.className = "meta";
    meta.textContent = `Nível ${data.level} · ${data.allocated.length} nós alocados`;

    const actions = document.createElement("div");
    actions.className = "card-actions";
    const loadBtn = document.createElement("button");
    loadBtn.className = "secondary";
    loadBtn.textContent = data.id === character.id ? "Ativo" : "Usar personagem";
    loadBtn.disabled = data.id === character.id;
    loadBtn.addEventListener("click", () => setCharacter(data));

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "ghost";
    deleteBtn.textContent = "Excluir";
    deleteBtn.addEventListener("click", () => deleteCharacter(data.id));

    actions.append(loadBtn, deleteBtn);
    card.append(header, meta, actions);
    savedContainer.appendChild(card);
  });
}

function deleteCharacter(id) {
  savedCharacters = savedCharacters.filter((c) => c.id !== id);
  saveCharacters();
  renderSavedCharacters();
  if (character.id === id) {
    resetCharacterState();
  }
}

function resetCharacterState() {
  character.id = null;
  character.name = null;
  character.classId = null;
  character.level = 1;
  character.xp = 0;
  character.xpToNext = 60;
  character.points = 0;
  character.allocated = new Set();
  character.selectedMap = null;
  creationStatus.textContent = "Nenhum personagem ativo. Crie ou carregue um.";
  updateSheet();
  renderTree();
  renderMaps();
  updateCurrentTag();
  document.getElementById("run-map").disabled = true;
}

function updateCurrentTag() {
  if (!character.id) {
    currentCharacterTag.textContent = "Nenhum personagem";
    return;
  }
  currentCharacterTag.textContent = `${character.name} · ${classes[character.classId].label}`;
}

function setupJumpButtons() {
  document.querySelectorAll("[data-jump]").forEach((button) => {
    button.addEventListener("click", () => {
      const target = document.querySelector(button.dataset.jump);
      if (target) target.scrollIntoView({ behavior: "smooth" });
    });
  });
}

// Bindings

document.getElementById("create-btn").addEventListener("click", createCharacter);
document.getElementById("run-map").addEventListener("click", runMap);
document.getElementById("close-play").addEventListener("click", closeOverlay);
document.addEventListener("keydown", handleInput);

savedCharacters = loadCharacters();
renderSavedCharacters();
setupJumpButtons();
updateCurrentTag();
renderTree();
renderMaps();
if (savedCharacters.length) {
  setCharacter(savedCharacters[0], true);
  creationStatus.textContent = "Personagem carregado do banco local.";
} else {
  creationStatus.textContent = "Crie um personagem para começar.";
  logMessage("Crie um personagem para começar.");
}
