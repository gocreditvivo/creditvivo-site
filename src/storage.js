const fs = require("fs");
const { storage } = require("./config");

function ensureStore() {
  if (!fs.existsSync(storage.dataDir)) fs.mkdirSync(storage.dataDir, { recursive: true });
  if (!fs.existsSync(storage.leadsFile)) fs.writeFileSync(storage.leadsFile, "[]\n", { mode: 0o600 });
  [storage.workflowsFile, storage.ceoMemoryFile, storage.ceoActionsFile, storage.ceoAuditFile].forEach((file) => {
    if (!fs.existsSync(file)) fs.writeFileSync(file, "[]\n", { mode: 0o600 });
  });
}

function readJson(file, fallback = []) {
  ensureStore();
  try {
    const parsed = JSON.parse(fs.readFileSync(file, "utf8"));
    return Array.isArray(parsed) ? parsed : fallback;
  } catch {
    return fallback;
  }
}

function writeJson(file, records) {
  ensureStore();
  const tempFile = `${file}.${process.pid}.tmp`;
  fs.writeFileSync(tempFile, `${JSON.stringify(records, null, 2)}\n`, { mode: 0o600 });
  fs.renameSync(tempFile, file);
}

function readLeads() {
  return readJson(storage.leadsFile);
}

function writeLeads(leads) {
  writeJson(storage.leadsFile, leads);
}

function readWorkflows() {
  return readJson(storage.workflowsFile);
}

function writeWorkflows(workflows) {
  writeJson(storage.workflowsFile, workflows);
}

function storageDiagnostics() {
  ensureStore();
  return {
    dataDirExists: fs.existsSync(storage.dataDir),
    leadsFileExists: fs.existsSync(storage.leadsFile),
    leadsFile: storage.leadsFile,
    workflowsFileExists: fs.existsSync(storage.workflowsFile),
    workflowsFile: storage.workflowsFile,
    ceoMemoryFileExists: fs.existsSync(storage.ceoMemoryFile),
    ceoActionsFileExists: fs.existsSync(storage.ceoActionsFile),
    ceoAuditFileExists: fs.existsSync(storage.ceoAuditFile),
    leadCount: readLeads().length,
    workflowCount: readWorkflows().length,
    adapter: "local-json-atomic"
  };
}

module.exports = {
  ensureStore,
  readJson,
  writeJson,
  readLeads,
  writeLeads,
  readWorkflows,
  writeWorkflows,
  storageDiagnostics
};
