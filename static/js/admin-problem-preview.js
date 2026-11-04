(function () {
  function addStatementPreview(textarea) {
    const preview = document.createElement('div');
    preview.className = 'admin-statement-preview';
    preview.setAttribute('aria-label', 'Aperçu de l’énoncé');
    preview.setAttribute('aria-live', 'polite');

    const toolbar = textarea.nextElementSibling;
    if (toolbar && toolbar.classList.contains('statement-image-tools')) {
      toolbar.insertAdjacentElement('afterend', preview);
    } else {
      textarea.insertAdjacentElement('afterend', preview);
    }

    function render() {
      const value = textarea.value.trim();
      const fragment = document.createDocumentFragment();
      const imagePattern = /!\[([^\]\r\n]*)\]\(([^)\s]+)\)/g;
      const mediaPath = new URL(
        textarea.dataset.mediaPrefix,
        window.location.origin,
      ).pathname;
      const imagePrefix = `${mediaPath.replace(/\/$/, '')}/problem_statement_images/`;
      let cursor = 0;
      let match;

      while ((match = imagePattern.exec(value)) !== null) {
        let imageUrl;
        try {
          imageUrl = new URL(match[2], window.location.origin);
        } catch (error) {
          continue;
        }

        const filename = imageUrl.pathname.slice(imagePrefix.length);
        if (
          imageUrl.origin !== window.location.origin
          || !imageUrl.pathname.startsWith(imagePrefix)
          || !/^[a-f0-9]{32}\.webp$/.test(filename)
          || imageUrl.search
          || imageUrl.hash
        ) {
          continue;
        }

        fragment.appendChild(document.createTextNode(value.slice(cursor, match.index)));
        const image = document.createElement('img');
        image.className = 'problem-statement-image';
        image.src = imageUrl.href;
        image.alt = match[1];
        fragment.appendChild(image);
        cursor = imagePattern.lastIndex;
      }

      fragment.appendChild(document.createTextNode(value.slice(cursor)));
      preview.replaceChildren(fragment);

      if (window.renderMathInElement) {
        window.renderMathInElement(preview, {
          delimiters: [
            { left: '$$', right: '$$', display: true },
            { left: '$', right: '$', display: false },
            { left: '\\(', right: '\\)', display: false },
            { left: '\\[', right: '\\]', display: true },
          ],
          throwOnError: false,
          strict: 'ignore',
        });
      }
    }

    textarea.addEventListener('input', render);
    textarea.addEventListener('change', render);
    render();
  }

  function initialize() {
    document
      .querySelectorAll('textarea[data-admin-statement-preview]')
      .forEach(addStatementPreview);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
  } else {
    initialize();
  }
})();
