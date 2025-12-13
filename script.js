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

const character = {
  classId: null,
  level: 1,
  xp: 0,
  xpToNext: 60,
  points: 0,
  allocated: new Set(),
  selectedMap: null,
};

const creationStatus = document.getElementById("creation-status");
const pointsTag = document.getElementById("points-tag");
const levelValue = document.getElementById("level-value");
const xpValue = document.getElementById("xp-value");
const powerValue = document.getElementById("power-value");
const treeContainer = document.getElementById("tree");
const mapContainer = document.getElementById("maps");
const logContainer = document.getElementById("log");

function createCharacter() {
  const selected = document.querySelector('input[name="class"]:checked');
  if (!selected) return;

  const classId = selected.value;
  character.classId = classId;
  character.level = 1;
  character.xp = 0;
  character.xpToNext = 60;
  character.points = 1; // ponto inicial
  character.allocated = new Set([classes[classId].startNode]);

  creationStatus.textContent = `${classes[classId].label} criado. Você começa com 1 ponto e o nó inicial ativo.`;
  updateSheet();
  renderTree();
  renderMaps();
  logMessage("Personagem criado! Escolha um mapa e avance.");
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
  renderMaps();
  logMessage(`Mapa escolhido: ${maps.find((m) => m.id === mapId).name}.`);
}

function runMap() {
  if (!character.classId || !character.selectedMap) {
    logMessage("Crie um personagem e escolha um mapa.");
    return;
  }

  const map = maps.find((m) => m.id === character.selectedMap);
  const encounters = [encounterTypes[0], encounterTypes[1], encounterTypes[2], encounterTypes[3]];
  const { power } = calculateStats();

  logMessage(`Iniciando ${map.name} (dificuldade base ${map.baseDifficulty}).`);

  encounters.forEach((encounter) => {
    const enemyPower = Math.round(map.baseDifficulty * encounter.multiplier * (0.8 + Math.random() * 0.6));
    const playerRoll = Math.round(power * (0.85 + Math.random() * 0.35));

    if (playerRoll >= enemyPower) {
      logMessage(`Vitória contra inimigo ${encounter.label} (seu poder ${playerRoll} vs ${enemyPower}). +${encounter.xp} XP.`);
      gainXp(encounter.xp);
    } else {
      logMessage(`Você sofreu dano contra inimigo ${encounter.label} (seu poder ${playerRoll} vs ${enemyPower}). Tente fortalecer a árvore.`);
      // penalidade simples: perder um pouco de xp acumulado, sem reduzir nível
      character.xp = Math.max(0, character.xp - Math.round(encounter.xp / 3));
      updateSheet();
    }
  });
}

function gainXp(amount) {
  character.xp += amount;
  while (character.xp >= character.xpToNext) {
    character.xp -= character.xpToNext;
    levelUp();
  }
  updateSheet();
}

function levelUp() {
  character.level += 1;
  character.points += 1;
  character.xpToNext = Math.round(character.xpToNext * 1.15);
  logMessage(`Subiu para o nível ${character.level}! Você ganhou 1 ponto de árvore.`);
  renderTree();
}

function logMessage(message) {
  const p = document.createElement("p");
  p.textContent = message;
  logContainer.appendChild(p);
  logContainer.scrollTop = logContainer.scrollHeight;
}

// Bindings

document.getElementById("create-btn").addEventListener("click", createCharacter);
document.getElementById("run-map").addEventListener("click", runMap);

renderTree();
renderMaps();
logMessage("Crie um personagem para começar.");
