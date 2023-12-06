var MigakuEditor = {}

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
  document.getElementById('migaku_btn_syntax_generate').style.display = 'none';
  document.getElementById('migaku_btn_syntax_remove').style.display = 'none';
}
