(function () {
  function addImageControls(textarea) {
    const form = textarea.form;
    if (!form) return;

    const toolbar = document.createElement('div');
    toolbar.className = 'statement-image-tools d-flex flex-wrap align-items-center gap-2 mt-2 mb-3';

    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'btn btn-sm btn-outline-secondary';
    button.innerHTML = '<i class="bi bi-image me-1" aria-hidden="true"></i>Ajouter une image';

    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/png,image/jpeg,image/webp';
    input.hidden = true;
    input.setAttribute('aria-label', 'Choisir une image à ajouter à l’énoncé');

    const status = document.createElement('span');
    status.className = 'small text-muted';
    status.setAttribute('role', 'status');
    status.setAttribute('aria-live', 'polite');
    status.textContent = 'PNG, JPEG ou WebP, 5 Mo maximum.';

    button.addEventListener('click', function () {
      input.click();
    });

    input.addEventListener('change', async function () {
      const image = input.files && input.files[0];
      if (!image) return;

      const csrfToken = form.querySelector('[name="csrfmiddlewaretoken"]');
      if (!csrfToken) {
        status.textContent = 'Rechargez la page avant d’ajouter une image.';
        return;
      }

      const payload = new FormData();
      payload.append('image', image);
      button.disabled = true;
      status.textContent = 'Chargement de l’image…';

      try {
        const response = await fetch(textarea.dataset.imageUploadUrl, {
          method: 'POST',
          headers: {
            Accept: 'application/json',
            'X-CSRFToken': csrfToken.value,
          },
          body: payload,
        });
        const result = await response.json();
        if (!response.ok) {
          throw new Error(result.error || 'Impossible de charger cette image.');
        }

        const imageMarkdown = `![Illustration](${result.url})`;
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const before = textarea.value.slice(0, start);
        const after = textarea.value.slice(end);
        const prefix = before && !before.endsWith('\n') ? '\n' : '';
        const suffix = after && !after.startsWith('\n') ? '\n' : '';
        textarea.setRangeText(`${prefix}${imageMarkdown}${suffix}`, start, end, 'end');
        textarea.dispatchEvent(new Event('input', { bubbles: true }));
        status.textContent = 'Image ajoutée à l’énoncé.';
      } catch (error) {
        status.textContent = error.message || 'Impossible de charger cette image.';
      } finally {
        button.disabled = false;
        input.value = '';
      }
    });

    toolbar.append(button, input, status);
    textarea.insertAdjacentElement('afterend', toolbar);
  }

  function initialize() {
    document.querySelectorAll('textarea[data-image-upload-url]').forEach(addImageControls);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
  } else {
    initialize();
  }
})();
