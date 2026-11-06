document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("[data-auto-apply-filters]");
  if (!form) return;

  let searchTimer;
  form.querySelectorAll("select").forEach((select) => {
    select.addEventListener("change", () => form.requestSubmit());
  });

  const search = form.querySelector('input[name="q"]');
  if (search) {
    search.addEventListener("input", () => {
      window.clearTimeout(searchTimer);
      searchTimer = window.setTimeout(() => form.requestSubmit(), 350);
    });
  }
});
