function fetch_text() {
    const field = getCurrentField();
    if (field) {
        return field.editable.fieldHTML;
    }
    return null;
}

function set_text(text) {
    const field = getCurrentField();
    if (field) {
        field.editable.fieldHTML = text;
    }
}
