/**
 * reco_tracker.js
 * À inclure dans votre base template (base.html) avant </body>
 * Envoie automatiquement les interactions implicites au serveur.
 *
 * Usage dans les templates :
 *   <div data-restaurant-id="{{ restaurant.id }}"> ... </div>
 *   <button data-clic-menu data-restaurant-id="{{ restaurant.id }}">Voir le plat</button>
 */

(function () {
  'use strict';

  const ENDPOINT = '/recommandations/interaction/';

  function getCsrfToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : '';
  }

  function envoyer(restaurantId, typeAction) {
    if (!restaurantId) return;
    fetch(ENDPOINT, {
      method:  'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken':  getCsrfToken(),
      },
      body: JSON.stringify({
        restaurant_id: parseInt(restaurantId),
        type_action:   typeAction,
      }),
    }).catch(() => {}); // silencieux en cas d'erreur réseau
  }

  // ── 1. Vue de restaurant : envoi au chargement de la page détail ────────────
  const detailEl = document.querySelector('[data-restaurant-id][data-page="detail"]');
  if (detailEl) {
    envoyer(detailEl.dataset.restaurantId, 'vue');
  }

  // ── 2. Clic sur un item menu ────────────────────────────────────────────────
  document.querySelectorAll('[data-clic-menu]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const rid = this.closest('[data-restaurant-id]')?.dataset?.restaurantId
               || this.dataset.restaurantId;
      envoyer(rid, 'clic_menu');
    });
  });

  // ── 3. Bouton partager ──────────────────────────────────────────────────────
  document.querySelectorAll('[data-partage]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const rid = this.dataset.restaurantId;
      envoyer(rid, 'partage');
    });
  });

})();
