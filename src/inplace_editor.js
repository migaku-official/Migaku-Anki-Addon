$('head').append(`<link rel="stylesheet" href="${inplace_editor_css_path}" type="text/css" />`);

function encode_b64(str) {
    return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{2})/g,
        function toSolidBytes(match, p1) {
            return String.fromCharCode('0x' + p1);
    }));
}

function decode_b64(str) {
    return decodeURIComponent(atob(str).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
}

function editable_field_activated() {
    if (this.classList.contains('editable-field-active')) {
        return;
    }

    this.classList.toggle('editable-field-active');

    const content = decode_b64(this.getAttribute('data-content'));

    this.setAttribute('contenteditable', 'true');
    this.innerHTML = content;

    this.focus();
}

function editable_field_deactivated() {
    if (!this.classList.contains('editable-field-active')) {
        return;
    }

    this.setAttribute('contenteditable', 'false');
    this.classList.remove('editable-field-active');

    const is_empty = this.innerHTML.trim() === '';
    this.classList.toggle('editable-field-empty', is_empty);

    const field_name = this.getAttribute('data-field-name');

    const new_content = this.innerHTML;
    const new_content_b64 = encode_b64(new_content);
    this.setAttribute('data-content', new_content_b64);

    const should_reload =
        (this.parentElement &&                                   // Field with syntax
         this.parentElement.classList.contains('field') &&
         new_content.includes('[')) ||
        new_content.includes('[sound:') ||                       // Sound
        new_content.match(/\{\{c\d+::.*?\}\}/g);                 // Cloze

    const should_reload_str = should_reload ? 'true' : 'false';

    pycmd(`inplace-edit-submit|${field_name}|${new_content_b64}|${should_reload_str}`);
}

function editable_field_on_keydown(e) {
    if (e.ctrlKey && e.key === 'Enter') {
        e.preventDefault();
        this.blur();
    }
    else if (e.key === 'F2' || e.key == 'F4') {
        e.preventDefault();
        this.setAttribute('contenteditable', 'false');
        this.classList.remove('editable-field-active');

        const new_content = this.innerHTML;
        const new_content_b64 = encode_b64(new_content);

        const command = e.key === 'F2' ? 'inplace-edit-syntax-add' : 'inplace-edit-syntax-remove';

        const field_name = this.getAttribute('data-field-name');

        pycmd(`${command}|${field_name}|${new_content_b64}`);
    }
    else if (e.ctrlKey && e.key.toLowerCase() === 'v') {
        e.preventDefault();
        pycmd('inplace-paste');
    }
}

function init_editable_fields() {
    $('.editable-field').each(function() {
        const is_empty = this.innerHTML.trim() === '';
        this.classList.toggle('editable-field-empty', is_empty);

        this.addEventListener('dblclick', editable_field_activated);
        this.addEventListener('blur', editable_field_deactivated);
        this.addEventListener('keydown', editable_field_on_keydown);
    });
}

function inplace_pasteHTML(html, internal, ext) {
    if (!ext){
        html = html.replace(/<((?!img)[^>])+?>/g, '');
    }

    document.execCommand('inserthtml', false, html);
}
