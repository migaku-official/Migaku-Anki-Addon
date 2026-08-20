const assert = require('assert')
const { spawn } = require('child_process')
const fs = require('fs')
const { get } = require('http')
const { tmpdir } = require('os')
const { join } = require('path')
const { createServer } = require('net')
const WebSocket = require('ws')

const { existsSync, mkdtempSync } = fs

const chromePaths = [
  process.env.CHROME_PATH,
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome',
  '/usr/bin/google-chrome-stable',
  '/usr/bin/chromium',
  '/usr/bin/chromium-browser',
  process.env.PROGRAMFILES && join(process.env.PROGRAMFILES, 'Google', 'Chrome', 'Application', 'chrome.exe'),
].filter(Boolean)

const wait = (duration) => new Promise((resolve) => setTimeout(resolve, duration))
const removeDirectory = (path) => (fs.rmSync || fs.rmdirSync)(path, { recursive: true, force: true })
const withTimeout = (promise, duration, message) => new Promise((resolve, reject) => {
  const timeout = setTimeout(() => reject(new Error(message)), duration)
  promise.then(
    (value) => {
      clearTimeout(timeout)
      resolve(value)
    },
    (error) => {
      clearTimeout(timeout)
      reject(error)
    },
  )
})
const startProcess = (command, args, options) => {
  const childProcess = spawn(command, args, options)
  const started = new Promise((resolve, reject) => {
    childProcess.once('spawn', () => resolve(childProcess))
    childProcess.once('error', reject)
  })
  return { childProcess, started }
}

const getResponse = (url) => new Promise((resolve, reject) => {
  const request = get(url, (response) => {
    const chunks = []
    response.on('data', (chunk) => chunks.push(chunk))
    response.on('end', () => resolve({
      body: Buffer.concat(chunks).toString('utf8'),
      statusCode: response.statusCode,
    }))
  })
  request.on('error', reject)
  request.setTimeout(1000, () => request.destroy(new Error(`Request timed out: ${url}`)))
})

const getAvailablePort = () => new Promise((resolve, reject) => {
  const server = createServer()
  server.once('error', reject)
  server.listen(0, '127.0.0.1', () => {
    const { port } = server.address()
    server.close(() => resolve(port))
  })
})

const waitForServer = async (url) => {
  for (const attempt of Array(100).keys()) {
    try {
      const { statusCode } = await getResponse(url)
      if (statusCode >= 200 && statusCode < 300) return
    } catch {}
    await wait(50)
  }
  throw new Error('Card preview server did not start')
}

const waitForPage = async (port, previewUrl) => {
  for (const attempt of Array(100).keys()) {
    try {
      const { body } = await getResponse(`http://127.0.0.1:${port}/json/list`)
      const pages = JSON.parse(body)
      const page = pages.find(({ type, url }) => type === 'page' && url.startsWith(previewUrl))
      if (page) return page
    } catch {}
    await wait(50)
  }
  throw new Error('Card preview did not open in headless Chrome')
}

const connect = (url) => new Promise((resolve, reject) => {
  const socket = new WebSocket(url)
  const pending = new Map()
  const state = { nextId: 0 }
  const rejectPending = (error) => {
    reject(error)
    for (const { reject: rejectRequest } of pending.values()) rejectRequest(error)
    pending.clear()
  }
  socket.on('error', rejectPending)
  socket.on('close', () => rejectPending(new Error('Chrome DevTools connection closed')))
  socket.on('message', (data) => {
    const message = JSON.parse(data)
    if (!message.id || !pending.has(message.id)) return
    const { resolve: resolveRequest, reject: rejectRequest } = pending.get(message.id)
    pending.delete(message.id)
    if (message.error) rejectRequest(new Error(message.error.message))
    else resolveRequest(message.result)
  })
  socket.on('open', () => resolve({
    close: () => socket.close(),
    send: (method, params = {}) => {
      const id = ++state.nextId
      const response = new Promise((resolveRequest, rejectRequest) => pending.set(id, { resolve: resolveRequest, reject: rejectRequest }))
      socket.send(JSON.stringify({ id, method, params }))
      return withTimeout(response, 10000, `Chrome DevTools command timed out: ${method}`).finally(() => pending.delete(id))
    },
  }))
})

const evaluate = async (client, expression) => {
  const { result, exceptionDetails } = await client.send('Runtime.evaluate', {
    expression,
    awaitPromise: true,
    returnByValue: true,
  })
  if (exceptionDetails) throw new Error(exceptionDetails.exception?.description || exceptionDetails.text)
  return result.value
}

