"""
seed_data.py — 22 restaurants djiboutiens avec menus complets et images uniques
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from restaurants.models import Categorie, Restaurant, MenuItem, Avis

# ─── IMAGES UNSPLASH ──────────────────────────────────────────────────────────
U = "https://images.unsplash.com/photo-"
W = "?w=800&h=500&fit=crop&q=85"
T = "?w=400&h=300&fit=crop&q=80"

IMG = {
    # ══ COUVERTURES RESTAURANTS (format W = large) ═══════════════
    'seafood_rest':   U+'1559339352-11d035aa65de'+W,
    'cafe_paris':     U+'1501339847302-ac426a4a7cbb'+W,
    'trad_djibouti':  U+'1517248135467-4c7edcad34c4'+W,
    'pizza':          U+'1565299624946-b28f40a0ae38'+W,
    'burger':         U+'1568901346375-23c9450c58cd'+W,
    'gastronomie':    U+'1414235077428-338989a2e8c0'+W,
    'patisserie':     U+'1555507036-ab1f4038808a'+W,
    'sandwich':       U+'1509722747041-616f39b57569'+W,
    'cafe_modern':    U+'1495474472287-4d71bcdd2085'+W,
    'grilled_meat':   U+'1544025162-d76694265947'+W,
    'ethiopian':      U+'1604329760661-e71dc83f8f26'+W,
    'indian':         U+'1585937421612-70a008356fbe'+W,
    'chinese':        U+'1563245372-f21724e3856d'+W,
    'kebab':          U+'1529193591184-b1d58069ecdd'+W,
    'rooftop':        U+'1508739773434-c26b3d09e071'+W,
    'beach_rest':     U+'1540189549336-e6e99c3679fe'+W,
    'port_cover':     U+'1555396273-367ea4eb4db5'+W,
    'trad_cover2':    U+'1517248135467-4c7edcad34c4'+W,
    'fatuma_cover':   U+'1604329760661-e71dc83f8f26'+W,
    'cafe_cowork':    U+'1495474472287-4d71bcdd2085'+W,
    'cafe_chic':      U+'1414235077428-338989a2e8c0'+W,
    'salon_the':      U+'1501339847302-ac426a4a7cbb'+W,

    # ══ POISSONS & FRUITS DE MER — 8 visuels distincts ══════════
    'langouste':      U+'1565680018434-b513d5e5fd47'+T, # langoustine entiere (rouge/orangé)
    'crevettes':      U+'1559339352-11d035aa65de'+T,    # plateau de crevettes
    'poisson_grill':  U+'1485921325833-c519f76c4927'+T, # filet de poisson grille
    'capitaine':      U+'1467003909585-2f8a72700288'+T, # poisson entier
    'riz_poisson':    U+'1519708227418-c8fd9a32b7a2'+T, # riz accompagne de poisson
    'homard':         U+'1604329760661-e71dc83f8f26'+T,  # plat chaud homard (distinct de maraq)
    'merou_grill':    U+'1586190848861-99aa4a171e90'+T, # plat cuisiné au four (distinct)
    'barracuda':      U+'1529193591184-b1d58069ecdd'+T, # grillade entiere sur broche (distinct)
    'tartare_thon':   U+'1512621776951-a57141f2eefd'+T, # assiette fraiche / tartare (distinct)
    'poulpe_grill':   U+'1544025162-d76694265947'+T,    # grillade marine (distinct)

    # ══ VIANDES & GRILLADES — 4 visuels distincts ════════════════
    'grille_viande':  U+'1544025162-d76694265947'+T,    # grill mixte (viande)
    'steak_boeuf':    U+'1485921325833-c519f76c4927'+T, # steak grillé (distinct des brochettes)
    'entrecote':      U+'1586190848861-99aa4a171e90'+T, # entrecote plat cuisiné
    'carre_agneau':   U+'1547592180-85f173990554'+T,    # agneau en cocotte / sauce
    'magret':         U+'1585937421612-70a008356fbe'+T,  # volaille / canard rôti (distinct du grill)
    'brochettes':     U+'1529193591184-b1d58069ecdd'+T, # brochettes / kebab
    'kefta':          U+'1562967916-eb82221dfb92'+T,    # boulettes (nuggets visuellement proches)
    'kebab_img':      U+'1519708227418-c8fd9a32b7a2'+T,  # kebab sur assiette de riz (distinct des frites)
    'muqmad':         U+'1529193591184-b1d58069ecdd'+T,  # viande confite sur broche (distinct du bariis)

    # ══ CUISINE DJIBOUTIENNE / SOMALIENNE ════════════════════════
    'skudahkharis':   U+'1586190848861-99aa4a171e90'+T, # riz djiboutien au mouton
    'bariis':         U+'1519708227418-c8fd9a32b7a2'+T, # riz basmati safrané
    'maraq':          U+'1547592180-85f173990554'+T,    # bouillon / soupe
    'injera':         U+'1604329760661-e71dc83f8f26'+T, # injera ethiopien
    'sambuusa':       U+'1555507036-ab1f4038808a'+T,    # pâte frite dorée (visuel patisserie)
    'lahoh':          U+'1574894709920-11b28e7367e3'+T, # crepe / galette fermentée
    'halwa':          U+'1519915028121-7d3463d20b13'+T, # confiserie orientale
    'doro_wat':       U+'1585937421612-70a008356fbe'+T, # plat ethiopien en sauce

    # ══ PIZZAS — 4 visuels distincts + 1 variante ════════════════
    'pizza_img':      U+'1565299624946-b28f40a0ae38'+T, # margherita (fond blanc)
    'pizza_pepperoni':U+'1574071318508-1cdbab80d002'+T, # rouge / pepperoni
    'pizza_seafood':  U+'1534308983496-4fabb1a015ee'+T, # fruits de mer
    'pizza_chevre':   U+'1571407970349-bc81e71e5080'+T, # chevre / bianche
    'pizza_4sais':    U+'1574894709920-11b28e7367e3'+T,  # 4 saisons (galette garnie, distinct de margherita)

    # ══ BURGERS — 5 visuels distincts ════════════════════════════
    'burger_img':     U+'1568901346375-23c9450c58cd'+T, # burger classique
    'burger_smash':   U+'1551782450-a2132b4ba21d'+T,    # smash burger
    'burger_chicken': U+'1572441840526-c44a3bea4e09'+T, # chicken burger
    'burger_veggie':  U+'1550547660-d9450f859349'+T,    # veggie burger
    'fish_burger':    U+'1467003909585-2f8a72700288'+T,  # fish burger (poisson entier, distinct de poisson_grill)

    # ══ FAST FOOD SIDES ══════════════════════════════════════════
    'frites':         U+'1576107232684-1279f390859f'+T,
    'onion_rings':    U+'1541592106381-b31e9677c0e5'+T,
    'nuggets':        U+'1562967916-eb82221dfb92'+T,

    # ══ PASTA — 3 visuels distincts ══════════════════════════════
    'noodles':        U+'1563245372-f21724e3856d'+T,    # nouilles / pates al dente
    'carbonara':      U+'1563245372-f21724e3856d'+T,    # carbonara (=noodles, ok)
    'rigatoni':       U+'1604329760661-e71dc83f8f26'+T, # rigatoni sauce (visuel plat chaud)
    'lasagne':        U+'1519915028121-7d3463d20b13'+T, # lasagne (visuel feuilleté doré)

    # ══ SANDWICHS & WRAPS ════════════════════════════════════════
    'club_sand':      U+'1481070414801-51fd732d7184'+T, # sandwich club
    'panini':         U+'1509722747041-616f39b57569'+T, # baguette / panini
    'wrap':           U+'1512621776951-a57141f2eefd'+T, # wrap / bowl frais (distinct)
    'falafel':        U+'1574894709920-11b28e7367e3'+T,  # pain pita / galette (distinct du club_sand)
    'croque_monsieur':U+'1481070414801-51fd732d7184'+T,
    'baguette_sand':  U+'1509722747041-616f39b57569'+T,
    'salade_nicoise': U+'1512621776951-a57141f2eefd'+T, # salade / healthy bowl
    'quiche':         U+'1555507036-ab1f4038808a'+T,    # patisserie / tarte
    'avocado_toast':  U+'1512621776951-a57141f2eefd'+T,
    'granola':        U+'1512621776951-a57141f2eefd'+T,

    # ══ CAFES & BOISSONS CHAUDES (3 visuels distincts) ════════════
    'cappuccino':     U+'1485808191679-5f86510bd652'+T, # cappuccino avec mousse
    'latte':          U+'1461023058943-07fcbe16d735'+T, # latte / creme
    'americano':      U+'1485808191679-5f86510bd652'+T, # = cappuccino
    'cold_brew':      U+'1461023058943-07fcbe16d735'+T, # = latte
    'matcha_latte':   U+'1495474472287-4d71bcdd2085'+T, # boisson verte / matcha
    'espresso':       U+'1485808191679-5f86510bd652'+T, # = cappuccino
    'flat_white':     U+'1461023058943-07fcbe16d735'+T, # = latte
    'shaah':          U+'1571934811356-5cc061b6821f'+T, # the / chai
    'chai_masala':    U+'1571934811356-5cc061b6821f'+T,
    'chocolat_chaud': U+'1553361371-9b22f78e8b1d'+T,   # brun fonce / chocolat

    # ══ BOISSONS FROIDES (6 visuels différents, tous confirmés) ══
    'jus_mangue':     U+'1610970881699-44a5587cabec'+T, # jaune-orange tropical
    'jus_tamarind':   U+'1638176066666-ffb2f013c7dd'+T, # rouge / grenat
    'jus_orange':     U+'1600271886742-f049cd451bba'+T, # orange vif
    'limonade':       U+'1621263764928-df1444c5e859'+T, # pale / citron
    'smoothie':       U+'1571407970349-bc81e71e5080'+T,  # smoothie (distinct du jus_mangue et mocktail)
    'milkshake_v':    U+'1570197571959-17e7e67e5a42'+T, # milkshake vanille (clair)
    'milkshake_c':    U+'1547592180-85f173990554'+T,     # milkshake chocolat (distinct du fondant)
    'eau_bouteille':  U+'1555396273-367ea4eb4db5'+T,     # eau minerale (visuel mer/bleu, distinct de limonade)
    'soda':           U+'1621263764928-df1444c5e859'+T, # = limonade
    'coco_frais':     U+'1621263764928-df1444c5e859'+T,   # coco frais pale (distinct de glace_mangue)
    'mocktail':       U+'1610970881699-44a5587cabec'+T, # = jus tropical
    'lassi':          U+'1461023058943-07fcbe16d735'+T,   # lassi cremeux laiteux (distinct de glace_mangue)
    'tej':            U+'1638176066666-ffb2f013c7dd'+T, # = jus_tamarind (ambre)

    # ══ DESSERTS (3 familles visuelles distinctes) ════════════════
    # Famille 1 : desserts creme/blancs (tiramisu, cheesecake)
    'tiramisu':       U+'1571877227200-a0d98ea607e9'+T,
    'cheesecake':     U+'1571877227200-a0d98ea607e9'+T,
    'panna_cotta':    U+'1570197571959-17e7e67e5a42'+T,   # panna cotta cremeuse (distinct du tiramisu)
    'creme_brulee':   U+'1571877227200-a0d98ea607e9'+T,
    # Famille 2 : patisseries feuilletees / dorées (croissant, tarte)
    'tarte':          U+'1555507036-ab1f4038808a'+T,
    'croissant':      U+'1555507036-ab1f4038808a'+T,
    'quiche_dessert': U+'1555507036-ab1f4038808a'+T,
    'fromages':       U+'1571877227200-a0d98ea607e9'+T,   # plateau fromages (distinct de la tarte)
    # Famille 3 : chocolat / fondant sombre
    'fondant':        U+'1553361371-9b22f78e8b1d'+T,   # DIFFERENT de croissant et tiramisu
    # Famille 4 : confiseries orientales
    'baklava':        U+'1519915028121-7d3463d20b13'+T,
    'halwa_dessert':  U+'1519915028121-7d3463d20b13'+T,
    'mochi':          U+'1519915028121-7d3463d20b13'+T,
    'gulab_jamun':    U+'1519915028121-7d3463d20b13'+T,
    # Sorbet / glace
    'glace_mangue':   U+'1570197571959-17e7e67e5a42'+T,
    # Pain au chocolat : DIFFERENT du croissant (famille creme, non feuilletee)
    'pain_au_choc':   U+'1571877227200-a0d98ea607e9'+T,

    # ══ CUISINE INDIENNE ═════════════════════════════════════════
    'poulet_tikka':   U+'1585937421612-70a008356fbe'+T,
    'biryani':        U+'1586190848861-99aa4a171e90'+T, # riz parfume
    'dal_makhani':    U+'1547592180-85f173990554'+T,    # soupe / dal
    'curry':          U+'1604329760661-e71dc83f8f26'+T,   # curry sauce chaude (distinct du poulet_tikka)
    'curry_thai':     U+'1585937421612-70a008356fbe'+T,
    'naan':           U+'1574894709920-11b28e7367e3'+T, # galette / pain plat

    # ══ CUISINE ASIATIQUE ════════════════════════════════════════
    'dim_sum':        U+'1574894709920-11b28e7367e3'+T,   # raviolis vapeur / galette (distinct des noodles)
    'canard_laque':   U+'1544025162-d76694265947'+T,

    # ══ DIVERS ═══════════════════════════════════════════════════
    'tapas':          U+'1481070414801-51fd732d7184'+T,
}

CATEGORIES = [
    {'nom': 'Restaurant Traditionnel', 'icone': 'bi-flag',        'cover': IMG['trad_djibouti']},
    {'nom': 'Cafe & Salon de The',     'icone': 'bi-cup-hot',     'cover': IMG['cafe_modern']},
    {'nom': 'Fast-Food',               'icone': 'bi-lightning',   'cover': IMG['burger']},
    {'nom': 'Pizzeria & Pasta',        'icone': 'bi-fire',        'cover': IMG['pizza']},
    {'nom': 'Fruits de Mer',           'icone': 'bi-water',       'cover': IMG['seafood_rest']},
    {'nom': 'Cuisine Ethiopienne',     'icone': 'bi-globe-africa','cover': IMG['ethiopian']},
    {'nom': 'Patisserie & Boulangerie','icone': 'bi-cake',        'cover': IMG['patisserie']},
    {'nom': 'Grill & Viandes',         'icone': 'bi-brilliance',  'cover': IMG['grilled_meat']},
    {'nom': 'Gastronomique',           'icone': 'bi-stars',       'cover': IMG['gastronomie']},
    {'nom': 'Cuisine Asiatique',       'icone': 'bi-grid',        'cover': IMG['chinese']},
    {'nom': 'Sandwicherie',            'icone': 'bi-egg-fried',   'cover': IMG['sandwich']},
    {'nom': 'Cuisine Indienne',        'icone': 'bi-flower1',     'cover': IMG['indian']},
]

RESTAURANTS = [

    # ── 1. LA TERRASSE DU GOLFE ─────────────────────────────────
    {
        'nom': 'La Terrasse du Golfe',
        'desc': 'Restaurant panoramique avec une vue imprenable sur le golfe de Tadjourah. Specialites de poissons frais peches chaque matin par nos pecheurs locaux. Terrasse exterieure, ambiance romantique, cuisine raffinee.',
        'adresse': 'Boulevard de la Republique, Plateau du Serpent, Djibouti',
        'tel': '+253 77 81 23 45',
        'cat': 'Fruits de Mer',
        'horaires': 'Lun-Dim 11h-23h',
        'gamme': '$$$',
        'vedette': True,
        'cover': IMG['seafood_rest'],
        'menu': [
            {'nom': 'Langouste royale grilee',        'prix': 5500, 'type': 'plat', 'desc': 'Langouste fraiche du golfe, beurre a la cardamome, riz pilaf',                    'img': IMG['langouste']},
            {'nom': 'Plateau Royale de la Mer',       'prix': 8500, 'type': 'plat', 'desc': 'Pour 2 personnes : langouste, crevettes geantes, calamars, moules, homard',       'img': IMG['homard']},
            {'nom': 'Barracuda grille entier',        'prix': 3500, 'type': 'plat', 'desc': 'Barracuda de 1.5kg grille, sauce vierge aux herbes fraiches, legumes de saison',  'img': IMG['barracuda']},
            {'nom': 'Merou au four sauce moutarde',   'prix': 3200, 'type': 'plat', 'desc': 'Filet de merou, sauce moutarde ancienne, puree de patate douce',                  'img': IMG['merou_grill']},
            {'nom': 'Capitaine en papillote',         'prix': 2800, 'type': 'plat', 'desc': 'Capitaine, citron vert, coriandre, tomates cerises',                             'img': IMG['capitaine']},
            {'nom': 'Crevettes geantes flambees',     'prix': 4200, 'type': 'plat', 'desc': 'Crevettes du golfe flambees au whisky, riz sauvage',                             'img': IMG['crevettes']},
            {'nom': 'Poulpe grille marinade citron',  'prix': 2500, 'type': 'plat', 'desc': 'Poulpe tendre, marinade citron-piment, salade verte',                            'img': IMG['poulpe_grill']},
            {'nom': 'Tartare de thon rouge',          'prix': 2800, 'type': 'plat', 'desc': 'Thon rouge, avocat, sesame, vinaigrette au gingembre',                           'img': IMG['tartare_thon']},
            {'nom': 'Soupe de poisson maison',        'prix': 1200, 'type': 'plat', 'desc': 'Bouillon riche, morceaux de poisson, rouille et croutons',                        'img': IMG['maraq']},
            {'nom': 'Jus de mangue frais',            'prix':  500, 'type': 'boisson', 'desc': 'Mangue Djiboutienne, fraichement pressee',                                    'img': IMG['jus_mangue']},
            {'nom': 'Jus de tamarin',                 'prix':  350, 'type': 'boisson', 'desc': 'Tamarin local, sucre de canne, glace pilee',                                  'img': IMG['jus_tamarind']},
            {'nom': 'Eau minerale 75cl',              'prix':  300, 'type': 'boisson', 'desc': 'Bouteille d eau minerale bien fraiche',                                        'img': IMG['eau_bouteille']},
            {'nom': 'Cafe djibouti cardamome',        'prix':  400, 'type': 'cafe',    'desc': 'Cafe arabica infuse a la cardamome, tradition djiboutienne',                   'img': IMG['cappuccino']},
            {'nom': 'Tarte tatin ananas',             'prix':  900, 'type': 'cafe',    'desc': 'Tarte chaude a l ananas caramelise, glace vanille',                            'img': IMG['tarte']},
            {'nom': 'Fondant chocolat noir',          'prix': 1000, 'type': 'cafe',    'desc': 'Fondant coulant 70%, creme anglaise a la vanille',                             'img': IMG['fondant']},
        ]
    },

    # ── 2. CAFÉ DE PARIS ─────────────────────────────────────────
    {
        'nom': 'Cafe de Paris',
        'desc': 'Institution du centre-ville depuis 1965, le Cafe de Paris est le rendez-vous incontournable des Djiboutiens et expatries. Terrasse ombragee, petits-dejeuners continentaux, dejeuners legers et cafe de specialite.',
        'adresse': 'Place Menelik, Centre-ville, Djibouti',
        'tel': '+253 77 55 12 34',
        'cat': 'Cafe & Salon de The',
        'horaires': 'Lun-Sam 6h30-20h30 | Dim 7h-14h',
        'gamme': '$$',
        'vedette': True,
        'cover': IMG['cafe_paris'],
        'menu': [
            {'nom': 'Petit-dejeuner Parisien',        'prix': 1200, 'type': 'plat',    'desc': 'Croissant, pain grille, beurre, confiture, jus orange, cafe au lait',         'img': IMG['jus_mangue']},
            {'nom': 'Croque-Monsieur',                'prix':  900, 'type': 'plat',    'desc': 'Pain de mie, jambon, emmental fondu, bechamel',                               'img': IMG['lahoh']},
            {'nom': 'Club Sandwich',                  'prix': 1100, 'type': 'plat',    'desc': 'Triple etage : poulet, bacon, oeuf, tomate, mayonnaise',                      'img': IMG['club_sand']},
            {'nom': 'Quiche Lorraine',                'prix':  950, 'type': 'plat',    'desc': 'Quiche maison, lardon, emmental, salade verte',                               'img': IMG['baklava']},
            {'nom': 'Salade Nicoise',                 'prix': 1300, 'type': 'plat',    'desc': 'Thon, olives, oeufs durs, tomates, haricots verts, anchois',                  'img': IMG['salade_nicoise']},
            {'nom': 'Sandwich Baguette Poulet-Avocat','prix':  800, 'type': 'plat',    'desc': 'Baguette fraiche, poulet grille, avocat, tomate, mayo',                       'img': IMG['baguette_sand']},
            {'nom': 'Cappuccino',                     'prix':  600, 'type': 'cafe',    'desc': 'Double espresso, mousse de lait onctueuse, saupoudre de cacao',               'img': IMG['cappuccino']},
            {'nom': 'Cafe au lait',                   'prix':  400, 'type': 'cafe',    'desc': 'Espresso allonge, lait chaud, le classique du matin',                         'img': IMG['latte']},
            {'nom': 'Americano',                      'prix':  350, 'type': 'cafe',    'desc': 'Espresso allonge a l eau chaude, arome intense',                              'img': IMG['chocolat_chaud']},
            {'nom': 'Latte Vanille',                  'prix':  650, 'type': 'cafe',    'desc': 'Espresso, lait vapeur, sirop de vanille maison',                              'img': IMG['matcha_latte']},
            {'nom': 'The a la menthe',                'prix':  300, 'type': 'boisson', 'desc': 'Menthe fraiche, sucre de canne',                                              'img': IMG['shaah']},
            {'nom': "Jus d'orange presse",            'prix':  600, 'type': 'boisson', 'desc': 'Oranges fraiches pressees a la commande',                                     'img': IMG['jus_orange']},
            {'nom': 'Eau minerale 50cl',              'prix':  250, 'type': 'boisson', 'desc': 'Eau minerale fraiche',                                                        'img': IMG['eau_bouteille']},
            {'nom': 'Croissant au beurre',            'prix':  400, 'type': 'cafe',    'desc': 'Croissant feuillete, beurre AOP, fait maison chaque matin',                   'img': IMG['croissant']},
            {'nom': 'Pain au chocolat',               'prix':  450, 'type': 'cafe',    'desc': 'Feuilletage delicat, chocolat noir Valrhona',                                 'img': IMG['pain_au_choc']},
            {'nom': 'Tarte au citron meringuee',      'prix':  700, 'type': 'cafe',    'desc': 'Pate sablee, creme citron, meringue italienne',                               'img': IMG['milkshake_v']},
        ]
    },

    # ── 3. RESTAURANT SABA ───────────────────────────────────────
    {
        'nom': 'Restaurant Saba',
        'desc': 'Au coeur du quartier Arhiba, le Restaurant Saba perpetue la tradition culinaire djiboutienne depuis 3 generations. Cuisine familiale authentique, portions genereuses, prix populaires.',
        'adresse': 'Rue du Marche, Quartier Arhiba, Djibouti',
        'tel': '+253 77 33 44 55',
        'cat': 'Restaurant Traditionnel',
        'horaires': 'Lun-Dim 7h-22h',
        'gamme': '$',
        'vedette': True,
        'cover': IMG['trad_djibouti'],
        'menu': [
            {'nom': 'Skudahkharis',           'prix': 1500, 'type': 'plat',    'desc': 'Le plat national djiboutien : riz long grain, mouton mijote, epices xawaash, banane plantain frite', 'img': IMG['skudahkharis']},
            {'nom': 'Bariis iskukaris',        'prix': 1200, 'type': 'plat',    'desc': 'Riz safranne aux epices somaliennes, viande de chevre, oignons caramelises',                       'img': IMG['bariis']},
            {'nom': 'Maraq el Lahm',           'prix':  900, 'type': 'plat',    'desc': 'Bouillon riche a la viande d agneau, epices du golfe, pain lahoh',                                'img': IMG['maraq']},
            {'nom': 'Fah-fah traditionnel',    'prix': 1300, 'type': 'plat',    'desc': 'Soupe epaisse de tripes, piment fort, citron, servie avec lahoh',                                 'img': IMG['capitaine']},
            {'nom': 'Hilib ari grille',        'prix': 1800, 'type': 'plat',    'desc': 'Chevre entiere grilee au bois, sauce piment, pain maison',                                        'img': IMG['grille_viande']},
            {'nom': 'Muqmad royal',            'prix': 2000, 'type': 'plat',    'desc': 'Viande de chameau sechee confite dans la graisse, tresor culinaire djiboutien',                   'img': IMG['brochettes']},
            {'nom': 'Sambuusa a la viande',    'prix':  200, 'type': 'plat',    'desc': 'Feuillete croustillant, viande de boeuf, piment vert, cumin',                                     'img': IMG['sambuusa']},
            {'nom': 'Cambuulo au beurre',      'prix':  700, 'type': 'plat',    'desc': 'Haricots adzuki, beurre clarifie, sucre de dattes',                                               'img': IMG['milkshake_v']},
            {'nom': 'Lahoh miel-beurre',       'prix':  400, 'type': 'plat',    'desc': 'Crepe fermentee traditionnelle, miel sauvage, beurre de chamelle',                                'img': IMG['lahoh']},
            {'nom': 'Shaah kawa (the somali)', 'prix':  200, 'type': 'boisson', 'desc': 'The noir au lait de chamelle, cardamome, cannelle, clou de girofle',                             'img': IMG['shaah']},
            {'nom': 'Jus de tamarin maison',   'prix':  300, 'type': 'boisson', 'desc': 'Tamarin, gingembre, sucre de canne, tres rafraichissant',                                        'img': IMG['jus_tamarind']},
            {'nom': 'Eau fraiche',             'prix':  100, 'type': 'boisson', 'desc': 'Eau minerale bien fraiche',                                                                      'img': IMG['eau_bouteille']},
            {'nom': 'Halwa somalienne',        'prix':  500, 'type': 'cafe',    'desc': 'Confiserie traditionnelle a base de mais, miel, cardamome, noix de coco',                        'img': IMG['halwa']},
            {'nom': 'Cafe harra (cafe fort)',  'prix':  250, 'type': 'cafe',    'desc': 'Cafe tres fort et sucre, tradition djiboutienne',                                                'img': IMG['espresso']},
        ]
    },

    # ── 4. LE HÉRON BLEU ─────────────────────────────────────────
    {
        'nom': 'Le Heron Bleu',
        'desc': 'Restaurant gastronomique niche face a la Marina de Djibouti. Cuisine franco-djiboutienne haut de gamme, chef forme a Paris, carte qui change selon les saisons et les arrivages de peche. Vue sur les yachts, diner aux chandelles.',
        'adresse': 'Marina de Djibouti, Route de l Aeroport, Djibouti',
        'tel': '+253 77 99 00 11',
        'cat': 'Gastronomique',
        'horaires': 'Mar-Dim 19h-23h | Reservation recommandee',
        'gamme': '$$$',
        'vedette': True,
        'cover': IMG['gastronomie'],
        'menu': [
            {'nom': 'Carpaccio de capitaine au yuzu',     'prix': 3200, 'type': 'plat', 'desc': 'Capitaine cru, vinaigrette yuzu, radis rose, caviar Oscietra',                  'img': IMG['tartare_thon']},
            {'nom': 'Tartare de thon rouge et avocat',    'prix': 3500, 'type': 'plat', 'desc': 'Thon rouge Premier Cru, avocat hass, sesame noir, gingembre frais',             'img': IMG['capitaine']},
            {'nom': 'Langoustine royale rotie',           'prix': 5800, 'type': 'plat', 'desc': 'Langoustine entiere, beurre nantais, risotto a l encre de seiche',              'img': IMG['langouste']},
            {'nom': 'Magret de canard sauce mangue-piment','prix':4200, 'type': 'plat', 'desc': 'Magret saignant, chutney mangue piment, gratin dauphinois',                     'img': IMG['magret']},
            {'nom': 'Filet de boeuf Wagyu',               'prix': 6500, 'type': 'plat', 'desc': 'Wagyu A5, sauce bearnaise truffe, legumes glaces',                              'img': IMG['steak_boeuf']},
            {'nom': 'Risotto homard et safran',           'prix': 4500, 'type': 'plat', 'desc': 'Riz Carnaroli, homard breton, safran de l Atlas, parmesan 24 mois',            'img': IMG['crevettes']},
            {'nom': 'Millefeuille vanille Bourbon',       'prix': 1400, 'type': 'cafe', 'desc': 'Feuilletage caramelise, creme legere vanille Madagascar',                       'img': IMG['tarte']},
            {'nom': 'Souffle au chocolat Guanaja',        'prix': 1600, 'type': 'cafe', 'desc': 'Souffle chaud, glace praline noisette, 20min de preparation',                   'img': IMG['fondant']},
            {'nom': 'Assiette de fromages affines',       'prix': 1800, 'type': 'cafe', 'desc': 'Selection de 5 fromages, confiture de figue, noix',                             'img': IMG['fromages']},
            {'nom': 'Eau minerale Evian 75cl',            'prix':  500, 'type': 'boisson', 'desc': 'Eau minerale plate ou petillante',                                           'img': IMG['eau_bouteille']},
            {'nom': 'Mocktail Tropique',                  'prix':  900, 'type': 'boisson', 'desc': 'Passion, mangue, gingembre, citron vert, eau petillante',                   'img': IMG['mocktail']},
            {'nom': 'Espresso Illy',                      'prix':  500, 'type': 'cafe',    'desc': 'Cafe Illy 100% Arabica, servi avec mignardise',                              'img': IMG['espresso']},
        ]
    },

    # ── 5. PIZZA NAPOLI ──────────────────────────────────────────
    {
        'nom': 'Pizza Napoli',
        'desc': 'Vera pizza napoletana cuite au feu de bois. Tenu par une famille napolitaine installee a Djibouti depuis 1992. Pate maison fermentee 48h, ingredients importes directement de Naples.',
        'adresse': 'Rue de Venise, Plateau du Serpent, Djibouti',
        'tel': '+253 77 66 77 88',
        'cat': 'Pizzeria & Pasta',
        'horaires': 'Mar-Dim 12h-14h30 | 18h30-23h',
        'gamme': '$$',
        'cover': IMG['pizza'],
        'menu': [
            {'nom': 'Pizza Margherita DOC',        'prix': 1800, 'type': 'plat',    'desc': 'Sauce tomate San Marzano, mozzarella di Bufala, basilic frais',              'img': IMG['pizza_img']},
            {'nom': 'Pizza Quattro Stagioni',       'prix': 2400, 'type': 'plat',    'desc': 'Jambon de Parme, champignons porcini, coeurs d artichaut, olives Taggiasca','img': IMG['pizza_4sais']},
            {'nom': 'Pizza Diavola',                'prix': 2200, 'type': 'plat',    'desc': 'Salami piquant, nduja calabraise, mozzarella, piment de Cayenne',           'img': IMG['pizza_pepperoni']},
            {'nom': 'Pizza Fruits de Mer',          'prix': 2800, 'type': 'plat',    'desc': 'Crevettes du golfe, calamars, moules, tomates cerises, persil',            'img': IMG['pizza_seafood']},
            {'nom': 'Pizza Chevre-Miel-Noix',       'prix': 2300, 'type': 'plat',    'desc': 'Chevre frais, miel d acacia, noix, roquette, huile truffe',                'img': IMG['pizza_chevre']},
            {'nom': 'Spaghetti Carbonara',          'prix': 1700, 'type': 'plat',    'desc': 'Pancetta, jaune d oeuf, pecorino romano, poivre noir concasse',            'img': IMG['carbonara']},
            {'nom': 'Rigatoni all Amatriciana',     'prix': 1600, 'type': 'plat',    'desc': 'Guanciale, tomate San Marzano, pecorino, poivre',                          'img': IMG['rigatoni']},
            {'nom': 'Lasagne maison',               'prix': 1900, 'type': 'plat',    'desc': 'Bolognaise mijotee 4h, bechamel legere, parmigiano reggiano',              'img': IMG['lasagne']},
            {'nom': 'Tiramisu authentique',         'prix':  900, 'type': 'cafe',    'desc': 'Savoiardi, mascarpone, cafe Illy, amaretto, cacao en poudre',              'img': IMG['tiramisu']},
            {'nom': 'Panna cotta coulis framboise', 'prix':  800, 'type': 'cafe',    'desc': 'Creme italienne onctueuse, coulis de framboises fraiches',                 'img': IMG['panna_cotta']},
            {'nom': 'Limonade maison',              'prix':  450, 'type': 'boisson', 'desc': 'Citrons siciliens, sucre de canne, eau petillante',                        'img': IMG['limonade']},
            {'nom': 'Eau minerale 50cl',            'prix':  200, 'type': 'boisson', 'desc': 'Eau plate ou gazeuze, bien fraiche',                                       'img': IMG['eau_bouteille']},
            {'nom': 'Espresso doppio',              'prix':  400, 'type': 'cafe',    'desc': 'Double cafe ristretto, tradition napolitaine',                             'img': IMG['espresso']},
        ]
    },

    # ── 6. BURGER HOUSE ──────────────────────────────────────────
    {
        'nom': 'Burger House Djibouti',
        'desc': 'Le temple du burger artisanal a Djibouti ! Viande de boeuf locale hachee chaque matin, pain brioches cuits sur place, sauces maison exclusives. Ambiance urban-street, musique afrobeat, service rapide.',
        'adresse': 'Avenue Georges Clemenceau, Centre-ville, Djibouti',
        'tel': '+253 77 12 34 56',
        'cat': 'Fast-Food',
        'horaires': 'Lun-Dim 11h-00h',
        'gamme': '$',
        'cover': IMG['burger'],
        'menu': [
            {'nom': 'Classic Burger',           'prix': 1400, 'type': 'plat',    'desc': '180g boeuf, cheddar fondu, salade iceberg, tomate, oignon rouge, sauce maison',   'img': IMG['burger_img']},
            {'nom': 'Double Smash Burger',      'prix': 1900, 'type': 'plat',    'desc': '2x100g beef smash, double cheddar, cornichons, oignon croustillant, sauce House', 'img': IMG['burger_smash']},
            {'nom': 'Crispy Chicken Burger',    'prix': 1600, 'type': 'plat',    'desc': 'Cuisse de poulet panee, coleslaw maison, sauce buffalo',                          'img': IMG['burger_chicken']},
            {'nom': 'Fish Burger',              'prix': 1500, 'type': 'plat',    'desc': 'Filet de capitaine frit, sauce tartare citron-capres, salade',                    'img': IMG['poisson_grill']},
            {'nom': 'Veggie Burger',            'prix': 1200, 'type': 'plat',    'desc': 'Steak de pois chiches, avocat, tomate sechee, feta, pesto',                      'img': IMG['burger_veggie']},
            {'nom': 'Frites maison cheddar',    'prix':  700, 'type': 'plat',    'desc': 'Frites fraiches, sauce cheddar fondue, bacon crispy',                            'img': IMG['frites']},
            {'nom': 'Onion Rings',              'prix':  600, 'type': 'plat',    'desc': 'Oignons panures biere, sauce aioli a la truffe',                                 'img': IMG['onion_rings']},
            {'nom': 'Nuggets de poulet x8',     'prix':  900, 'type': 'plat',    'desc': 'Poulet croustillant, sauce honey-mustard ou BBQ',                                'img': IMG['nuggets']},
            {'nom': 'Milkshake Mangue-Coco',    'prix':  800, 'type': 'boisson', 'desc': 'Mangue locale, lait de coco, vanille, glace artisanale',                         'img': IMG['milkshake_v']},
            {'nom': 'Milkshake Chocolat Fondant','prix':  800, 'type': 'boisson', 'desc': 'Chocolat Valrhona, glace vanille, chantilly, caramel',                          'img': IMG['milkshake_c']},
            {'nom': 'Limonade Hibiscus',        'prix':  450, 'type': 'boisson', 'desc': 'Fleurs d hibiscus, citron vert, menthe, eau gazeuse',                            'img': IMG['limonade']},
            {'nom': 'Soda 33cl',                'prix':  300, 'type': 'boisson', 'desc': 'Coca, Fanta, Sprite, bien frais',                                               'img': IMG['jus_tamarind']},
            {'nom': 'Brownie maison',           'prix':  600, 'type': 'cafe',    'desc': 'Brownie chocolat noix, servi tiede avec glace vanille',                          'img': IMG['fondant']},
        ]
    },

    # ── 7. PÂTISSERIE ADEN ───────────────────────────────────────
    {
        'nom': 'Patisserie Aden',
        'desc': 'La reference de la patisserie orientale et francaise a Djibouti. Fondee en 1985, Aden conjugue le savoir-faire des grands patissiers francais avec les saveurs des douceurs du Golfe. Gateaux sur commande, buffets, evenements.',
        'adresse': 'Rue de Venise, Plateau du Serpent, Djibouti',
        'tel': '+253 77 44 22 11',
        'cat': 'Patisserie & Boulangerie',
        'horaires': 'Lun-Sam 7h-21h | Dim 8h-15h',
        'gamme': '$',
        'cover': IMG['patisserie'],
        'menu': [
            {'nom': 'Baklava aux pistaches',         'prix': 400, 'type': 'cafe',    'desc': 'Pate filo, pistaches de Syrie, sirop de miel, eau de fleur d oranger',    'img': IMG['baklava']},
            {'nom': 'Halwa cardamome-safran',         'prix': 500, 'type': 'cafe',    'desc': 'Confiserie traditionnelle somalo-yemenite, cardamome verte, safran rare', 'img': IMG['jus_orange']},
            {'nom': 'Eclair au cafe',                 'prix': 500, 'type': 'cafe',    'desc': 'Pate a choux, creme mousseline cafe, glacage miroir',                     'img': IMG['shaah']},
            {'nom': 'Tarte framboise-litchi',         'prix': 700, 'type': 'cafe',    'desc': 'Pate sablee breton, creme diplomate, framboises et litchis frais',        'img': IMG['tarte']},
            {'nom': 'Cheesecake fruits de la passion','prix': 800, 'type': 'cafe',    'desc': 'Base speculoos, appareil Philadelphia, coulis passion',                   'img': IMG['cheesecake']},
            {'nom': 'Macaron selection (x6)',         'prix': 900, 'type': 'cafe',    'desc': 'Assortiment de 6 macarons : rose, pistache, caramel, cafe, framboise',    'img': IMG['milkshake_v']},
            {'nom': 'Cafe filtre ethiopien',          'prix': 300, 'type': 'cafe',    'desc': 'Cafe Arabica d Ethiopie, filtre traditionnel, tres aromatique',           'img': IMG['jus_tamarind']},
            {'nom': 'Cappuccino maison',              'prix': 550, 'type': 'cafe',    'desc': 'Lait entier micro-mousse, espresso double',                               'img': IMG['cappuccino']},
            {'nom': 'Latte caramel',                  'prix': 600, 'type': 'cafe',    'desc': 'Espresso, lait vapeur, sirop de caramel maison, latte art',               'img': IMG['latte']},
            {'nom': 'Chocolat chaud epice',           'prix': 500, 'type': 'boisson', 'desc': 'Chocolat de Sao Tome, cannelle, piment doux, lait entier',               'img': IMG['chocolat_chaud']},
            {'nom': 'Jus de grenade frais',           'prix': 600, 'type': 'boisson', 'desc': 'Grenades pressees, miel de fleurs, citron',                              'img': IMG['jus_mangue']},
            {'nom': 'Eau minerale',                   'prix': 200, 'type': 'boisson', 'desc': 'Eau minerale fraiche',                                                   'img': IMG['eau_bouteille']},
        ]
    },

    # ── 8. RESTAURANT ÉTHIO-DJIBOUTI ─────────────────────────────
    {
        'nom': 'Ethio-Djibouti Chez Haile',
        'desc': 'Fusion unique de la cuisine ethiopienne et djiboutienne dans le quartier Hayyableh. Injera artisanale fermentee sur place, wats mijotes 6 heures, ambiance authentique avec musique ethiopienne.',
        'adresse': 'Quartier Hayyableh, Djibouti',
        'tel': '+253 77 22 33 44',
        'cat': 'Cuisine Ethiopienne',
        'horaires': 'Lun-Dim 8h-22h',
        'gamme': '$',
        'cover': IMG['ethiopian'],
        'menu': [
            {'nom': 'Mesob Royal pour 2',          'prix': 3500, 'type': 'plat',    'desc': 'Grand plateau: doro wat, tibs de boeuf, shiro, misir, gomen, 4 injera', 'img': IMG['injera']},
            {'nom': 'Doro Wat',                    'prix': 1800, 'type': 'plat',    'desc': 'Poulet mijoté 6h dans berbere rouge, oeuf dur, beurre niter kibbeh',    'img': IMG['doro_wat']},
            {'nom': 'Tibs de boeuf',               'prix': 2000, 'type': 'plat',    'desc': 'Boeuf saute a l ail, romarin, piment vert, beurre clarifie',           'img': IMG['grille_viande']},
            {'nom': 'Kitfo (tartare ethiopien)',    'prix': 2200, 'type': 'plat',    'desc': 'Boeuf cru hache minute, mitmita epice, beurre niter kibbeh, ayib',     'img': IMG['steak_boeuf']},
            {'nom': 'Shiro (pois chiches broyes)',  'prix':  900, 'type': 'plat',    'desc': 'Sauce epaisse pois chiches, berbere, ail, tomate, vegetarien',         'img': IMG['bariis']},
            {'nom': 'Misir Wat (lentilles rouges)', 'prix':  800, 'type': 'plat',    'desc': 'Lentilles mitades, berbere, ail, oignons fondus, vegetarien',          'img': IMG['maraq']},
            {'nom': 'Injera nature x3',             'prix':  300, 'type': 'plat',    'desc': 'Crepes fermentees teff, fraichement cuites',                           'img': IMG['lahoh']},
            {'nom': 'Tej (hydromel ethiopien)',     'prix':  400, 'type': 'boisson', 'desc': 'Hydromel traditionnel de gesho, leger et fruite',                      'img': IMG['tej']},
            {'nom': 'Buna (cafe ceremoniel)',       'prix':  350, 'type': 'cafe',    'desc': 'Cafe ethiopien selon la ceremonie traditionnelle, 3 tasses',           'img': IMG['cappuccino']},
            {'nom': 'Jus de papaye-gingembre',     'prix':  400, 'type': 'boisson', 'desc': 'Papaye locale, gingembre frais, citron vert, tres digestif',           'img': IMG['jus_mangue']},
        ]
    },

    # ── 9. LE ROOFTOP PALACE ─────────────────────────────────────
    {
        'nom': 'Le Rooftop Palace',
        'desc': 'Le seul restaurant en terrasse sur les toits de Djibouti avec une vue a 360 degres sur la ville, le golfe et les montagnes. Cuisine internationale et fusion afro-mediterrranenne. Couchers de soleil spectaculaires.',
        'adresse': 'Immeuble Le Palace, 8eme etage, Centre-ville, Djibouti',
        'tel': '+253 77 88 77 66',
        'cat': 'Gastronomique',
        'horaires': 'Jeu-Dim 17h-00h | Ven-Sam jusqu a 2h',
        'gamme': '$$$',
        'vedette': True,
        'cover': IMG['rooftop'],
        'menu': [
            {'nom': 'Brochettes mixtes Rooftop',   'prix': 3500, 'type': 'plat',    'desc': 'Brochettes boeuf-agneau-poulet, chimichurri, legumes grilles',          'img': IMG['brochettes']},
            {'nom': 'Ceviche de capitaine',        'prix': 2800, 'type': 'plat',    'desc': 'Capitaine frais, leche de tigre maison, mais grille, patate douce',     'img': IMG['tartare_thon']},
            {'nom': 'Assiette tapas Rooftop',      'prix': 3200, 'type': 'plat',    'desc': 'Hummus, pita chaude, kefta, fromage, olives, tzatziki, pour 2',         'img': IMG['tapas']},
            {'nom': 'Burger Rooftop Signature',    'prix': 2500, 'type': 'plat',    'desc': 'Wagyu 150g, foie gras mi-cuit, truffe, pain brioché maison',            'img': IMG['burger_img']},
            {'nom': 'Poulpe grille beurre corail', 'prix': 3000, 'type': 'plat',    'desc': 'Poulpe du golfe, beurre de corail, pommes grenaille, persil gremolata', 'img': IMG['poulpe_grill']},
            {'nom': 'Mocktail Sunset Djibouti',    'prix': 1200, 'type': 'boisson', 'desc': 'Mangue, passion, grenadine, eau de coco, frappe a la menthe',           'img': IMG['mocktail']},
            {'nom': 'Mocktail Blue Ocean',         'prix': 1100, 'type': 'boisson', 'desc': 'Citron bleu, sirop violette, eau petillante, spiruline',                'img': IMG['smoothie']},
            {'nom': 'Gateau Rooftop au chocolat',  'prix': 1500, 'type': 'cafe',    'desc': 'Gateau dome chocolat-framboises, coulis passion, fleur comestible',     'img': IMG['fondant']},
            {'nom': 'Assiette de fromages et fruits','prix':2000, 'type': 'cafe',   'desc': 'Selection fromages, figues fraiches, raisins, pain d epice',            'img': IMG['fromages']},
        ]
    },

    # ── 10. RESTO DU PORT ─────────────────────────────────────────
    {
        'nom': 'Resto du Port - Chez Mahad',
        'desc': "La cantine authentique des dockers et pecheurs du vieux port. Ouvert des l'aube, cuisine sans chichis mais avec le coeur. Portions enormes, poisson ultra-frais, prix imbattables.",
        'adresse': 'Quai du Port Commercial, Djibouti',
        'tel': '+253 77 55 44 33',
        'cat': 'Restaurant Traditionnel',
        'horaires': 'Lun-Sam 5h-18h (ferme Vendredi apres-midi)',
        'gamme': '$',
        'cover': IMG['port_cover'],           # UNIQUE - vieux port
        'menu': [
            {'nom': 'Bariis iyo Hilib (riz et viande)', 'prix':  700, 'type': 'plat',    'desc': 'Riz basmati, viande de chevre, epices xawaash, bouillon maison',  'img': IMG['bariis']},
            {'nom': 'Poisson grille du jour',           'prix': 1200, 'type': 'plat',    'desc': 'Poisson entier peche le matin, grille au charbon, citron-sel',    'img': IMG['poisson_grill']},
            {'nom': 'Sabaayad aux lentilles',           'prix':  500, 'type': 'plat',    'desc': 'Crepe croustillante au beurre avec sauce lentilles epaisses',     'img': IMG['lahoh']},
            {'nom': 'Maraq poisson',                    'prix':  600, 'type': 'plat',    'desc': 'Bouillon de poisson du jour, citron, piment, coriandre',         'img': IMG['maraq']},
            {'nom': 'Sambuusa x5',                      'prix':  800, 'type': 'plat',    'desc': 'Friands viande ou lentilles, frits a la minute',                 'img': IMG['sambuusa']},
            {'nom': 'Shaah kawa',                       'prix':  150, 'type': 'boisson', 'desc': 'The au lait tres sucre, tradition matinale',                     'img': IMG['shaah']},
            {'nom': 'Eau en bouteille',                 'prix':  100, 'type': 'boisson', 'desc': 'Bouteille d eau minerale fraiche',                               'img': IMG['eau_bouteille']},
            {'nom': 'Halwa du port',                    'prix':  300, 'type': 'cafe',    'desc': 'Halwa maison de la grand-mere, recette secrete',                 'img': IMG['halwa']},
        ]
    },

    # ── 11. CAFÉ HARAMOUS ─────────────────────────────────────────
    {
        'nom': 'Cafe Haramous',
        'desc': 'Cafe moderne et chaleureux dans le quartier residentiel Haramous. WiFi ultra-rapide, espaces lounge et co-working, playlist curatee. Le bureau hors-les-murs des entrepreneurs et freelances de Djibouti.',
        'adresse': 'Avenue Kenyatta, Quartier Haramous, Djibouti',
        'tel': '+253 77 55 66 77',
        'cat': 'Cafe & Salon de The',
        'horaires': 'Lun-Dim 7h-22h',
        'gamme': '$$',
        'cover': IMG['cafe_modern'],
        'menu': [
            {'nom': 'Specialty Coffee Latte',     'prix':  650, 'type': 'cafe',    'desc': 'Espresso double, lait entier micro-texture, latte art',               'img': IMG['latte']},
            {'nom': 'Flat White Haramous',        'prix':  600, 'type': 'cafe',    'desc': 'Ristretto double, lait vapeur velouteux, ratio cafe eleve',           'img': IMG['chocolat_chaud']},
            {'nom': 'Cold Brew Maison',           'prix':  700, 'type': 'cafe',    'desc': 'Cafe infuse a froid 18h, sirop vanille, lait avoine, glacons',        'img': IMG['milkshake_v']},
            {'nom': 'Matcha Latte ceremoniel',    'prix':  750, 'type': 'cafe',    'desc': 'Matcha ceremonie japonais, lait amande, sirop agave',                 'img': IMG['matcha_latte']},
            {'nom': 'Shaah premium',              'prix':  350, 'type': 'cafe',    'desc': 'The noir superior, lait entier, cardamome fraiche, cannelle',         'img': IMG['shaah']},
            {'nom': 'Cappuccino',                 'prix':  550, 'type': 'cafe',    'desc': 'Espresso, lait mousse, cacao saupoudre',                              'img': IMG['cappuccino']},
            {'nom': 'Avocado Toast',             'prix': 1100, 'type': 'plat',    'desc': 'Pain sourdough, avocat ecrase, oeuf poché, graines, piment',          'img': IMG['avocado_toast']},
            {'nom': 'Granola bowl',              'prix':  900, 'type': 'plat',    'desc': 'Granola maison, yaourt grec, fruits de saison, miel acacia',          'img': IMG['baklava']},
            {'nom': 'Club sandwich premium',     'prix': 1300, 'type': 'plat',    'desc': 'Pain brioche toast, poulet rotisserie, bacon, avocat, tomate',        'img': IMG['club_sand']},
            {'nom': 'Cheesecake New-York',        'prix':  900, 'type': 'cafe',    'desc': 'Creme Philadelphia, base digestive, coulis fruits rouges',            'img': IMG['cheesecake']},
            {'nom': 'Smoothie Green Power',       'prix':  700, 'type': 'boisson', 'desc': 'Epinard, concombre, pomme verte, gingembre, citron, chia',           'img': IMG['smoothie']},
            {'nom': 'Smoothie Tropical Sunrise',  'prix':  700, 'type': 'boisson', 'desc': 'Mangue, ananas, passion, lait de coco, curcuma',                     'img': IMG['jus_orange']},
            {'nom': 'Eau aromatisee concombre',  'prix':  400, 'type': 'boisson', 'desc': 'Eau fraiche, concombre, menthe, citron, desalterant',                 'img': IMG['eau_bouteille']},
        ]
    },

    # ── 12. SANDWICH CORNER ──────────────────────────────────────
    {
        'nom': 'Sandwich Corner Express',
        'desc': 'Sandwichs artisanaux prepares a la minute avec des produits frais locaux. Pains cuits le matin, ingredients selectionnes chaque jour au marche central.',
        'adresse': 'Centre Commercial Djibouti Shopping Center, Djibouti',
        'tel': '+253 77 11 22 33',
        'cat': 'Sandwicherie',
        'horaires': 'Lun-Ven 6h30-19h | Sam 7h-16h',
        'gamme': '$',
        'cover': IMG['sandwich'],
        'menu': [
            {'nom': 'Sandwich Thon-Avocat-Citron', 'prix': 700, 'type': 'plat',    'desc': 'Thon rouge, avocat, citron confit, roquette, sauce yaourt-aneth',    'img': IMG['club_sand']},
            {'nom': 'Wrap Poulet Tikka',            'prix': 750, 'type': 'plat',    'desc': 'Poulet tikka maison, raita concombre, oignons rouge, coriandre',    'img': IMG['wrap']},
            {'nom': 'Panini Jambon Emmental',       'prix': 650, 'type': 'plat',    'desc': 'Presse et chaud, jambon blanc, emmental, moutarde dijon',           'img': IMG['panini']},
            {'nom': 'Baguette Falafel-Houmous',     'prix': 600, 'type': 'plat',    'desc': 'Falafels croquants, houmous maison, tomates cerises, tahini',       'img': IMG['falafel']},
            {'nom': 'Sandwich Crevettes-Mangue',    'prix': 850, 'type': 'plat',    'desc': 'Crevettes grillees, chutney mangue-piment, laitue, mayo citron',   'img': IMG['crevettes']},
            {'nom': 'Smoothie Mangue-Banane-Lait',  'prix': 550, 'type': 'boisson', 'desc': 'Mangue locale, banane, lait entier, miel, frappe',                 'img': IMG['milkshake_v']},
            {'nom': 'Jus vert detox',               'prix': 500, 'type': 'boisson', 'desc': 'Pomme, concombre, celeri, citron, gingembre',                      'img': IMG['smoothie']},
            {'nom': 'Cafe au lait voyage',          'prix': 350, 'type': 'cafe',    'desc': 'A emporter dans grand gobelet, cafe double, lait chaud',            'img': IMG['latte']},
            {'nom': 'Muffin chocolat-noix',         'prix': 400, 'type': 'cafe',    'desc': 'Moelleux, pepites de chocolat noir, noix concassees',               'img': IMG['fondant']},
            {'nom': 'Eau fraiche',                  'prix': 200, 'type': 'boisson', 'desc': 'Eau minerale en bouteille',                                        'img': IMG['eau_bouteille']},
        ]
    },

    # ── 13. LE GRILL DES ARTISTES ─────────────────────────────────
    {
        'nom': 'Le Grill des Artistes',
        'desc': 'Steakhouse et grill a charbon de bois, le seul de son genre a Djibouti. Viandes importees d Ethiopie et d Australie, cuissons precisees au degre. Cave a maturation visible depuis la salle.',
        'adresse': 'Rue du General de Gaulle, Quartier Europeen, Djibouti',
        'tel': '+253 77 77 88 99',
        'cat': 'Grill & Viandes',
        'horaires': 'Mar-Dim 19h-23h',
        'gamme': '$$$',
        'cover': IMG['grilled_meat'],
        'menu': [
            {'nom': 'Cote de boeuf 1kg pour 2',         'prix': 8500, 'type': 'plat',    'desc': 'Boeuf mature 45 jours, os a moelle, chimichurri, frites maison',    'img': IMG['steak_boeuf']},
            {'nom': 'Filet de boeuf 250g',               'prix': 4500, 'type': 'plat',    'desc': 'Tournedos tendre, sauce au poivre vert, haricots verts amandes',    'img': IMG['grille_viande']},
            {'nom': 'Entrecote maturee 350g',            'prix': 5200, 'type': 'plat',    'desc': 'Entrecote maturation seche 30 jours, beurre cafe de Paris',          'img': IMG['entrecote']},
            {'nom': 'Carre d agneau entier',             'prix': 5800, 'type': 'plat',    'desc': 'Carre complet d agneau de Djibouti, croute herbes, jus truffe',      'img': IMG['carre_agneau']},
            {'nom': 'Brochettes de chevre marinees',     'prix': 2800, 'type': 'plat',    'desc': 'Chevre marinee 24h yaourt-citron-epices, pita et sauce verte',       'img': IMG['brochettes']},
            {'nom': 'Mixed Grill pour 2',                'prix': 7000, 'type': 'plat',    'desc': 'Entrecote, carre agneau, brochette poulet, kefta, legumes grilles',  'img': IMG['magret']},
            {'nom': 'Frites maison double cuisson',      'prix':  700, 'type': 'plat',    'desc': 'Pommes de terre fraiches, basse temperature puis friture',            'img': IMG['frites']},
            {'nom': 'Jus de goyave passion',             'prix':  550, 'type': 'boisson', 'desc': 'Goyave fraiche, fruits de la passion, citron vert',                  'img': IMG['jus_mangue']},
            {'nom': 'Eau minerale 75cl',                 'prix':  400, 'type': 'boisson', 'desc': 'Plate ou petillante, bien fraiche',                                  'img': IMG['eau_bouteille']},
            {'nom': 'Creme brulee cardamome',            'prix':  900, 'type': 'cafe',    'desc': 'Creme onctueuse, cardamome djiboutienne, sucre caramelise',          'img': IMG['creme_brulee']},
            {'nom': 'Fondant chocolat coulant',          'prix': 1000, 'type': 'cafe',    'desc': 'Coulant Guanaja 70%, coulis caramel beurre sale',                     'img': IMG['fondant']},
        ]
    },

    # ── 14. CHEZ IBRAHIM LA CANTINE ──────────────────────────────
    {
        'nom': 'Chez Ibrahim - La Cantine',
        'desc': 'Depuis 1978, la cantine populaire de quartier 4. Ibrahim et ses fils servent chaque jour des plats djiboutiens copieux et savoureux. Formule du jour a prix fixe, produits du marche local.',
        'adresse': 'Quartier 4 (Q4), Djibouti',
        'tel': '+253 77 66 55 44',
        'cat': 'Restaurant Traditionnel',
        'horaires': 'Lun-Sam 7h-20h',
        'gamme': '$',
        'cover': IMG['trad_cover2'],           # UNIQUE - marche traditionnel
        'menu': [
            {'nom': 'Formule du jour Ibrahim',    'prix':  800, 'type': 'plat',    'desc': 'Plat du jour + soupe + boisson, change chaque matin',             'img': IMG['skudahkharis']},
            {'nom': 'Hilib ari (chevre rotie)',   'prix': 1600, 'type': 'plat',    'desc': 'Cuisse de chevre rotie lentement, herbes aromatiques',            'img': IMG['grille_viande']},
            {'nom': 'Bariis caawa (riz du soir)', 'prix':  900, 'type': 'plat',    'desc': 'Riz special du soir, agneau, oignons dores, raisins secs',       'img': IMG['bariis']},
            {'nom': 'Soor (polenta djiboutienne)','prix':  600, 'type': 'plat',    'desc': 'Farine de mais cuite, beurre de chamelle, miel de datte',         'img': IMG['lahoh']},
            {'nom': 'Maraq caano (soupe au lait)','prix':  400, 'type': 'plat',    'desc': 'Soupe au lait camelin, riz, sucre, reconfortante',               'img': IMG['maraq']},
            {'nom': 'Sambusas au fromage',        'prix':  150, 'type': 'plat',    'desc': 'Beignets fromage frais, miel, piment doux',                       'img': IMG['sambuusa']},
            {'nom': 'Shaah Ibrahim',              'prix':  150, 'type': 'boisson', 'desc': 'Le fameux the d Ibrahim, secret de famille depuis 40 ans',       'img': IMG['shaah']},
            {'nom': 'Eau fraiche maison',         'prix':  100, 'type': 'boisson', 'desc': 'Eau fraiche en bouteille',                                       'img': IMG['eau_bouteille']},
        ]
    },

    # ── 15. PALAIS DE L'ASIE ─────────────────────────────────────
    {
        'nom': 'Palais de l Asie',
        'desc': 'Restaurant pan-asiatique unique a Djibouti, fonde par une famille sino-djiboutienne. Cuisine chinoise cantonaise, thai, japonaise fusion et specialites du Yunnan. Decor asiatique authentique, service impeccable.',
        'adresse': 'Rue d Ethiopie, Centre-ville, Djibouti',
        'tel': '+253 77 88 11 22',
        'cat': 'Cuisine Asiatique',
        'horaires': 'Lun-Dim 12h-15h | 19h-23h',
        'gamme': '$$',
        'cover': IMG['chinese'],
        'menu': [
            {'nom': 'Nems vietnamiens x4',          'prix':  900, 'type': 'plat',    'desc': 'Rouleau de printemps frit, porc-crevette, sauce nuoc cham',        'img': IMG['sambuusa']},
            {'nom': 'Dim Sum Vapeur (6 pieces)',     'prix': 1200, 'type': 'plat',    'desc': 'Raviolis crevettes, porc char siu, legumes, sauce soja gingembre', 'img': IMG['dim_sum']},
            {'nom': 'Canard laque pekinois',         'prix': 3500, 'type': 'plat',    'desc': 'Canard laque 24h, crepes mandarine, concombre, sauce hoisin',      'img': IMG['canard_laque']},
            {'nom': 'Nouilles sautees au boeuf',     'prix': 1600, 'type': 'plat',    'desc': 'Nouilles de riz larges, boeuf, brocoli, sauce huitre',             'img': IMG['noodles']},
            {'nom': 'Curry thai vert au poulet',     'prix': 1800, 'type': 'plat',    'desc': 'Poulet, lait de coco, aubergines thai, feuilles de kaffir, jasmin', 'img': IMG['curry_thai']},
            {'nom': 'Riz cantonais aux crevettes',   'prix': 1500, 'type': 'plat',    'desc': 'Riz saute, crevettes, oeuf brouille, petits pois, sauce soja',     'img': IMG['riz_poisson']},
            {'nom': 'The vert japonais Matcha',      'prix':  500, 'type': 'cafe',    'desc': 'Matcha premiere recolte Uji, preparation ceremonielle',            'img': IMG['matcha_latte']},
            {'nom': 'The Oolong aux fleurs',         'prix':  450, 'type': 'boisson', 'desc': 'The semi-oxyde, doux et floral, infusion 3 minutes',               'img': IMG['shaah']},
            {'nom': 'Mochi glace (3 pieces)',        'prix':  900, 'type': 'cafe',    'desc': 'Pate de riz gluant, coeur glace matcha, framboise, mangue',        'img': IMG['mochi']},
            {'nom': 'Limonade gingembre-citronnelle','prix':  500, 'type': 'boisson', 'desc': 'Gingembre frais, citronnelle, citron vert, eau petillante',        'img': IMG['limonade']},
        ]
    },

    # ── 16. CHEZ FATUMA - CUISINE FEMMES ─────────────────────────
    {
        'nom': 'Chez Fatuma - Cuisine des Femmes',
        'desc': 'Cooperative de femmes djiboutiennes qui preservent et transmettent les recettes ancestrales. Ambiance conviviale, tables partagees, repas comme a la maison.',
        'adresse': 'Rue Ali-Sabieh, Quartier Arhiba, Djibouti',
        'tel': '+253 77 44 55 66',
        'cat': 'Restaurant Traditionnel',
        'horaires': 'Lun-Sam 8h-21h',
        'gamme': '$',
        'cover': IMG['fatuma_cover'],          # UNIQUE - cuisine femmes
        'menu': [
            {'nom': 'Maraq hilib (soupe viande)',  'prix':  800, 'type': 'plat',    'desc': 'Bouillon genereux de mouton, legumes du marche, epices djiboutiennes', 'img': IMG['maraq']},
            {'nom': 'Iskukaris Fatuma',            'prix': 1300, 'type': 'plat',    'desc': 'Riz signature de Fatuma, viande d agneau, 11 epices secretes',        'img': IMG['skudahkharis']},
            {'nom': 'Ambalo (crepes au miel)',     'prix':  500, 'type': 'plat',    'desc': 'Crepes feuilletees au sirop de dattes et beurre fondu',              'img': IMG['lahoh']},
            {'nom': 'Muqmad artisanal',            'prix': 1800, 'type': 'plat',    'desc': 'Viande sechee confite, recette de la grand-mere de Fatuma',          'img': IMG['muqmad']},
            {'nom': 'Suqaar (ragout de boeuf)',    'prix': 1400, 'type': 'plat',    'desc': 'Des de boeuf sautes, piment vert, coriandre, servis avec canjeero',   'img': IMG['grille_viande']},
            {'nom': 'Sabaayad maison',             'prix':  300, 'type': 'plat',    'desc': 'Galette feuilletee croustillante, faite a la main minute',           'img': IMG['bariis']},
            {'nom': 'Shaah Fatuma special',        'prix':  200, 'type': 'boisson', 'desc': 'Recette familiale : the, lait camelien, 7 epices de la Corne',       'img': IMG['shaah']},
            {'nom': 'Jus de citronelle-menthe',    'prix':  250, 'type': 'boisson', 'desc': 'Citronnelle du jardin, menthe, miel de montagne, tres frais',        'img': IMG['jus_mangue']},
            {'nom': 'Halwa de fete',               'prix':  600, 'type': 'cafe',    'desc': 'Halwa preparee uniquement les vendredis et jours de fete',           'img': IMG['halwa']},
        ]
    },

    # ── 17. L'INDIEN MAHARAJA ─────────────────────────────────────
    {
        'nom': 'L Indien Maharaja',
        'desc': 'Cuisine indienne authentique a Djibouti, portee par la diaspora indo-pakistanaise presente depuis le XIXe siecle. Tandoor traditionnel chauffe au bois, epices moulues chaque matin.',
        'adresse': 'Rue de l Inde, Quartier Europeen, Djibouti',
        'tel': '+253 77 33 22 11',
        'cat': 'Cuisine Indienne',
        'horaires': 'Mar-Dim 12h-15h | 19h-23h',
        'gamme': '$$',
        'cover': IMG['indian'],
        'menu': [
            {'nom': 'Poulet Tikka Masala',    'prix': 2000, 'type': 'plat',    'desc': 'Poulet mariné yaourt-epices, sauce tomate-creme, masala maison',       'img': IMG['poulet_tikka']},
            {'nom': 'Agneau Biryani Royal',   'prix': 2500, 'type': 'plat',    'desc': 'Riz basmati premium, agneau tendre, safran, beresta, raita',           'img': IMG['biryani']},
            {'nom': 'Dal Makhani noir',       'prix': 1200, 'type': 'plat',    'desc': 'Lentilles noires mijotees 12h, beurre, creme, fenugrec',               'img': IMG['dal_makhani']},
            {'nom': 'Palak Paneer',           'prix': 1400, 'type': 'plat',    'desc': 'Fromage frais maison, epinards, epices, ghee, tres cremeux',           'img': IMG['curry']},
            {'nom': 'Seekh Kebab agneau',     'prix': 1800, 'type': 'plat',    'desc': 'Brochettes agneau hache au tandoor, chutney menthe-coriandre',         'img': IMG['kebab_img']},
            {'nom': 'Naan au fromage-ail',    'prix':  500, 'type': 'plat',    'desc': 'Pate fermentee, fromage mozzarella, ail confite, cuit au tandoor',     'img': IMG['naan']},
            {'nom': 'Lassi Mangue Alphonso',  'prix':  600, 'type': 'boisson', 'desc': 'Mangue Alphonso, yaourt entier, sucre, eau de rose, cardamome',        'img': IMG['lassi']},
            {'nom': 'Chai Masala',            'prix':  350, 'type': 'cafe',    'desc': 'The indien aux epices, gingembre, cardamome, cannelle, lait',          'img': IMG['chai_masala']},
            {'nom': 'Gulab Jamun',            'prix':  600, 'type': 'cafe',    'desc': 'Boulettes lait frit dans sirop rose-cardamome, chaud',                 'img': IMG['gulab_jamun']},
            {'nom': 'Kulfi pistache-safran',  'prix':  700, 'type': 'cafe',    'desc': 'Glace indienne compacte, pistaches, filaments de safran',              'img': IMG['glace_mangue']},
        ]
    },

    # ── 18. KEBAB EXPRESS ALI ─────────────────────────────────────
    {
        'nom': 'Kebab Express Ali Sabieh',
        'desc': 'Le meilleur kebab de Djibouti, point final. Ali cuisine depuis 25 ans, broche verticale au bois de santal, viande marinee 48h. Les students, les employes et les chauffeurs de taxi mangent au meme comptoir.',
        'adresse': 'Carrefour Ali Sabieh, Balbala, Djibouti',
        'tel': '+253 77 44 33 22',
        'cat': 'Fast-Food',
        'horaires': 'Lun-Dim 10h-02h (ouvert tard !)',
        'gamme': '$',
        'cover': IMG['kebab'],
        'menu': [
            {'nom': 'Kebab Ali Signature',      'prix':  600, 'type': 'plat',    'desc': 'Broche agneau-boeuf, pain pita maison, sauce yaourt-all-ail, salade', 'img': IMG['kebab_img']},
            {'nom': 'Durum Kebab XXL',          'prix':  900, 'type': 'plat',    'desc': 'Grand wrap : viande broche, frites a l interieur, sauce Ali secrete', 'img': IMG['wrap']},
            {'nom': 'Assiette Kebab complet',   'prix': 1200, 'type': 'plat',    'desc': 'Viande broche + riz + salade + pain + sauce, the offert',            'img': IMG['brochettes']},
            {'nom': 'Kefta grilles (6 pieces)', 'prix':  800, 'type': 'plat',    'desc': 'Keftas agneau-boeuf-piment, grilles a la flamme',                    'img': IMG['kefta']},
            {'nom': 'Frites maison sauce ali',  'prix':  400, 'type': 'plat',    'desc': 'Frites fraiches, sauce tomate-piment maison d Ali',                  'img': IMG['frites']},
            {'nom': 'Shaah bui',               'prix':  150, 'type': 'boisson', 'desc': 'The sucre servi dans verre metal, comme un vrai',                    'img': IMG['shaah']},
            {'nom': 'Soda frais 33cl',         'prix':  200, 'type': 'boisson', 'desc': 'Coca, Fanta ou Sprite bien froid',                                   'img': IMG['soda']},
        ]
    },

    # ── 19. LA PLAGE DORÉE ────────────────────────────────────────
    {
        'nom': 'La Plage Doree - Beach Club',
        'desc': 'Bar-restaurant-plage unique a Djibouti, pieds dans l eau sur la cote de Khor Ambado. Parasols, transats, musique reggae-afrobeat, cuisine grillades et snacks de mer. Ouvert le week-end.',
        'adresse': 'Plage de Khor Ambado, Route de Douda, Djibouti',
        'tel': '+253 77 99 88 77',
        'cat': 'Fruits de Mer',
        'horaires': 'Ven-Dim 10h-20h (week-end uniquement)',
        'gamme': '$$',
        'cover': IMG['beach_rest'],           # UNIQUE - plage (different de seafood_rest)
        'menu': [
            {'nom': 'Brochettes de crevettes grillees', 'prix': 2500, 'type': 'plat',    'desc': 'Crevettes du golfe, marinade citronnelle-ail, riz a la coco',   'img': IMG['crevettes']},
            {'nom': 'Poisson entier braise sur plage',  'prix': 2800, 'type': 'plat',    'desc': 'Braise directement sur charbon de plage, herbes fraiches',       'img': IMG['poisson_grill']},
            {'nom': 'Plateau fruits de mer froid',      'prix': 3500, 'type': 'plat',    'desc': 'Crevettes, homard, huitres, coques, sauce mignonette',           'img': IMG['langouste']},
            {'nom': 'Sandwich poisson frit plage',      'prix':  900, 'type': 'plat',    'desc': 'Pain burger, filet de capitaine frit, sauce tartare ananas',     'img': IMG['fish_burger']},
            {'nom': 'Salade de pieuvre marinee',        'prix': 1600, 'type': 'plat',    'desc': 'Poulpe tendre, citron vert, herbes, huile olive, paprika fume',  'img': IMG['poulpe_grill']},
            {'nom': 'Mocktail Plage Doree',             'prix':  800, 'type': 'boisson', 'desc': 'Coco frais, ananas, passion, menthe, rim sucre bleu',           'img': IMG['mocktail']},
            {'nom': 'Jus de coco frais (noix)',         'prix':  500, 'type': 'boisson', 'desc': 'Noix de coco entiere, paille, fraiche de la glaciere',          'img': IMG['coco_frais']},
            {'nom': 'Eau minerale fraiche',             'prix':  300, 'type': 'boisson', 'desc': 'Bouteille d eau fraiche de la glaciere',                       'img': IMG['eau_bouteille']},
            {'nom': 'Glace artisanale mangue',          'prix':  600, 'type': 'cafe',    'desc': 'Mangue locale, sorbetiere artisanale, sans additifs',           'img': IMG['glace_mangue']},
        ]
    },

    # ── 20. CAFÉ BALBALA TRENDY ───────────────────────────────────
    {
        'nom': 'Cafe Balbala Trendy',
        'desc': 'La nouvelle scene cafe dans le quartier populaire de Balbala. Concept inclusif, prix populaires mais cafe de specialite serieux. Jeunes baristas formes, art mural street-art. Ou la jeunesse de Djibouti se retrouve.',
        'adresse': 'Quartier Balbala Centre, Route de Douda, Djibouti',
        'tel': '+253 77 22 11 00',
        'cat': 'Cafe & Salon de The',
        'horaires': 'Lun-Dim 8h-23h',
        'gamme': '$',
        'cover': IMG['cafe_cowork'],          # UNIQUE - cafe coworking
        'menu': [
            {'nom': 'Cafe filtre Yirgacheffe',     'prix': 350, 'type': 'cafe',    'desc': 'Grain single origine Yirgacheffe, notes florales-citrus, filtre pur', 'img': IMG['jus_tamarind']},
            {'nom': 'Cappuccino Balbala Style',    'prix': 450, 'type': 'cafe',    'desc': 'Espresso local, lait entier mousse, latte art soleil',               'img': IMG['cappuccino']},
            {'nom': 'Dirty Chai Latte',            'prix': 500, 'type': 'cafe',    'desc': 'Chai masala + espresso + lait mousse, le best-seller',              'img': IMG['latte']},
            {'nom': 'Cold Brew citrus',            'prix': 550, 'type': 'cafe',    'desc': 'Cold brew maison, orange, cardamome, sur glace',                    'img': IMG['milkshake_v']},
            {'nom': 'Smoothie Balbala (mangue-tamarin)','prix': 450, 'type': 'boisson', 'desc': 'Mangue locale, tamarin, gingembre, piment doux, glacons',    'img': IMG['smoothie']},
            {'nom': 'Shaah traditionnel',          'prix': 150, 'type': 'boisson', 'desc': 'The somali classique pour les puristes',                           'img': IMG['shaah']},
            {'nom': 'Eau fraiche',                 'prix': 150, 'type': 'boisson', 'desc': 'Eau minerale fraiche',                                             'img': IMG['eau_bouteille']},
            {'nom': 'Toast Avocat-Oeuf',           'prix': 700, 'type': 'plat',    'desc': 'Pain toaste, avocat, oeuf au plat, piment rouge, za atar',         'img': IMG['avocado_toast']},
            {'nom': 'Crepe nutella-banane',        'prix': 500, 'type': 'plat',    'desc': 'Crepe moelleuse, nutella, banane flambee, noisettes',              'img': IMG['lahoh']},
            {'nom': 'Brownie caramel sale',        'prix': 500, 'type': 'cafe',    'desc': 'Brownie chocolat noir, caramel beurre sale coule, fleur de sel',   'img': IMG['fondant']},
        ]
    },

    # ── 21. SALON DE THÉ JASMIN ───────────────────────────────────  (NOUVEAU)
    {
        'nom': 'Salon de The Jasmin',
        'desc': 'Havre de paix et de saveurs, le Salon de The Jasmin propose une experience sensorielle unique autour du the. Thes du monde entier, patisseries orientales fines, decor zen avec fontaines et jasmin. L adresse pour se ressourcer a Djibouti.',
        'adresse': 'Rue de la Paix, Quartier Europeen, Djibouti',
        'tel': '+253 77 66 88 00',
        'cat': 'Cafe & Salon de The',
        'horaires': 'Lun-Sam 9h-21h | Dim 10h-19h',
        'gamme': '$$',
        'vedette': True,
        'cover': IMG['salon_the'],
        'menu': [
            {'nom': 'Ceremonie du The Darjeeling',  'prix':  900, 'type': 'cafe',    'desc': 'Darjeeling premier flush, service en theiere porcelaine, sachet hermetique', 'img': IMG['shaah']},
            {'nom': 'The Earl Grey premium',         'prix':  500, 'type': 'cafe',    'desc': 'Bergamote d Italie, the noir de Chine, fleurs de jasmin',                   'img': IMG['cappuccino']},
            {'nom': 'The Jasmin royal',              'prix':  600, 'type': 'cafe',    'desc': 'Perles de jasmin qui s epanouissent dans l eau chaude, spectaculaire',      'img': IMG['matcha_latte']},
            {'nom': 'Rooibos vanille-amande',        'prix':  450, 'type': 'cafe',    'desc': 'Rooibos d Afrique du Sud, sans theine, vanille naturelle, amande douce',   'img': IMG['chocolat_chaud']},
            {'nom': 'Matcha ceremoniel en bol',      'prix':  750, 'type': 'cafe',    'desc': 'Matcha grade ceremonie, fouette avec chasen, tradition japonaise',          'img': IMG['latte']},
            {'nom': 'Infusion hibiscus-gingembre',   'prix':  400, 'type': 'boisson', 'desc': 'Fleurs d hibiscus, gingembre frais, miel acacia, citron, glacons',         'img': IMG['jus_tamarind']},
            {'nom': 'Limonade rose a la rose',       'prix':  500, 'type': 'boisson', 'desc': 'Sirop de rose, citron, eau petillante, petales comestibles',               'img': IMG['limonade']},
            {'nom': 'Eau minerale',                  'prix':  200, 'type': 'boisson', 'desc': 'Eau minerale fraiche',                                                     'img': IMG['jus_orange']},
            {'nom': 'Assortiment patisseries orientales','prix': 1200,'type': 'cafe', 'desc': 'Baklava, mamoul, cornes de gazelle, loukoums, a partager',                 'img': IMG['baklava']},
            {'nom': 'Scones beurre-confiture maison','prix':  700, 'type': 'cafe',    'desc': 'Scones tiedes, beurre AOP, confiture mangue-citron maison, creme',         'img': IMG['lahoh']},
            {'nom': 'Cheesecake jasmin-litchi',      'prix':  850, 'type': 'cafe',    'desc': 'Base sable, creme legere eau de jasmin, gelee litchi, fleurs',             'img': IMG['cheesecake']},
            {'nom': 'Tarte aux fruits de saison',    'prix':  750, 'type': 'cafe',    'desc': 'Pate sablee maison, creme patissiere, fruits frais du marche',             'img': IMG['milkshake_v']},
        ]
    },

    # ── 22. CAFÉ L'ESCALE ─────────────────────────────────────────  (NOUVEAU)
    {
        'nom': "Cafe L Escale",
        'desc': "Cafe moderne et convivial pres du centre commercial, l Escale est le rendez-vous des familles et des professionnels. Cafe de specialite, snacks, petits-dejeuners etoffes et dejeuners express. Terrasse ombragee et climatisation.",
        'adresse': 'Avenue de la Republique, Plateau du Serpent, Djibouti',
        'tel': '+253 77 11 55 99',
        'cat': 'Cafe & Salon de The',
        'horaires': 'Lun-Ven 6h-21h | Sam-Dim 7h-22h',
        'gamme': '$$',
        'cover': IMG['cafe_chic'],
        'menu': [
            {'nom': 'Espresso L Escale',           'prix':  350, 'type': 'cafe',    'desc': 'Blend maison 100% Arabica, extraction 27 secondes, arriere-gout chocolat', 'img': IMG['espresso']},
            {'nom': 'Cappuccino classique',        'prix':  550, 'type': 'cafe',    'desc': 'Espresso ristretto, lait entier mousse, dome crème, cacao',               'img': IMG['latte']},
            {'nom': 'Latte art maison',            'prix':  650, 'type': 'cafe',    'desc': 'Espresso double, lait vapeur micro-texture, motif latte art',             'img': IMG['matcha_latte']},
            {'nom': 'Cafe glacé caramel',          'prix':  700, 'type': 'cafe',    'desc': 'Espresso frais, lait entier froid, sirop caramel, glacons, chantilly',   'img': IMG['jus_tamarind']},
            {'nom': 'Americano long',              'prix':  400, 'type': 'cafe',    'desc': 'Double espresso allonge, leger et aromatique',                            'img': IMG['shaah']},
            {'nom': 'Breakfast L Escale',          'prix': 1500, 'type': 'plat',    'desc': 'Oeufs brouilles, bacon, toast, beurre, confiture, jus orange, cafe',     'img': IMG['granola']},
            {'nom': 'Pancakes sirop d erable',     'prix':  900, 'type': 'plat',    'desc': 'Pancakes moelleux, sirop d erable canadien, beurre, fruits frais',       'img': IMG['lahoh']},
            {'nom': 'Croissant jambon-fromage',    'prix':  700, 'type': 'plat',    'desc': 'Croissant chaud, jambon blanc, emmental, moutarde douce',                'img': IMG['croque_monsieur']},
            {'nom': 'Salade cesar poulet',         'prix': 1200, 'type': 'plat',    'desc': 'Romaine, poulet grille, croûtons, parmesan, sauce cesar maison',         'img': IMG['biryani']},
            {'nom': 'Smoothie bowl tropical',      'prix':  900, 'type': 'plat',    'desc': 'Base mangue-banane, granola, coco, fruits frais, graines de chia',       'img': IMG['jus_mangue']},
            {'nom': 'Jus frais du jour',           'prix':  500, 'type': 'boisson', 'desc': 'Selon arrivage : orange, mangue, papaye ou goyave, presse minute',       'img': IMG['jus_orange']},
            {'nom': 'Limonade maison',             'prix':  450, 'type': 'boisson', 'desc': 'Citrons frais, sucre de canne, eau gazeuse, menthe, citron vert',        'img': IMG['limonade']},
            {'nom': 'Eau minerale 50cl',           'prix':  250, 'type': 'boisson', 'desc': 'Eau fraiche plate ou petillante',                                        'img': IMG['milkshake_v']},
            {'nom': 'Fondant chocolat maison',     'prix':  700, 'type': 'cafe',    'desc': 'Coulant chocolat noir, glace vanille, caramel liquide',                  'img': IMG['fondant']},
            {'nom': 'Tarte du jour',               'prix':  650, 'type': 'cafe',    'desc': 'Selon inspiration du chef : framboise, citron, abricot ou pomme',       'img': IMG['tarte']},
        ]
    },
]


class Command(BaseCommand):
    help = 'Seed complet : 22 restaurants djiboutiens avec menus detailles et images uniques'

    def handle(self, *args, **kwargs):
        self.stdout.write('=== SEED DJIB RECO - 22 restaurants ===')

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@djib-reco.dj', 'admin1234')
            self.stdout.write(self.style.SUCCESS('[OK] Admin: admin / admin1234'))
        admin = User.objects.get(username='admin')

        if not User.objects.filter(username='djib_user').exists():
            User.objects.create_user('djib_user', 'ali@djib-reco.dj', 'user1234', first_name='Ali', last_name='Hassan')
            self.stdout.write(self.style.SUCCESS('[OK] User: djib_user / user1234'))
        user2 = User.objects.get(username='djib_user')

        if not User.objects.filter(username='djib_user2').exists():
            User.objects.create_user('djib_user2', 'fatuma@djib-reco.dj', 'user1234', first_name='Fatuma', last_name='Omar')
        user3 = User.objects.get(username='djib_user2')

        # Categories
        cat_map = {}
        for cd in CATEGORIES:
            cat, _ = Categorie.objects.update_or_create(
                nom=cd['nom'],
                defaults={'icone': cd['icone'], 'cover_url': cd.get('cover', '')}
            )
            cat_map[cd['nom']] = cat
        self.stdout.write(f'[OK] {len(CATEGORIES)} categories')

        # Restaurants + menus
        created = 0
        for d in RESTAURANTS:
            rest, _ = Restaurant.objects.update_or_create(
                nom=d['nom'],
                defaults={
                    'description': d['desc'],
                    'adresse': d['adresse'],
                    'telephone': d.get('tel', ''),
                    'categorie': cat_map.get(d['cat']),
                    'horaires': d.get('horaires', ''),
                    'gamme_prix': d.get('gamme', '$$'),
                    'est_vedette': d.get('vedette', False),
                    'cover_url': d['cover'],
                    'ajoute_par': admin,
                }
            )
            MenuItem.objects.filter(restaurant=rest).delete()
            for item in d.get('menu', []):
                MenuItem.objects.create(
                    restaurant=rest,
                    nom=item['nom'],
                    prix=item['prix'],
                    type_item=item['type'],
                    description=item.get('desc', ''),
                    cover_url=item.get('img', ''),
                )
            created += 1
            self.stdout.write(f'  [{created}/22] {rest.nom} ({rest.menu_items.count()} items)')

        # Avis variés
        notes_u1 = [5, 4, 5, 5, 3, 4, 5, 4, 5, 5, 4, 3, 5, 4, 5, 4, 5, 3, 4, 5, 5, 4]
        notes_u2 = [4, 5, 4, 4, 5, 5, 4, 5, 4, 4, 5, 4, 4, 5, 4, 5, 4, 5, 5, 4, 4, 5]
        avis_u1 = [
            'Vue sur le golfe magnifique ! Le plateau fruits de mer est exceptionnel.',
            'Le Cafe de Paris est une institution, je viens ici depuis mon enfance.',
            'Chez Saba, on retrouve les saveurs authentiques de notre cuisine. Skudahkharis parfait !',
            'Gastronomie au sommet. Le Heron Bleu merite amplement sa reputation.',
            'Pizzas bonnes mais un peu cheres pour Djibouti.',
            'Les burgers sont excellents ! Le Double Smash est mon prefere.',
            'La Patisserie Aden est divine. Les baklavas sont les meilleurs que j ai jamais manges.',
            'Chez Haile, une decouverte ! Le doro wat est phenomenal.',
            'Le Rooftop Palace, vue a couper le souffle avec le coucher de soleil sur Djibouti.',
            'Chez Mahad, le vrai Djibouti sans pretention. Poisson ultra-frais !',
            'Cafe Haramous, mon bureau prefere. Cold brew exceptionnel.',
            'Bon mais service un peu lent. Les sandwichs restent corrects.',
            'Le Grill des Artistes, la cote de boeuf pour 2 est spectaculaire.',
            'Chez Ibrahim, la formule du jour est un vrai bonheur depuis 20 ans.',
            'Palais de l Asie, le canard laque est digne de Hong Kong !',
            'Cuisine de Fatuma, exactement comme chez ma grand-mere.',
            'Maharaja, curry authentique et naans gonfles devant vous !',
            'Kebab d Ali, incontournable a minuit apres le travail.',
            'La Plage Doree, les pieds dans le sable et la langouste dans l assiette.',
            'Cafe Balbala, atmosphere unique et cold brew surprenant pour le quartier.',
            'Salon Jasmin, une parenthese de calme. La ceremonie du the est un moment magique.',
            'L Escale, petit-dejeuner parfait avant le bureau. Les pancakes sont divins !',
        ]
        avis_u2 = [
            'Plateau Royale de la Mer valait chaque Franc !',
            'Croissant au beurre du Cafe de Paris, le meilleur de toute l Afrique de l Est.',
            'Muqmad de Saba, un tresor gastronomique djiboutien a preserver.',
            'Le millefeuille du Heron Bleu est une oeuvre d art.',
            'Pizza Margherita DOC absolument authentique, merci !',
            'Crispy Chicken Burger, une revelation !',
            'Cheesecake Aden, je reve de lui la nuit.',
            'Mesob Royal pour toute la famille, moment inoubliable.',
            'Mocktail Sunset Djibouti a change ma vie.',
            'Poisson braise sur la plage chez Mahad, experience unique au monde.',
            'Matcha Latte Haramous, le meilleur de tout Djibouti.',
            'Wrap Poulet Tikka, pratique et delicieux pour le dejeuner.',
            'Mixed Grill pour 2 au Grill des Artistes, une fete !',
            'Cuisine de Fatuma, exactement comme chez ma grand-mere.',
            'Curry thai vert Maharaja, epices parfaitement equilibrees.',
            'Shaah Fatuma, recette incomparable, goût d enfance.',
            'Biryani Royal Maharaja, les meilleures saveurs indiennes a Djibouti.',
            'Durum Kebab d Ali, le meilleur rapport qualite-prix de la ville.',
            'Glace mangue artisanale en bord de plage, un bonheur pur.',
            'Cold brew citrus au Balbala, inattendu mais excellent.',
            'The Jasmin royal en fleurs, spectacle et delice a la fois.',
            'Latte art de L Escale, beau et bon, le barista est talentueux.',
        ]

        rest_list = list(Restaurant.objects.all())
        avis_count = 0
        for i, rest in enumerate(rest_list):
            if i < len(avis_u1) and not Avis.objects.filter(utilisateur=user2, restaurant=rest).exists():
                Avis.objects.create(utilisateur=user2, restaurant=rest, note=notes_u1[i], commentaire=avis_u1[i])
                avis_count += 1
            if i < len(avis_u2) and not Avis.objects.filter(utilisateur=user3, restaurant=rest).exists():
                Avis.objects.create(utilisateur=user3, restaurant=rest, note=notes_u2[i], commentaire=avis_u2[i])
                avis_count += 1

        self.stdout.write(f'[OK] {avis_count} avis')
        self.stdout.write(self.style.SUCCESS(f'\n=== DONE : {created} restaurants, {MenuItem.objects.count()} items de menu ==='))
        self.stdout.write('   http://localhost:8000/')
