const image = (label, color) =>
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 360" role="img" aria-label="${label}"><rect width="640" height="360" fill="${color}"/><circle cx="320" cy="150" r="72" fill="rgba(255,255,255,.72)"/><text x="320" y="274" text-anchor="middle" font-family="sans-serif" font-size="28" fill="white">${label}</text></svg>`;

const dataImage = (label, color) =>
  `data:image/svg+xml,${encodeURIComponent(image(label, color))}`;

const fixtures = {
  sentence: {
    label: "Sentence card",
    fields: {
      Definitions:
        "<ol><li>A system of communication used by a community.</li><li>The style of a piece of writing or speech.</li></ol>",
      "Example Sentences":
        "<p>Language connects people across cultures.</p><p>Her use of language is precise and warm.</p>",
      Images: `<img alt="A second fixture" src="${dataImage("Supporting image", "#f59e0b")}">`,
      "Is Audio Card": "",
      "Is Vocabulary Card": "",
      Notes:
        "<p>Fixture note: this content intentionally includes <strong>rich text</strong> and punctuation.</p>",
      Screenshot: `<img alt="A preview fixture" src="${dataImage("Screenshot fixture", "#2563eb")}">`,
      Sentence: "Learning a language opens another window onto the world.",
      "Sentence Audio": "<audio controls preload=\"none\"></audio>",
      "Target Word": "<span class=\"word\">language</span>",
      Translation:
        "Eine Sprache zu lernen öffnet ein weiteres Fenster zur Welt.",
      "Word Audio": "<audio controls preload=\"none\"></audio>",
    },
  },
  vocabulary: {
    label: "Vocabulary card",
    fields: {
      Definitions:
        "<ol><li>A word or phrase used in a particular language.</li></ol>",
      "Example Sentences": "<p>This expression appears in everyday conversation.</p>",
      Images: "",
      "Is Audio Card": "",
      "Is Vocabulary Card": "1",
      Notes: "<p>Vocabulary fixture with a deliberately concise definition.</p>",
      Screenshot: "",
      Sentence: "The expression sounds natural in this context.",
      "Sentence Audio": "",
      "Target Word": "<span class=\"word\">expression</span>",
      Translation: "Der Ausdruck klingt in diesem Kontext natürlich.",
      "Word Audio": "<audio controls preload=\"none\"></audio>",
    },
  },
  audio: {
    label: "Audio card",
    fields: {
      Definitions: "",
      "Example Sentences": "",
      Images: "",
      "Is Audio Card": "1",
      "Is Vocabulary Card": "",
      Notes: "",
      Screenshot: "",
      Sentence: "Can you understand this sentence from audio alone?",
      "Sentence Audio": "<audio controls preload=\"none\"></audio>",
      "Target Word": "",
      Translation: "Kannst du diesen Satz allein durch den Ton verstehen?",
      "Word Audio": "",
    },
  },
  stress: {
    label: "Stress test",
    fields: {
      Definitions: `<ol>${Array.from(
        { length: 8 },
        (_, index) =>
          `<li>Definition ${index + 1}: a deliberately long explanation that exercises wrapping, vertical rhythm, and overflow behavior across narrow and wide screens.</li>`,
      ).join("")}</ol>`,
      "Example Sentences": `<p>${"A long example sentence with mixed punctuation — commas, dashes, parentheses, and emphasis. ".repeat(
        5,
      )}</p>`,
      Images: Array.from(
        { length: 4 },
        (_, index) =>
          `<img alt="Stress fixture ${index + 1}" src="${dataImage(`Image ${index + 1}`, "#7c3aed")}">`,
      ).join(""),
      "Is Audio Card": "",
      "Is Vocabulary Card": "",
      Notes: `<p>${"UnbrokenContent".repeat(24)}</p>`,
      Screenshot: `<img alt="Wide stress fixture" src="${dataImage("Wide screenshot", "#0f766e")}">`,
      Sentence:
        "これは非常に長い文章です。它包含多种文字、verylongunbrokencontentthatmustwrapwithoutbreakingthelayout、そして複数の句読点。",
      "Sentence Audio": "<audio controls preload=\"none\"></audio>",
      "Target Word": "<span class=\"word\">非常に長い対象語句</span>",
      Translation:
        "This intentionally long translation verifies that the card remains readable when content grows far beyond the happy path.",
      "Word Audio": "<audio controls preload=\"none\"></audio>",
    },
  },
};

module.exports = { fixtures };