const waitForCard = async (client) => {
  for (const attempt of Array(100).keys()) {
    const ready = await evaluate(client, `Boolean(document.querySelector('iframe')?.contentDocument?.querySelector('.migaku-card-shell > .migaku-type-toggle'))`)
    if (ready) return
    await wait(50)
  }
  const details = await evaluate(client, `(() => {
    const frame = document.querySelector('iframe')
    return { frame: Boolean(frame), src: frame?.src, body: frame?.contentDocument?.body?.innerText?.slice(0, 200) }
  })()`)
  throw new Error(`Card preview iframe did not render the type toggle: ${JSON.stringify(details)}`)
}

const getLayout = (client) => evaluate(client, `(() => {
  const frame = document.querySelector('iframe')
  const button = frame.contentDocument.querySelector('.migaku-card-shell > .migaku-type-toggle')
  const shell = frame.contentDocument.querySelector('.migaku-card-shell')
  const frameRect = frame.getBoundingClientRect()
  const buttonRect = button.getBoundingClientRect()
  const shellRect = shell.getBoundingClientRect()
  const buttonStyle = getComputedStyle(button)
  const labelStyle = getComputedStyle(button, '::after')
  const rect = ({ x, y, width, height }) => ({ x, y, width, height })
  return {
    button: rect(buttonRect),
    hovered: button.matches(':hover'),
    opacity: buttonStyle.opacity,
    buttonTypography: {
      fontFamily: buttonStyle.fontFamily,
      fontSize: buttonStyle.fontSize,
      fontWeight: buttonStyle.fontWeight,
      letterSpacing: buttonStyle.letterSpacing,
      lineHeight: buttonStyle.lineHeight,
      textDecorationLine: buttonStyle.textDecorationLine,
    },
    shell: rect(shellRect),
    label: {
      content: labelStyle.content,
      fontFamily: labelStyle.fontFamily,
      fontSize: labelStyle.fontSize,
      fontWeight: labelStyle.fontWeight,
      letterSpacing: labelStyle.letterSpacing,
      lineHeight: labelStyle.lineHeight,
      textDecorationLine: labelStyle.textDecorationLine,
    },
    hoverPoint: {
      x: frameRect.x + buttonRect.x + buttonRect.width / 2,
      y: frameRect.y + buttonRect.y + buttonRect.height / 2,
    },
  }
})()`)

const scrollToggleIntoView = (client) => evaluate(client, `document.querySelector('iframe').contentDocument.querySelector('.migaku-card-shell > .migaku-type-toggle').scrollIntoView({ block: 'center' })`)

const stopProcess = async (childProcess) => {
  if (childProcess.exitCode !== null || childProcess.signalCode !== null) return
  const exited = new Promise((resolve) => childProcess.once('exit', resolve))
  childProcess.kill('SIGTERM')
  try {
    await withTimeout(exited, 2000, 'Child process did not exit after SIGTERM')
  } catch {
    childProcess.kill('SIGKILL')
    await withTimeout(exited, 2000, 'Child process did not exit after SIGKILL')
  }
}

const assertNoHoverShift = async (client, label) => {
  await scrollToggleIntoView(client)
  await wait(150)
  await client.send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: 0, y: 0 })
  await wait(150)
  const before = await getLayout(client)
  await client.send('Input.dispatchMouseEvent', { type: 'mouseMoved', ...before.hoverPoint })
  await wait(150)
  const after = await getLayout(client)
  assert.strictEqual(after.hovered, true, `${label} hover was not activated`)
  assert.deepStrictEqual(after.button, before.button, `${label} button shifts on hover`)
  assert.deepStrictEqual(after.buttonTypography, before.buttonTypography, `${label} button typography shifts on hover`)
  assert.deepStrictEqual(after.shell, before.shell, `${label} card shell shifts on hover`)
  assert.deepStrictEqual(after.label, before.label, `${label} typography shifts on hover`)
}

const loadPreview = (client, url) => evaluate(client, `new Promise((resolve, reject) => {
  const frame = document.querySelector('iframe')
  const timeout = setTimeout(() => reject(new Error('Card preview iframe did not load')), 5000)
  frame.addEventListener('load', () => {
    clearTimeout(timeout)
    resolve()
  }, { once: true })
  frame.src = ${JSON.stringify(url)}
})`)

