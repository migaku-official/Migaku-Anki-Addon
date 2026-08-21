const assert = require("assert");
const { execFileSync, spawnSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const repoRoot = path.join(__dirname, "..");
const outputPath = path.join(os.tmpdir(), `migaku-anki-addon-${process.pid}.ankiaddon`);

try {
  execFileSync("python3", ["tools/build_ankiaddon.py", "--output", outputPath], {
    cwd: repoRoot,
    env: { ...process.env, MIGAKU_VERSION: "9.9.9-test" },
    stdio: "pipe",
  });

  const version = execFileSync("unzip", ["-p", outputPath, "version.py"], {
    encoding: "utf8",
  });
  const entries = execFileSync("unzip", ["-Z1", outputPath], { encoding: "utf8" });

  assert.strictEqual(version, 'VERSION_STRING = "9.9.9-test"\n');
  assert.ok(entries.includes("manifest.json\n"));
  assert.doesNotMatch(entries, /(^|\/)(?:meta\.json|user_files\/|__pycache__\/|.*\.pyc$)/m);

  const placeholderBuild = spawnSync("python3", ["tools/build_ankiaddon.py", "--output", outputPath], {
    cwd: repoRoot,
    env: { ...process.env, MIGAKU_VERSION: "git" },
    encoding: "utf8",
  });
  assert.notStrictEqual(placeholderBuild.status, 0);
  assert.match(placeholderBuild.stderr, /Invalid add-on version/);
} finally {
  fs.rmSync(outputPath, { force: true });
}

console.log("✓ Anki add-on build injects a validated version and excludes development files");
