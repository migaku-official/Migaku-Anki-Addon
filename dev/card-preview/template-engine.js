const renderSections = (template, fields) =>
  template.replace(
    /{{([#^])\s*([^{}]+?)\s*}}([\s\S]*?){{\/\s*\2\s*}}/g,
    (_, mode, fieldName, content) => {
      const hasValue = Boolean(fields[fieldName]);
      const shouldRender = mode === "#" ? hasValue : !hasValue;
      return shouldRender ? renderSections(content, fields) : "";
    },
  );

const renderFields = (template, fields) =>
  template.replace(/{{\s*([^#^/][^{}]*?)\s*}}/g, (_, expression) => {
    const fieldName = expression.split(":").pop().trim();
    return fields[fieldName] || "";
  });

const renderTemplate = (template, fields) =>
  renderFields(renderSections(template, fields), fields);

module.exports = { renderTemplate };
