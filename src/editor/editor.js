function MigakuEditor() { }

/**
 * @param {string} add_icon_path 
 * @param {string} remove_icon_path 
 * @param {string} img_filter 
 */
MigakuEditor.initButtons = function (add_icon_path, remove_icon_path, img_filter) {
  document.querySelector('#migaku_btn_syntax_generate img').src = add_icon_path;
  document.querySelector('#migaku_btn_syntax_generate img').style.filter = img_filter;
  document.querySelector('#migaku_btn_syntax_remove img').src = remove_icon_path;
  document.querySelector('#migaku_btn_syntax_remove img').style.filter = img_filter;
  document.getElementById('migaku_btn_syntax_generate').style.display = '';
  document.getElementById('migaku_btn_syntax_remove').style.display = '';
}

MigakuEditor.hideButtons = function () {
  if (!document.getElementById('migaku_btn_syntax_generate')) setTimeout(() => {
    document.getElementById('migaku_btn_syntax_generate').style.display = 'none';
    document.getElementById('migaku_btn_syntax_remove').style.display = 'none';
  }, 100)
  else {
    document.getElementById('migaku_btn_syntax_generate').style.display = 'none';
    document.getElementById('migaku_btn_syntax_remove').style.display = 'none';
  }
}

/** These are the values on CardFields */
const selectorOptions = [
  { value: 'none', text: '(None)' },
  { value: 'sentence', text: 'Sentence' },
  { value: 'targetWord', text: 'Word' },
  { value: 'translation', text: 'Sentence Translation' },
  { value: 'sentenceAudio', text: 'Sentence Audio' },
  { value: 'wordAudio', text: 'Word Audio' },
  { value: 'images', text: 'Image' },
  { value: 'definitions', text: 'Definitions' },
  { value: 'exampleSentences', text: 'Example sentences' },
  { value: 'notes', text: 'Notes' },
]

function getSelectorField(editorField, settings) {
  const field = document.createElement('div');
  field.classList.add('migaku-field-selector');

  const select = document.createElement('select');
  select.style.margin = '2px';
  field.append(select);

  for (const option of selectorOptions) {
    const optionElement = document.createElement('option');
    optionElement.value = option.value;
    optionElement.text = option.text;
    select.append(optionElement);
  }

  const fieldContainer = editorField.parentElement.parentElement
  const labelName = fieldContainer.querySelector('.label-name').innerText
  select.value = settings[labelName] ?? 'none'

  select.addEventListener('change', (selectTarget) => {

    const cmd = `migakuSelectChange:${selectTarget.currentTarget.value}:${labelName}`
    bridgeCommand(cmd)
  })

  return field
}

const hiddenButtonCategories = [
  'settings',
  'inlineFormatting',
  'blockFormatting',
  'template',
  'cloze',
  'image-occlusion-button',
]

MigakuEditor.toggleMode = function (settings) {
  if (document.querySelector('.migaku-field-selector')) {
    resetMigakuEditor();
  } else {
    setupMigakuEditor(settings);
  }
}

// New Migaku Editor
function setupMigakuEditor(settings) {
  document.querySelectorAll('.editing-area').forEach((field) => field.style.display = 'none');
  document.querySelectorAll('.plain-text-badge').forEach((field) => field.style.display = 'none');
  document.querySelectorAll('svg#mdi-pin-outline').forEach((field) => field.parentElement.parentElement.parentElement.style.display = 'none');
  hiddenButtonCategories.forEach((category) => document.querySelector(`.item#${category}`).style.display = 'none');

  for (const field of document.querySelectorAll('.editor-field')) {
    field.append(getSelectorField(field, settings))
  }
}

function resetMigakuEditor() {
  document.querySelectorAll('.editing-area').forEach((field) => field.style.display = '');
  document.querySelectorAll('.plain-text-badge').forEach((field) => field.style.display = '');
  document.querySelectorAll('svg#mdi-pin-outline').forEach((field) => field.parentElement.parentElement.parentElement.style.display = '');
  hiddenButtonCategories.forEach((category) => document.querySelector(`.item#${category}`).style.display = '');

  document.querySelectorAll('.migaku-field-selector').forEach((selector) => selector.remove());
}
