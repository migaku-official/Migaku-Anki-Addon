const assert = require("assert");
const { execFileSync, spawnSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const repoRoot = path.join(__dirname, "..");
const outputPath = path.join(os.tmpdir(), `migaku-anki-addon-${process.pid}.ankiaddon`);
const distPath = path.join(repoRoot, "dist");
const resolvedDefaultOutput = execFileSync(
  "python3",
  [
    "-c",
    "from tools.build_ankiaddon import get_default_output; print(get_default_output('v9.9.9-test', '2026-08-24--1530'))",
  ],
  { cwd: repoRoot, encoding: "utf8" },
).trim();
const invalidDistOutputs = ["dist/Migaku.ankiaddon", "dist/archive/Migaku.ankiaddon"].map((output) =>
  spawnSync(
    "python3",
    [
      "-c",
      `from pathlib import Path; from tools.build_ankiaddon import get_output_path; get_output_path(Path('${output}'), '9.9.9-test', '2026-08-24--1530')`,
    ],
    { cwd: repoRoot, encoding: "utf8" },
  ),
);
const invalidBuildTimestamp = spawnSync(
  "python3",
  ["-c", "from tools.build_ankiaddon import get_default_output; get_default_output('9.9.9-test', '20260824-1530')"],
  { cwd: repoRoot, encoding: "utf8" },
);
const expectedTag = execFileSync("git", ["describe", "--tags", "--abbrev=0"], {
  cwd: repoRoot,
  encoding: "utf8",
}).trim();

try {
  assert.strictEqual(
    resolvedDefaultOutput,
    path.join(repoRoot, "dist", "Migaku-Anki-Addon-v9.9.9-test--2026-08-24--1530.ankiaddon"),
  );
  invalidDistOutputs.forEach((result) => {
    assert.notStrictEqual(result.status, 0);
    assert.match(result.stderr, /Archives written to dist must use/);
  });
  assert.notStrictEqual(invalidBuildTimestamp.status, 0);
  assert.match(invalidBuildTimestamp.stderr, /Invalid build timestamp/);

  fs.mkdirSync(path.join(distPath, "stale"), { recursive: true });
  fs.writeFileSync(path.join(distPath, "stale", "previous-build.ankiaddon"), "stale");
  execFileSync("python3", ["tools/build_ankiaddon.py", "--output", outputPath], {
    cwd: repoRoot,
    env: { ...process.env, MIGAKU_VERSION: "9.9.9-test" },
    stdio: "pipe",
  });
  assert.ok(!fs.existsSync(distPath));

  const version = execFileSync("unzip", ["-p", outputPath, "version.py"], {
    encoding: "utf8",
  });
  const entries = execFileSync("unzip", ["-Z1", outputPath], { encoding: "utf8" });

  assert.strictEqual(version, 'VERSION_STRING = "9.9.9-test"\n');
  assert.ok(entries.includes("manifest.json\n"));
  assert.doesNotMatch(entries, /(^|\/)(?:meta\.json|user_files\/|__pycache__\/|.*\.pyc$)/m);

  const localEnv = { ...process.env };
  delete localEnv.MIGAKU_VERSION;
  const localBuild = spawnSync("python3", ["tools/build_ankiaddon.py", "--output", outputPath], {
    cwd: repoRoot,
    env: localEnv,
    encoding: "utf8",
  });
  assert.strictEqual(localBuild.status, 0, localBuild.stderr);
  const localVersion = execFileSync("unzip", ["-p", outputPath, "version.py"], {
    encoding: "utf8",
  });
  assert.strictEqual(localVersion, `VERSION_STRING = "${expectedTag}"\n`);

  fs.mkdirSync(path.join(distPath, "stale"), { recursive: true });
  fs.writeFileSync(path.join(distPath, "stale", "previous-build.ankiaddon"), "stale");
  const defaultBuild = spawnSync("python3", ["tools/build_ankiaddon.py"], {
    cwd: repoRoot,
    env: { ...process.env, MIGAKU_VERSION: "v9.9.9-test" },
    encoding: "utf8",
  });
  assert.strictEqual(defaultBuild.status, 0, defaultBuild.stderr);
  const distEntries = fs.readdirSync(distPath);
  assert.strictEqual(distEntries.length, 1);
  assert.match(distEntries[0], /^Migaku-Anki-Addon-v9\.9\.9-test--\d{4}-\d{2}-\d{2}--\d{4}\.ankiaddon$/);
  assert.ok(defaultBuild.stdout.includes(distEntries[0]));

  const placeholderBuild = spawnSync("python3", ["tools/build_ankiaddon.py", "--output", outputPath], {
    cwd: repoRoot,
    env: { ...process.env, MIGAKU_VERSION: "git" },
    encoding: "utf8",
  });
  assert.notStrictEqual(placeholderBuild.status, 0);
  assert.match(placeholderBuild.stderr, /Invalid add-on version/);
} finally {
  fs.rmSync(outputPath, { force: true });
  fs.rmSync(distPath, { recursive: true, force: true });
}

console.log("✓ Anki add-on build clears dist, uses a timestamped versioned filename, and excludes development files");
