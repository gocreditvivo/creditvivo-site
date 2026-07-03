import { existsSync } from "node:fs";
import { join, resolve } from "node:path";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";

const root = resolve(fileURLToPath(new URL("..", import.meta.url)));
const backend = join(root, "scanner_backend");
const python = existsSync(join(backend, ".venv", "Scripts", "python.exe"))
  ? join(backend, ".venv", "Scripts", "python.exe")
  : "python";

const child = spawn(
  python,
  ["-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", process.env.PORT || "8082", "--reload"],
  {
    cwd: backend,
    stdio: "inherit",
    shell: false,
    env: {
      ...process.env,
      TMP: join(backend, ".tmp"),
      TEMP: join(backend, ".tmp"),
    },
  },
);

child.on("exit", (code) => process.exit(code ?? 0));
