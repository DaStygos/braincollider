document.addEventListener("DOMContentLoaded", () => {
  const search = document.querySelector("[data-problem-search]");
  const select = document.querySelector("[data-problem-picker]");
  const count = document.querySelector("[data-problem-count]");
  if (!search || !select || !count) return;

  const options = Array.from(select.options);
  const update = () => {
    const query = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    options.forEach((option) => {
      const matches = !query || option.text.toLocaleLowerCase().includes(query);
      option.hidden = !matches && !option.selected;
      if (matches) visible += 1;
    });
    count.textContent = `${visible} problème${visible === 1 ? "" : "s"} correspondant${visible === 1 ? "" : "s"} · ${select.selectedOptions.length} sélectionné${select.selectedOptions.length === 1 ? "" : "s"}`;
  };

  search.addEventListener("input", update);
  select.addEventListener("change", update);
  update();
});
