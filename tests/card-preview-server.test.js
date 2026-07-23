const assert = require("assert");
const http = require("http");
const path = require("path");

const { createPreviewServer } = require("../dev/card-preview/server");

const request = (port, requestPath) =>
  new Promise((resolve, reject) => {
    const req = http.get({ host: "127.0.0.1", path: requestPath, port }, (res) => {
      const chunks = [];
      res.on("data", (chunk) => chunks.push(chunk));
      res.on("end", () =>
        resolve({
          body: Buffer.concat(chunks).toString("utf8"),
          statusCode: res.statusCode,
        }),
      );
    });
    req.on("error", reject);
  });

const run = async () => {
  const server = createPreviewServer({
    rootDir: path.resolve(__dirname, ".."),
    watch: false,
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const port = server.address().port;

  const app = await request(port, "/");
  assert.strictEqual(app.statusCode, 200);
  assert.match(app.body, /Card Front-end Lab/);
  assert.match(app.body, /id="language"/);
  assert.match(app.body, /new EventSource\("\/events"\)/);

  const preview = await request(
    port,
    "/preview?language=en&side=back&theme=dark&fixture=sentence",
  );
  assert.strictEqual(preview.statusCode, 200);
  assert.match(preview.body, /data-preview-side="back"/);
  assert.match(preview.body, /Eine Sprache zu lernen/);

  const invalid = await request(
    port,
    "/preview?language=en&side=middle&theme=dark&fixture=sentence",
  );
  assert.strictEqual(invalid.statusCode, 400);
  assert.match(invalid.body, /Unknown side/);

  await new Promise((resolve) => server.close(resolve));
  console.log("✓ card preview server exposes the live development workflow");
};

run().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
