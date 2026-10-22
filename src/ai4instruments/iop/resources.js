(() => {
  let loaded = false;
  window.refreshResources = async () => {
    if ($('#capacity').hidden) return;
    const [resources, adapters] = await Promise.all([api('resources'), api('adapters')]);
    $('#capacity-rows').replaceChildren();
    for (const item of resources.allocation) {
      const row = document.createElement('tr');
      cell(row, item.resource);
      const usage = cell(row, '');
      const meter = document.createElement('meter');
      meter.min = 0; meter.max = item.capacity; meter.value = item.used;
      meter.setAttribute('aria-label', item.resource);
      usage.append(meter, document.createTextNode(' ' + item.used));
      cell(row, item.capacity);
      $('#capacity-rows').append(row);
    }
    if (!loaded) {
      $('#capacity-definition').value = JSON.stringify(resources.capacities, null, 2);
      loaded = true;
    }
    $('#adapter-list').replaceChildren();
    for (const adapter of adapters) {
      const item = document.createElement('p');
      const name = document.createElement('strong'); name.textContent = adapter.name;
      item.append(name, document.createTextNode(' · ' + (adapter.description || adapter.package || adapter.entry_point)));
      $('#adapter-list').append(item);
    }
  };
  $('#capacity-save').onclick = async () => {
    try {
      await api('resources', { capacities: JSON.parse($('#capacity-definition').value) });
      message('资源配置已保存');
      await window.refreshResources();
    } catch (error) { message(error.message); }
  };
  document.querySelector('[data-tab="capacity"]').addEventListener('click', () => {
    window.refreshResources().catch(error => message(error.message));
  });
})();