const assertMobileControlsHidden = async (client, previewUrl) => {
  const cardUrl = `${previewUrl}/preview?language=ja&side=back&fixture=syntax&theme=light&bridge=none`
  await client.send('Emulation.setDeviceMetricsOverride', {
    width: 390,
    height: 844,
    deviceScaleFactor: 3,
    mobile: true,
  })
  await loadPreview(client, cardUrl)
  await evaluate(client, `document.querySelector('iframe').contentDocument.fonts.ready`)
  const control = await evaluate(client, `(() => {
    const button = document.querySelector('iframe').contentDocument.querySelector('.migaku-type-toggle')
    return { hidden: button.hidden, display: getComputedStyle(button).display }
  })()`)
  assert.strictEqual(control.hidden, true, 'mobile customize-front control should be marked hidden')
  assert.strictEqual(control.display, 'none', 'mobile customize-front control should not remain visibly inert')
}

const assertMobileReadingSpacing = async (client) => {
  const metrics = await evaluate(client, `(() => {
    const cardDocument = document.querySelector('iframe').contentDocument
    const sentence = cardDocument.querySelector('.migaku-card-sentence')
    return {
      fontSize: Number.parseFloat(getComputedStyle(sentence).fontSize),
      height: sentence.getBoundingClientRect().height,
      lineHeight: Number.parseFloat(getComputedStyle(sentence).lineHeight),
      readingCount: sentence.querySelectorAll('rt').length,
    }
  })()`)
  assert.ok(metrics.readingCount > 0, 'mobile spacing fixture should contain readings')
  assert.ok(
    metrics.height <= metrics.lineHeight * 2.2,
    `mobile reading lines are excessively spaced (${metrics.height}px at ${metrics.lineHeight}px line height)`,
  )
}

const assertWebkitRubyLayout = async (client, previewUrl) => {
  await client.send('Emulation.setUserAgentOverride', {
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
  })
  await loadPreview(client, `${previewUrl}/preview?language=ja&side=back&fixture=syntax&theme=light`)
  const readings = await evaluate(client, `(() => {
    const cardDocument = document.querySelector('iframe').contentDocument
    return {
      native: cardDocument.querySelectorAll('rt').length,
      webkit: cardDocument.querySelectorAll('.migaku-webkit-ruby-reading').length,
    }
  })()`)
  assert.strictEqual(readings.native, 0, 'WebKit fallback should replace native ruby readings')
  assert.ok(readings.webkit > 0, 'WebKit fallback should render positioned ruby readings')
}

const run = async () => {
  const chromePath = chromePaths.find((path) => existsSync(path))
  if (!chromePath) {
    console.log('↷ card browser layout skipped: set CHROME_PATH to Chrome or Chromium')
    return
  }
  const serverPort = await getAvailablePort()
  const devtoolsPort = await getAvailablePort()
  const previewUrl = `http://127.0.0.1:${serverPort}`
  const profile = mkdtempSync(join(tmpdir(), 'migaku-card-hover-'))
  const previewServer = startProcess(process.execPath, ['dev/card-preview/server.js'], {
    cwd: join(__dirname, '..'),
    env: { ...process.env, CARD_PREVIEW_PORT: String(serverPort) },
    stdio: 'ignore',
  })
  try {
    await withTimeout(previewServer.started, 5000, 'Card preview server process did not start')
    await waitForServer(previewUrl)
    const chrome = startProcess(chromePath, [
      '--headless=new',
      '--disable-gpu',
      '--no-first-run',
      '--no-default-browser-check',
      `--remote-debugging-port=${devtoolsPort}`,
      `--user-data-dir=${profile}`,
      previewUrl,
    ], { stdio: 'ignore' })
    try {
      await withTimeout(chrome.started, 5000, 'Chrome process did not start')
      const page = await waitForPage(devtoolsPort, previewUrl)
      const client = await withTimeout(connect(page.webSocketDebuggerUrl), 5000, 'Chrome DevTools connection timed out')
      try {
      await client.send('Runtime.enable')
      await evaluate(client, `(() => {
        const side = document.querySelector('#side')
        side.value = 'back'
        side.dispatchEvent(new Event('change', { bubbles: true }))
      })()`)
      await waitForCard(client)
      await assertNoHoverShift(client, 'Customize front of card')
      await evaluate(client, `document.querySelector('iframe').contentDocument.querySelector('.migaku-card-shell > .migaku-type-toggle').click()`)
      await wait(150)
      await assertNoHoverShift(client, 'Dismiss')
      await assertMobileControlsHidden(client, previewUrl)
      await assertMobileReadingSpacing(client)
      await assertWebkitRubyLayout(client, previewUrl)
      } finally {
        client.close()
      }
    } finally {
      await stopProcess(chrome.childProcess)
    }
  } finally {
    try {
      await stopProcess(previewServer.childProcess)
    } finally {
      removeDirectory(profile)
    }
  }
}

run()
  .then(() => console.log('✓ card hover, mobile controls, and mobile reading spacing'))
  .catch((error) => {
    console.error(error)
    process.exitCode = 1
  })
