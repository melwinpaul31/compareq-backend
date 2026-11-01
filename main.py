function selectCategory(cat) {
      activeCategory = cat;
      currentResults = [];       // Reset old search results immediately!
      currentBasketSummary = null;

      document.querySelectorAll('.cat-card').forEach(card => {
        card.className = "cat-card p-3 rounded-2xl bg-slate-900/80 border border-slate-800 text-left transition hover:border-slate-700 hover:scale-[1.02]";
      });
      const activeBtn = document.getElementById(`catBtn_${cat}`);
      if (activeBtn) {
        activeBtn.className = "cat-card p-3 rounded-2xl bg-[#b7e547]/10 border-2 border-[#b7e547] text-left transition hover:scale-[1.02]";
      }

      renderAggregatorPills();

      const singleBox = document.getElementById('singleSearchBox');
      const cabBox = document.getElementById('cabSearchBox');
      const searchTabs = document.getElementById('searchTabsBar');
      const groceryListBox = document.getElementById('groceryListBox');
      const searchInput = document.getElementById('mainSearchInput');

      if (cat === 'cabs') {
        singleBox.classList.add('hidden');
        cabBox.classList.remove('hidden');
        searchTabs.classList.add('hidden');
        groceryListBox.classList.add('hidden');
        triggerCabSearch();
      } else {
        singleBox.classList.remove('hidden');
        cabBox.classList.add('hidden');
        if (cat === 'grocery') {
          searchTabs.classList.remove('hidden');
        } else {
          searchTabs.classList.add('hidden');
          groceryListBox.classList.add('hidden');
        }
        
        const placeholders = {
          grocery: "Search milk, atta, eggs, paneer, oil... (Press Enter)",
          meat: "Search chicken, mutton, fish, prawns... (Press Enter)",
          food: "Search biryani, pizza, burger, roll... (Press Enter)",
          pharmacy: "Search dolo, paracetamol, strip... (Press Enter)",
          electronics: "Search airpods, sony tv, samsung microwave, laptop... (Press Enter)"
        };
        searchInput.placeholder = placeholders[cat] || "Search items... (Press Enter)";
        searchInput.value = '';
        renderEmptyState();
      }
    }
