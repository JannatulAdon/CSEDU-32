import os, json, re, shutil

deploy_dir = os.path.dirname(os.path.abspath(__file__))
sub_dir = os.path.join(deploy_dir, "messenger-group-chat")

# 1. Load clean chat_statistics.json
json_path = os.path.join(deploy_dir, "chat_statistics.json")
with open(json_path, 'r', encoding='utf-8') as f:
    chat_data = json.load(f)

# Clean up unwanted fields from chat_data if present
if 'funny_details' in chat_data and 'vai_addicts' in chat_data['funny_details']:
    del chat_data['funny_details']['vai_addicts']

# Ensure ranks are pre-assigned
for idx, p in enumerate(chat_data.get('participants', [])):
    p['rank'] = idx + 1

# Write back cleaned chat_statistics.json to both directories
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(chat_data, f, ensure_ascii=False, indent=2)

if os.path.exists(sub_dir):
    with open(os.path.join(sub_dir, "chat_statistics.json"), 'w', encoding='utf-8') as f:
        json.dump(chat_data, f, ensure_ascii=False, indent=2)

# 2. Build app.js
app_js_code = """// CSEDU-32 Group Chat Analytics & Meme Vault
const rawData = """ + json.dumps(chat_data, ensure_ascii=False) + """;

// Pre-assign participant ranks
if (rawData.participants) {
  rawData.participants.forEach((p, idx) => {
    p.rank = idx + 1;
  });
}

let currentGalleryFilter = 'all';
let currentSortKey = 'rank';
let sortDirection = { rank: 'asc' };

function switchTab(tabId, btn) {
  const panes = document.querySelectorAll('.tab-pane');
  for (let i = 0; i < panes.length; i++) {
    panes[i].classList.remove('active');
  }
  const btns = document.querySelectorAll('.tab-btn');
  for (let i = 0; i < btns.length; i++) {
    btns[i].classList.remove('active');
  }
  
  const targetPane = document.getElementById('tab-' + tabId);
  if (targetPane) {
    targetPane.classList.add('active');
  }

  for (let i = 0; i < btns.length; i++) {
    const b = btns[i];
    const oc = b.getAttribute('onclick') || '';
    if (b === btn || oc.indexOf(tabId) !== -1) {
      b.classList.add('active');
    }
  }
}

function openLightbox(src) {
  const modal = document.getElementById('lightboxModal');
  const img = document.getElementById('lightboxImg');
  if (modal && img) {
    img.src = src;
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
  }
}

function closeLightbox() {
  const modal = document.getElementById('lightboxModal');
  if (modal) modal.classList.remove('active');
  document.body.style.overflow = '';
}

function resolveImgSrc(item, type) {
  if (type === 'photo') {
    if (item.photos && item.photos.length > 0) return item.photos[0];
    if (item.photo_data && item.photo_data.length > 0) return item.photo_data[0];
  } else if (type === 'gif') {
    if (item.gifs && item.gifs.length > 0) return item.gifs[0];
    if (item.gif_data && item.gif_data.length > 0) return item.gif_data[0];
  }
  return '';
}

function buildSuperlatives() {
  const p = rawData.participants;
  const court = rawData.funny_details;
  if (!p || p.length === 0) return;

  const awards = [
    {
      icon: '👑',
      cat: 'The Supreme Chatterbox',
      title: 'Most Messages Sent',
      winner: p[0].name,
      stat: '<span class="award-highlight">' + p[0].messages.toLocaleString() + '</span> messages (' + p[0].percentage + '% of group)'
    },
    {
      icon: '🔨',
      cat: 'The Supreme Executioner',
      title: 'Most Members Kicked (The Ban Hammer)',
      winner: court.ban_hammer_executioners[0].name,
      stat: '<span class="award-highlight">' + court.ban_hammer_executioners[0].count + '</span> people purged from the group!'
    },
    {
      icon: '💀',
      cat: 'The Unkillable Martyr',
      title: 'Most Times Kicked by CR',
      winner: court.ban_hammer_victims[0].name,
      stat: '<span class="award-highlight">' + court.ban_hammer_victims[0].count + '</span> times kicked & 9 rage quits!'
    },
    {
      icon: '✍️',
      cat: 'The Chief Essayist',
      title: 'Most Words Written',
      winner: p.slice().sort((a,b) => b.words - a.words)[0].name,
      stat: '<span class="award-highlight">' + p.slice().sort((a,b) => b.words - a.words)[0].words.toLocaleString() + '</span> words typed'
    },
    {
      icon: '📜',
      cat: 'The Novelist',
      title: 'Longest Average Message',
      winner: p.filter(x => x.messages >= 100).sort((a,b) => b.avg_words_per_msg - a.avg_words_per_msg)[0].name,
      stat: '<span class="award-highlight">' + p.filter(x => x.messages >= 100).sort((a,b) => b.avg_words_per_msg - a.avg_words_per_msg)[0].avg_words_per_msg + '</span> words per message average'
    },
    {
      icon: '😭',
      cat: 'The Emoji Addict',
      title: 'Most Emojis Used',
      winner: p.slice().sort((a,b) => b.total_emojis - a.total_emojis)[0].name,
      stat: '<span class="award-highlight">' + p.slice().sort((a,b) => b.total_emojis - a.total_emojis)[0].total_emojis.toLocaleString() + '</span> emojis'
    },
    {
      icon: '🌟',
      cat: 'The Clout Sovereign',
      title: 'Most Reactions Received',
      winner: p.slice().sort((a,b) => b.reacts_received - a.reacts_received)[0].name,
      stat: '<span class="award-highlight">' + p.slice().sort((a,b) => b.reacts_received - a.reacts_received)[0].reacts_received.toLocaleString() + '</span> reactions gathered'
    },
    {
      icon: '❤️',
      cat: 'The Ultimate Hype Master',
      title: 'Most Reactions Given',
      winner: p.slice().sort((a,b) => b.reacts_given - a.reacts_given)[0].name,
      stat: '<span class="award-highlight">' + p.slice().sort((a,b) => b.reacts_given - a.reacts_given)[0].reacts_given.toLocaleString() + '</span> reactions given'
    },
    {
      icon: '🙈',
      cat: 'The Secret Keeper',
      title: 'Most Unsent Messages',
      winner: p.slice().sort((a,b) => b.unsent - a.unsent)[0].name,
      stat: '<span class="award-highlight">' + p.slice().sort((a,b) => b.unsent - a.unsent)[0].unsent + '</span> messages erased'
    },
    {
      icon: '🦉',
      cat: 'The Chief Night Owl',
      title: 'Most Late Night Msgs (12AM-5AM)',
      winner: p.slice().sort((a,b) => b.night_msgs - a.night_msgs)[0].name,
      stat: '<span class="award-highlight">' + p.slice().sort((a,b) => b.night_msgs - a.night_msgs)[0].night_msgs.toLocaleString() + '</span> night messages'
    },
    {
      icon: '📸',
      cat: 'The Shutterbug / Meme Dealer',
      title: 'Most Photos Sent',
      winner: p.slice().sort((a,b) => b.photos - a.photos)[0].name,
      stat: '<span class="award-highlight">' + p.slice().sort((a,b) => b.photos - a.photos)[0].photos + '</span> photos shared'
    },
    {
      icon: '🍿',
      cat: 'The Monologue King',
      title: 'Longest Solo Chat Streak',
      winner: p.slice().sort((a,b) => b.max_consecutive - a.max_consecutive)[0].name,
      stat: '<span class="award-highlight">' + p.slice().sort((a,b) => b.max_consecutive - a.max_consecutive)[0].max_consecutive + '</span> messages in a row uninterrupted'
    },
    {
      icon: '📢',
      cat: 'The CPR Reviver',
      title: 'Most Conversation Starters',
      winner: p.slice().sort((a,b) => b.starters - a.starters)[0].name,
      stat: '<span class="award-highlight">' + p.slice().sort((a,b) => b.starters - a.starters)[0].starters + '</span> times broke 4+ hour silence'
    },
    {
      icon: '🛑',
      cat: 'The Chat Assassin',
      title: 'Most Conversation Enders',
      winner: p.slice().sort((a,b) => b.killers - a.killers)[0].name,
      stat: '<span class="award-highlight">' + p.slice().sort((a,b) => b.killers - a.killers)[0].killers + '</span> times ended the chat'
    }
  ];

  const container = document.getElementById('awards-container');
  if (container) {
    container.innerHTML = awards.map(a => 
      '<div class="award-card">' +
        '<div>' +
          '<div class="award-header">' +
            '<div class="award-icon">' + a.icon + '</div>' +
            '<div>' +
              '<div class="award-category">' + a.cat + '</div>' +
              '<div class="award-title">' + a.title + '</div>' +
            '</div>' +
          '</div>' +
          '<div class="award-winner">' + a.winner + '</div>' +
        '</div>' +
        '<div class="award-stat">' + a.stat + '</div>' +
      '</div>'
    ).join('');
  }
}

function renderGallery() {
  const container = document.getElementById('gallery-container');
  if (!container || !rawData.media_gallery) return;

  let items = rawData.media_gallery;
  if (currentGalleryFilter !== 'all') {
    items = items.filter(m => m.type === currentGalleryFilter);
  }

  container.innerHTML = items.map((m) => {
    let mediaHtml = '';
    const photoSrc = resolveImgSrc(m, 'photo');
    const gifSrc = resolveImgSrc(m, 'gif');

    if (photoSrc) {
      mediaHtml = '<img src="' + photoSrc + '" loading="lazy" onerror="this.style.display=\\'none\\'" onclick="openLightbox(\\'' + photoSrc + '\\')" alt="Media">';
    } else if (gifSrc) {
      mediaHtml = '<img src="' + gifSrc + '" loading="lazy" onerror="this.style.display=\\'none\\'" onclick="openLightbox(\\'' + gifSrc + '\\')" alt="GIF">';
    }

    const rxBadges = Object.entries((m.reactions || []).reduce((acc, cur) => { acc[cur] = (acc[cur] || 0) + 1; return acc; }, {}))
      .map(([emoji, count]) => '<span class="rx-badge">' + emoji + ' ' + count + '</span>').join('');

    return (
      '<div class="gallery-card">' +
        '<div class="gallery-media-wrapper">' + mediaHtml + '</div>' +
        '<div class="gallery-info">' +
          '<div class="gallery-header">' +
            '<span class="gallery-sender">' + m.sender + '</span>' +
            '<span class="gallery-time">' + m.time + '</span>' +
          '</div>' +
          (m.content ? '<div class="gallery-caption">' + m.content + '</div>' : '') +
          '<div class="gallery-rx-bar">' +
            '<div class="gallery-reactions">' + rxBadges + '</div>' +
            '<div class="rx-total">🔥 ' + m.count + '</div>' +
          '</div>' +
        '</div>' +
      '</div>'
    );
  }).join('');
}

function filterGallery(filter, btn) {
  currentGalleryFilter = filter;
  document.querySelectorAll('.filter-chip').forEach(el => el.classList.remove('active'));
  if (btn) btn.classList.add('active');
  renderGallery();
}

function renderTable(dataToRender) {
  const tbody = document.getElementById('tableBody');
  if (!tbody) return;

  const countElem = document.getElementById('participantCount');
  if (countElem) {
    countElem.textContent = dataToRender.length;
  }

  if (dataToRender.length === 0) {
    tbody.innerHTML = '<tr><td colspan="13" style="text-align:center; padding: 2.5rem; color: var(--text-dim);">No participants found matching your search.</td></tr>';
    return;
  }

  tbody.innerHTML = dataToRender.map(p => {
    const rankClass = p.rank === 1 ? 'rank-1' : p.rank === 2 ? 'rank-2' : p.rank === 3 ? 'rank-3' : '';
    const safeName = (p.name || '').replace(/'/g, "\\\\'");
    const topEmoji = (p.top_emojis && p.top_emojis[0]) ? p.top_emojis[0] : { emoji: '💬', count: 0 };
    const initial = p.name ? p.name.charAt(0) : '?';

    return (
      '<tr class="participant-row" onclick="openModal(\\'' + safeName + '\\')">' +
        '<td class="rank-cell ' + rankClass + '">#' + p.rank + '</td>' +
        '<td>' +
          '<div class="user-cell">' +
            '<div class="user-avatar">' + initial + '</div>' +
            '<div class="user-name-wrapper">' +
              '<span class="user-name">' + p.name + '</span>' +
              '<span class="user-sub">' + p.percentage + '% of chat</span>' +
            '</div>' +
          '</div>' +
        '</td>' +
        '<td><span class="archetype-pill">' + (p.archetype || 'Member') + '</span></td>' +
        '<td class="mono-cell" style="font-weight:700;">' + p.messages.toLocaleString() + '</td>' +
        '<td class="mono-cell" style="color:var(--text-muted);">' + p.percentage + '%</td>' +
        '<td class="mono-cell">' + p.words.toLocaleString() + '</td>' +
        '<td class="mono-cell">' + p.avg_words_per_msg + '</td>' +
        '<td class="mono-cell" style="color:#38bdf8;">' + (p.photos || 0) + '</td>' +
        '<td class="mono-cell" style="color:#f59e0b;font-weight:700;">+' + (p.reacts_received || 0).toLocaleString() + '</td>' +
        '<td class="mono-cell" style="color:#ec4899;">-' + (p.reacts_given || 0).toLocaleString() + '</td>' +
        '<td class="mono-cell" style="color:#818cf8;">' + (p.night_msgs || 0).toLocaleString() + '</td>' +
        '<td><span class="emoji-pill">' + topEmoji.emoji + ' ' + topEmoji.count + '</span></td>' +
        '<td>' +
          '<button class="view-profile-btn" onclick="event.stopPropagation(); openModal(\\'' + safeName + '\\')">' +
            '<span>Profile</span> 👤' +
          '</button>' +
        '</td>' +
      '</tr>'
    );
  }).join('');
}

function filterTable() {
  const input = document.getElementById('tableSearch');
  const query = input ? input.value.toLowerCase().trim() : '';
  const filtered = rawData.participants.filter(p => p.name.toLowerCase().includes(query));
  
  // Re-sort filtered data based on currentSortKey
  const direction = sortDirection[currentSortKey] || 'asc';
  filtered.sort((a, b) => {
    let valA = a[currentSortKey] !== undefined ? a[currentSortKey] : '';
    let valB = b[currentSortKey] !== undefined ? b[currentSortKey] : '';
    if (typeof valA === 'string') {
      return direction === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA);
    }
    return direction === 'asc' ? valA - valB : valB - valA;
  });

  renderTable(filtered);
}

function sortTable(key) {
  if (currentSortKey === key) {
    sortDirection[key] = sortDirection[key] === 'asc' ? 'desc' : 'asc';
  } else {
    currentSortKey = key;
    sortDirection[key] = (key === 'rank' || key === 'name' || key === 'archetype') ? 'asc' : 'desc';
  }
  const direction = sortDirection[key];

  // Update sort icons in table headers
  document.querySelectorAll('.sort-icon').forEach(el => el.textContent = '');
  const activeIcon = document.getElementById('sort-' + key);
  if (activeIcon) {
    activeIcon.textContent = direction === 'asc' ? ' ▲' : ' ▼';
  }

  const query = (document.getElementById('tableSearch')?.value || '').toLowerCase().trim();
  const listToSort = rawData.participants.filter(p => p.name.toLowerCase().includes(query));

  listToSort.sort((a, b) => {
    let valA = a[key] !== undefined ? a[key] : '';
    let valB = b[key] !== undefined ? b[key] : '';
    if (typeof valA === 'string') {
      return direction === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA);
    }
    return direction === 'asc' ? valA - valB : valB - valA;
  });

  renderTable(listToSort);
}

function buildHallOfFame() {
  const container = document.getElementById('hof-container');
  if (!container || !rawData.hall_of_fame) return;

  container.innerHTML = rawData.hall_of_fame.map((m, i) => {
    let mediaBox = '';
    const photoSrc = resolveImgSrc(m, 'photo');
    const gifSrc = resolveImgSrc(m, 'gif');

    if (photoSrc) {
      mediaBox = '<div class="hof-media-box" onclick="openLightbox(\\'' + photoSrc + '\\')"><img src="' + photoSrc + '" loading="lazy" onerror="this.style.display=\\'none\\'" alt="Photo"></div>';
    } else if (gifSrc) {
      mediaBox = '<div class="hof-media-box" onclick="openLightbox(\\'' + gifSrc + '\\')"><img src="' + gifSrc + '" loading="lazy" onerror="this.style.display=\\'none\\'" alt="GIF"></div>';
    }

    const rxBadges = Object.entries((m.reactions || []).reduce((acc, cur) => { acc[cur] = (acc[cur] || 0) + 1; return acc; }, {}))
      .map(([emoji, count]) => '<span class="rx-badge">' + emoji + ' ' + count + '</span>').join('');

    return (
      '<div class="hof-card">' +
        '<div class="hof-top">' +
          '<div class="hof-sender">#' + (i+1) + ' ' + m.sender + '</div>' +
          '<div class="hof-time">' + m.time + '</div>' +
        '</div>' +
        mediaBox +
        (m.content ? '<div class="hof-content">' + m.content + '</div>' : '') +
        '<div class="hof-bottom">' +
          '<div class="hof-reactions">' + rxBadges + '</div>' +
          '<div class="hof-count">🔥 ' + m.count + ' reacts</div>' +
        '</div>' +
      '</div>'
    );
  }).join('');
}

function openModal(name) {
  const p = rawData.participants.find(x => x.name === name);
  if (!p) return;

  const modal = document.getElementById('profileModal');
  const body = document.getElementById('modalBody');
  if (!modal || !body) return;

  const topEmojisHtml = (p.top_emojis && p.top_emojis.length > 0)
    ? p.top_emojis.map(e => '<span class="profile-emoji-pill">' + e.emoji + ' <span class="profile-pill-count">' + e.count + '</span></span>').join('')
    : '<span style="color:var(--text-dim); font-size:0.85rem;">No emojis recorded</span>';

  const topRxRecvHtml = (p.top_reacts_received && p.top_reacts_received.length > 0)
    ? p.top_reacts_received.map(e => '<span class="profile-emoji-pill" style="border-color:rgba(245,158,11,0.35); background:rgba(245,158,11,0.08);">' + e.emoji + ' <span class="profile-pill-count" style="color:#f59e0b;">' + e.count + '</span></span>').join('')
    : '<span style="color:var(--text-dim); font-size:0.85rem;">No reactions recorded</span>';

  const topRxGivenHtml = (p.top_reacts_given && p.top_reacts_given.length > 0)
    ? p.top_reacts_given.map(e => '<span class="profile-emoji-pill" style="border-color:rgba(236,72,153,0.35); background:rgba(236,72,153,0.08);">' + e.emoji + ' <span class="profile-pill-count" style="color:#ec4899;">' + e.count + '</span></span>').join('')
    : '<span style="color:var(--text-dim); font-size:0.85rem;">No reactions given</span>';

  const previewHtml = (p.longest_msg_preview && p.longest_msg_preview.length > 0) ? (
    '<div class="profile-detail-section">' +
      '<h4>📜 Longest Message Sample (' + (p.max_msg_len || 0) + ' words)</h4>' +
      '<div class="profile-quote-box">' + p.longest_msg_preview + '</div>' +
    '</div>'
  ) : '';

  body.innerHTML = 
    '<div class="profile-modal-header">' +
      '<div class="profile-avatar-large">' + p.name.charAt(0) + '</div>' +
      '<div class="profile-title-block">' +
        '<div class="profile-name">' + p.name + '</div>' +
        '<div><span class="profile-archetype-badge">' + (p.archetype || 'Member') + '</span></div>' +
        '<div class="profile-rank-badge">🏆 Rank #' + p.rank + ' Overall • ' + p.percentage + '% of Group Volume (' + (p.active_days_count || 0) + ' active days)</div>' +
      '</div>' +
    '</div>' +

    '<div class="profile-section-heading">💬 Messaging & Volume</div>' +
    '<div class="profile-stats-grid">' +
      '<div class="profile-stat-box"><div class="profile-val">' + p.messages.toLocaleString() + '</div><div class="profile-lbl">Messages Sent</div></div>' +
      '<div class="profile-stat-box"><div class="profile-val">' + p.words.toLocaleString() + '</div><div class="profile-lbl">Words Typed</div></div>' +
      '<div class="profile-stat-box"><div class="profile-val">' + p.avg_words_per_msg + '</div><div class="profile-lbl">Avg Words / Msg</div></div>' +
      '<div class="profile-stat-box"><div class="profile-val">' + (p.chars || 0).toLocaleString() + '</div><div class="profile-lbl">Characters Typed</div></div>' +
      '<div class="profile-stat-box"><div class="profile-val" style="color:#38bdf8;">' + (p.photos || 0) + '</div><div class="profile-lbl">Photos Shared</div></div>' +
      '<div class="profile-stat-box"><div class="profile-val" style="color:#ef4444;">' + (p.unsent || 0) + ' <span style="font-size:0.8rem;color:var(--text-dim);">(' + (p.unsent_pct || 0) + '%)</span></div><div class="profile-lbl">Unsent Messages</div></div>' +
    '</div>' +

    '<div class="profile-section-heading">🔥 Reactions & Clout</div>' +
    '<div class="profile-stats-grid">' +
      '<div class="profile-stat-box"><div class="profile-val" style="color:#f59e0b;">+' + (p.reacts_received || 0).toLocaleString() + '</div><div class="profile-lbl">Reacts Received</div></div>' +
      '<div class="profile-stat-box"><div class="profile-val" style="color:#fbbf24;">' + (p.avg_reacts_per_msg || 0) + '</div><div class="profile-lbl">Avg Reacts / Msg</div></div>' +
      '<div class="profile-stat-box"><div class="profile-val" style="color:#ec4899;">-' + (p.reacts_given || 0).toLocaleString() + '</div><div class="profile-lbl">Reacts Given</div></div>' +
      '<div class="profile-stat-box"><div class="profile-val" style="color:#818cf8;">' + (p.night_msgs || 0).toLocaleString() + ' <span style="font-size:0.8rem;color:var(--text-dim);">(' + (p.night_pct || 0) + '%)</span></div><div class="profile-lbl">Late Night (12-5 AM)</div></div>' +
      '<div class="profile-stat-box"><div class="profile-val" style="color:#c084fc;">' + (p.max_consecutive || 0) + '</div><div class="profile-lbl">Max Solo Streak</div></div>' +
      '<div class="profile-stat-box"><div class="profile-val" style="color:#10b981;">' + (p.starters || 0) + ' / ' + (p.killers || 0) + '</div><div class="profile-lbl">Revived / Ended</div></div>' +
    '</div>' +

    '<div class="profile-section-heading">🎭 Group Quirks & Banter</div>' +
    '<div class="profile-stats-grid">' +
      '<div class="profile-stat-box"><div class="profile-val" style="color:#fbbf24;">' + (p.treat_calls || 0) + ' / ' + (p.kacchi_calls || 0) + '</div><div class="profile-lbl">Treats / Kacchi</div></div>' +
      '<div class="profile-stat-box"><div class="profile-val" style="color:#f97316;">' + (p.panic_score || 0) + '</div><div class="profile-lbl">Academic Panic</div></div>' +
      '<div class="profile-stat-box"><div class="profile-val" style="color:#a855f7;">' + (p.questions || 0) + '</div><div class="profile-lbl">Questions Asked</div></div>' +
      '<div class="profile-stat-box"><div class="profile-val" style="color:#f43f5e;">' + (p.kicked_received || 0) + '</div><div class="profile-lbl">Times Kicked</div></div>' +
      '<div class="profile-stat-box"><div class="profile-val" style="color:#e11d48;">' + (p.rage_quits || 0) + '</div><div class="profile-lbl">Rage Quits</div></div>' +
      '<div class="profile-stat-box"><div class="profile-val" style="color:#10b981;">' + (p.kicks_performed || 0) + '</div><div class="profile-lbl">Kicks Executed</div></div>' +
    '</div>' +

    '<div class="profile-detail-section">' +
      '<h4>😂 Top Emojis Used</h4>' +
      '<div class="profile-emoji-row">' + topEmojisHtml + '</div>' +
    '</div>' +

    '<div class="profile-detail-section">' +
      '<h4>🌟 Top Reactions Received</h4>' +
      '<div class="profile-emoji-row">' + topRxRecvHtml + '</div>' +
    '</div>' +

    '<div class="profile-detail-section">' +
      '<h4>❤️ Top Reactions Given</h4>' +
      '<div class="profile-emoji-row">' + topRxGivenHtml + '</div>' +
    '</div>' +
    previewHtml;

  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  const modal = document.getElementById('profileModal');
  if (modal) {
    modal.classList.remove('active');
  }
  document.body.style.overflow = '';
}

function closeModalDirect(event) {
  if (event && event.target && event.target.id === 'profileModal') {
    closeModal();
  }
}

// ESC Key listener
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape' || e.keyCode === 27) {
    closeModal();
    closeLightbox();
  }
});

function buildSnippets() {
  const p = rawData.participants;
  const court = rawData.funny_details;
  if (!p || p.length === 0) return;

  const courtText = 
'⚔️ === CR MOUMITA\\'S BAN HAMMER & COURT OF JUSTICE === 🔨\\n' +
'\"Amr tay ulta patla jei likhuk tanvir kicked🙃\" — Official Group Decree\\n\\n' +
'🔨 Supreme Executioner (The Ban Hammer):\\n' +
'1. ' + court.ban_hammer_executioners[0].name + ': ' + court.ban_hammer_executioners[0].count + ' kicks (' + Math.round(court.ban_hammer_executioners[0].count / 72 * 100) + '% of all kicks in group history!)\\n' +
'2. ' + court.ban_hammer_executioners[1].name + ': ' + court.ban_hammer_executioners[1].count + ' kicks\\n\\n' +
'💀 Wall of Victims (Most Kicked):\\n' +
'1. ' + court.ban_hammer_victims[0].name + ': ' + court.ban_hammer_victims[0].count + ' times kicked (The Martyr!)\\n' +
'2. ' + court.ban_hammer_victims[1].name + ': ' + court.ban_hammer_victims[1].count + ' times kicked\\n' +
'3. ' + court.ban_hammer_victims[2].name + ': ' + court.ban_hammer_victims[2].count + ' times kicked\\n\\n' +
'🚪 Dramatic Rage Quitters (Left the group):\\n' +
'1. ' + court.rage_quitters[0].name + ': ' + court.rage_quitters[0].count + ' times left\\n' +
'2. ' + court.rage_quitters[1].name + ': ' + court.rage_quitters[1].count + ' times left\\n\\n' +
'😇 The Mercy Giver (Added people back):\\n' +
'1. ' + court.resurrectors[0].name + ': ' + court.resurrectors[0].count + ' adds';

  const snipCourt = document.getElementById('snippet-court');
  if (snipCourt) snipCourt.textContent = courtText;

  const supText = 
'🏆 === ' + rawData.group_title + ' WRAPPED 2026 === 🏆\\n' +
'📅 Timeline: ' + rawData.first_message_time.substring(0,10) + ' to ' + rawData.last_message_time.substring(0,10) + ' (' + rawData.total_days + ' days)\\n' +
'💬 Total Messages: ' + rawData.total_messages.toLocaleString() + ' | Words: ' + rawData.total_words.toLocaleString() + ' | Reactions: ' + rawData.total_reactions.toLocaleString() + '\\n\\n' +
'👑 THE OFFICIAL GROUP AWARDS:\\n' +
'• 🗣️ Supreme Chat Titan: ' + p[0].name + ' (' + p[0].messages.toLocaleString() + ' msgs - ' + p[0].percentage + '% of group!)\\n' +
'• 🔨 Ban Hammer Executioner: ' + court.ban_hammer_executioners[0].name + ' (' + court.ban_hammer_executioners[0].count + ' kicks!)\\n' +
'• 💀 The Unkillable Martyr: ' + court.ban_hammer_victims[0].name + ' (' + court.ban_hammer_victims[0].count + ' times kicked & 9 rage quits!)\\n' +
'• ✍️ Chief Essayist: ' + p.slice().sort((a,b)=>b.words-a.words)[0].name + ' (' + p.slice().sort((a,b)=>b.words-a.words)[0].words.toLocaleString() + ' words)\\n' +
'• 🌟 Clout Sovereign: ' + p.slice().sort((a,b)=>b.reacts_received-a.reacts_received)[0].name + ' (' + p.slice().sort((a,b)=>b.reacts_received-a.reacts_received)[0].reacts_received.toLocaleString() + ' reacts recv)\\n' +
'• 🍖 Treat & Kacchi Emperor: ' + p.slice().sort((a,b)=>b.treat_calls-a.treat_calls)[0].name + ' (' + p.slice().sort((a,b)=>b.treat_calls-a.treat_calls)[0].treat_calls + ' treats & ' + p.slice().sort((a,b)=>b.kacchi_calls-a.kacchi_calls)[0].kacchi_calls + ' kacchi calls!)\\n' +
'• 😭 Emoji Addict: ' + p.slice().sort((a,b)=>b.total_emojis-a.total_emojis)[0].name + ' (' + p.slice().sort((a,b)=>b.total_emojis-a.total_emojis)[0].total_emojis.toLocaleString() + ' emojis)\\n' +
'• ❤️ Hype Master: ' + p.slice().sort((a,b)=>b.reacts_given-a.reacts_given)[0].name + ' (' + p.slice().sort((a,b)=>b.reacts_given-a.reacts_given)[0].reacts_given.toLocaleString() + ' reacts given)\\n' +
'• 🙈 Secret Keeper (Unsent): ' + p.slice().sort((a,b)=>b.unsent-a.unsent)[0].name + ' (' + p.slice().sort((a,b)=>b.unsent-a.unsent)[0].unsent + ' unsent msgs!)\\n' +
'• 🦉 Night Owl (12AM-5AM): ' + p.slice().sort((a,b)=>b.night_msgs-a.night_msgs)[0].name + ' (' + p.slice().sort((a,b)=>b.night_msgs-a.night_msgs)[0].night_msgs + ' night msgs)\\n' +
'• 📸 Shutterbug: ' + p.slice().sort((a,b)=>b.photos-a.photos)[0].name + ' (' + p.slice().sort((a,b)=>b.photos-a.photos)[0].photos + ' photos)\\n' +
'• 📢 Chat CPR Reviver: ' + p.slice().sort((a,b)=>b.starters-a.starters)[0].name + ' (' + p.slice().sort((a,b)=>b.starters-a.starters)[0].starters + ' times revived chat)\\n' +
'• 🛑 Chat Assassin: ' + p.slice().sort((a,b)=>b.killers-a.killers)[0].name + ' (' + p.slice().sort((a,b)=>b.killers-a.killers)[0].killers + ' times ended chat)\\n' +
'• 🍿 Monologue Record: ' + p.slice().sort((a,b)=>b.max_consecutive-a.max_consecutive)[0].name + ' (' + p.slice().sort((a,b)=>b.max_consecutive-a.max_consecutive)[0].max_consecutive + ' msgs in a row)';

  const snipSup = document.getElementById('snippet-superlatives');
  if (snipSup) snipSup.textContent = supText;

  const banterText = 
'🍖 === THE BANTER & PANIC SYNDICATE 2026 === 📚\\n\\n' +
'🍖 Treat & Kacchi Syndicate (Top Treat Demanders):\\n' +
'1. ' + p.slice().sort((a,b)=>b.treat_calls-a.treat_calls)[0].name + ': ' + p.slice().sort((a,b)=>b.treat_calls-a.treat_calls)[0].treat_calls + ' treat calls & ' + p.slice().sort((a,b)=>b.kacchi_calls-a.kacchi_calls)[0].kacchi_calls + ' kacchi demands\\n' +
'2. ' + p.slice().sort((a,b)=>b.treat_calls-a.treat_calls)[1].name + ': ' + p.slice().sort((a,b)=>b.treat_calls-a.treat_calls)[1].treat_calls + ' treat calls\\n' +
'3. ' + p.slice().sort((a,b)=>b.treat_calls-a.treat_calls)[2].name + ': ' + p.slice().sort((a,b)=>b.treat_calls-a.treat_calls)[2].treat_calls + ' treat calls\\n\\n' +
'📚 Academic Panic Board (Exam / Sir / Quiz / Lab):\\n' +
'1. ' + p.slice().sort((a,b)=>b.panic_score-a.panic_score)[0].name + ': ' + p.slice().sort((a,b)=>b.panic_score-a.panic_score)[0].panic_score + ' panic triggers\\n' +
'2. ' + p.slice().sort((a,b)=>b.panic_score-a.panic_score)[1].name + ': ' + p.slice().sort((a,b)=>b.panic_score-a.panic_score)[1].panic_score + ' panic triggers\\n' +
'3. ' + p.slice().sort((a,b)=>b.panic_score-a.panic_score)[2].name + ': ' + p.slice().sort((a,b)=>b.panic_score-a.panic_score)[2].panic_score + ' panic triggers';

  const snipBanter = document.getElementById('snippet-banter');
  if (snipBanter) snipBanter.textContent = banterText;

  const top10Text = 
'📊 === TOP 10 CHATTERS (MESSAGES) === 📊\\n' +
p.slice(0, 10).map((u, i) => (i+1) + '. ' + u.name + ': ' + u.messages.toLocaleString() + ' msgs (' + u.percentage + '%) | ' + u.words.toLocaleString() + ' words').join('\\n') + '\\n\\n' +
'📈 Group Total: ' + rawData.total_messages.toLocaleString() + ' messages';

  const snipTop10 = document.getElementById('snippet-top10');
  if (snipTop10) snipTop10.textContent = top10Text;

  const emojiText = 
'😭 === EMOJI & CLOUT LEADERBOARD === 🌟\\n\\n' +
'Top Emoji Spammers:\\n' +
p.slice().sort((a,b)=>b.total_emojis-a.total_emojis).slice(0,5).map((u, i) => (i+1) + '. ' + u.name + ': ' + u.total_emojis.toLocaleString() + ' emojis (Top: ' + u.top_emojis.map(e=>e.emoji).join(' ') + ')').join('\\n') + '\\n\\n' +
'Most Reacted To (Clout Kings/Queens):\\n' +
p.slice().sort((a,b)=>b.reacts_received-a.reacts_received).slice(0,5).map((u, i) => (i+1) + '. ' + u.name + ': ' + u.reacts_received.toLocaleString() + ' reacts received').join('\\n') + '\\n\\n' +
'Most Generous Reactors:\\n' +
p.slice().sort((a,b)=>b.reacts_given-a.reacts_given).slice(0,5).map((u, i) => (i+1) + '. ' + u.name + ': ' + u.reacts_given.toLocaleString() + ' reacts given').join('\\n');

  const snipEmojis = document.getElementById('snippet-emojis');
  if (snipEmojis) snipEmojis.textContent = emojiText;
}

function copySnippet(elementId, btn) {
  const elem = document.getElementById(elementId);
  if (!elem) return;
  const targetBtn = btn || event?.target;
  navigator.clipboard.writeText(elem.textContent).then(() => {
    if (targetBtn) {
      const originalText = targetBtn.textContent;
      targetBtn.textContent = '✅ Copied to Clipboard!';
      targetBtn.style.background = '#10b981';
      targetBtn.style.color = '#fff';
      setTimeout(() => {
        targetBtn.textContent = originalText;
        targetBtn.style.background = '';
        targetBtn.style.color = '';
      }, 2000);
    }
  }).catch(() => {
    if (targetBtn) targetBtn.textContent = '❌ Failed to copy';
  });
}

function initCharts() {
  if (typeof Chart === 'undefined') return;

  const ctxH = document.getElementById('hourlyChart');
  if (ctxH && !ctxH.chartInstance) {
    ctxH.chartInstance = new Chart(ctxH, {
      type: 'bar',
      data: {
        labels: Array.from({ length: 24 }, (_, i) => (i < 10 ? '0' + i : i) + ':00'),
        datasets: [{
          label: 'Messages',
          data: rawData.hourly_distribution,
          backgroundColor: 'rgba(59, 130, 246, 0.75)',
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
        }
      }
    });
  }

  const ctxD = document.getElementById('dowChart');
  if (ctxD && !ctxD.chartInstance) {
    ctxD.chartInstance = new Chart(ctxD, {
      type: 'bar',
      data: {
        labels: rawData.day_of_week_distribution.map(d => d.day),
        datasets: [{
          label: 'Messages',
          data: rawData.day_of_week_distribution.map(d => d.count),
          backgroundColor: 'rgba(6, 182, 212, 0.75)',
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
        }
      }
    });
  }

  const ctxM = document.getElementById('monthlyChart');
  if (ctxM && !ctxM.chartInstance) {
    ctxM.chartInstance = new Chart(ctxM, {
      type: 'bar',
      data: {
        labels: rawData.monthly_distribution.map(d => d.month),
        datasets: [{
          label: 'Messages',
          data: rawData.monthly_distribution.map(d => d.count),
          backgroundColor: 'rgba(139, 92, 246, 0.75)',
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
        }
      }
    });
  }

  const ctxT = document.getElementById('topSendersChart');
  if (ctxT && !ctxT.chartInstance) {
    const top10 = rawData.participants.slice(0, 10);
    ctxT.chartInstance = new Chart(ctxT, {
      type: 'bar',
      data: {
        labels: top10.map(p => p.name.split(' ')[0]),
        datasets: [{
          label: 'Messages',
          data: top10.map(p => p.messages),
          backgroundColor: 'rgba(236, 72, 153, 0.75)',
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
        }
      }
    });
  }

  const ctxE = document.getElementById('emojisChart');
  if (ctxE && !ctxE.chartInstance) {
    const topEmojis = rawData.top_emojis.slice(0, 8);
    ctxE.chartInstance = new Chart(ctxE, {
      type: 'doughnut',
      data: {
        labels: topEmojis.map(e => e.emoji),
        datasets: [{
          data: topEmojis.map(e => e.count),
          backgroundColor: ['#3b82f6', '#06b6d4', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#f43f5e', '#64748b'],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right',
            labels: { color: '#cbd5e1', font: { family: "'Plus Jakarta Sans', sans-serif" } }
          }
        }
      }
    });
  }

  const ctxR = document.getElementById('reactionsChart');
  if (ctxR && !ctxR.chartInstance) {
    const topRx = rawData.top_reaction_types.slice(0, 6);
    ctxR.chartInstance = new Chart(ctxR, {
      type: 'pie',
      data: {
        labels: topRx.map(r => r.emoji),
        datasets: [{
          data: topRx.map(r => r.count),
          backgroundColor: ['#f59e0b', '#ec4899', '#3b82f6', '#10b981', '#8b5cf6', '#06b6d4'],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right',
            labels: { color: '#cbd5e1', font: { family: "'Plus Jakarta Sans', sans-serif" } }
          }
        }
      }
    });
  }
}

function safeInit() {
  console.log('Initializing CSEDU-32 Dashboard...');
  try { buildSuperlatives(); } catch(e) { console.error('Superlatives error:', e); }
  try { renderGallery(); } catch(e) { console.error('Gallery error:', e); }
  try { renderTable(rawData.participants); } catch(e) { console.error('Table error:', e); }
  try { buildHallOfFame(); } catch(e) { console.error('HallOfFame error:', e); }
  try { buildSnippets(); } catch(e) { console.error('Snippets error:', e); }
  try {
    if (typeof Chart !== 'undefined') {
      initCharts();
    } else {
      setTimeout(() => { try { if (typeof Chart !== 'undefined') initCharts(); } catch(e){} }, 300);
    }
  } catch(e) { console.error('Charts error:', e); }
}

if (document.readyState === 'loading') {
  window.addEventListener('DOMContentLoaded', safeInit);
} else {
  safeInit();
}
"""

# 3. Build index.html
html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>লৌহপূর্ণ খামার (কসাই-৩২💻) - Group Chat Analytics & Meme Vault</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap" media="print" onload="this.media='all'">
  <style>
    :root {
      --bg-dark: #090d16;
      --card-bg: rgba(17, 24, 39, 0.75);
      --card-border: rgba(255, 255, 255, 0.08);
      --card-hover: rgba(30, 41, 59, 0.9);
      --accent-blue: #3b82f6;
      --accent-cyan: #06b6d4;
      --accent-purple: #8b5cf6;
      --accent-pink: #ec4899;
      --accent-amber: #f59e0b;
      --accent-emerald: #10b981;
      --accent-rose: #f43f5e;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --font-main: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      background-color: var(--bg-dark);
      background-image: 
        radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.15) 0px, transparent 50%),
        radial-gradient(at 100% 0%, rgba(139, 92, 246, 0.15) 0px, transparent 50%),
        radial-gradient(at 50% 100%, rgba(6, 182, 212, 0.1) 0px, transparent 50%);
      background-attachment: fixed;
      color: var(--text-main);
      font-family: var(--font-main);
      line-height: 1.5;
      min-height: 100vh;
      padding: 2rem 1rem;
    }

    .container {
      max-width: 1400px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 2rem;
    }

    /* Header */
    .header {
      background: var(--card-bg);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid var(--card-border);
      border-radius: 24px;
      padding: 2.5rem 2rem;
      position: relative;
      overflow: hidden;
      box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.6);
    }

    .header::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan), var(--accent-purple), var(--accent-pink));
    }

    .header-top {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      flex-wrap: wrap;
      gap: 1rem;
      margin-bottom: 1.5rem;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      background: rgba(59, 130, 246, 0.15);
      color: #60a5fa;
      border: 1px solid rgba(59, 130, 246, 0.3);
      padding: 0.35rem 0.85rem;
      border-radius: 999px;
      font-size: 0.825rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .title {
      font-size: 2.5rem;
      font-weight: 800;
      letter-spacing: -0.03em;
      background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-top: 0.5rem;
      line-height: 1.2;
    }

    .subtitle {
      color: var(--text-muted);
      font-size: 1rem;
      margin-top: 0.5rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      flex-wrap: wrap;
    }

    .quick-stats-bar {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
      gap: 1rem;
      margin-top: 2rem;
      padding-top: 1.5rem;
      border-top: 1px solid var(--card-border);
    }

    .stat-box {
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 1rem 1.25rem;
      transition: transform 0.2s, background 0.2s;
    }

    .stat-box:hover {
      transform: translateY(-3px);
      background: rgba(255, 255, 255, 0.05);
    }

    .stat-val {
      font-size: 1.75rem;
      font-weight: 800;
      font-family: var(--font-mono);
      color: #fff;
    }

    .stat-lbl {
      color: var(--text-dim);
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      font-weight: 700;
      margin-top: 0.25rem;
    }

    .section-title {
      font-size: 1.5rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      display: flex;
      align-items: center;
      gap: 0.75rem;
      margin-bottom: 1.25rem;
    }

    .section-title span.icon {
      font-size: 1.5rem;
    }

    /* Tabs */
    .tabs-nav {
      display: flex;
      gap: 0.5rem;
      background: rgba(15, 23, 42, 0.75);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      padding: 0.5rem;
      border-radius: 18px;
      border: 1px solid var(--card-border);
      overflow-x: auto;
      position: sticky;
      top: 1rem;
      z-index: 40;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }

    .tabs-nav::-webkit-scrollbar {
      height: 4px;
    }

    .tabs-nav::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.15);
      border-radius: 4px;
    }

    .tab-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 0.7rem 1.25rem;
      border-radius: 12px;
      font-family: var(--font-main);
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.2s;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }

    .tab-btn:hover {
      color: #fff;
      background: rgba(255, 255, 255, 0.06);
    }

    .tab-btn.active {
      background: linear-gradient(135deg, var(--accent-blue), #2563eb);
      color: #fff;
      box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);
    }

    .tab-pane {
      display: none;
    }

    .tab-pane.active {
      display: block;
    }

    /* Awards Grid */
    .awards-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(310px, 1fr));
      gap: 1.25rem;
    }

    .award-card {
      background: var(--card-bg);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid var(--card-border);
      border-radius: 20px;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: all 0.25s ease;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }

    .award-card:hover {
      transform: translateY(-4px);
      border-color: rgba(255, 255, 255, 0.2);
      box-shadow: 0 20px 30px -10px rgba(0, 0, 0, 0.5);
    }

    .award-header {
      display: flex;
      align-items: flex-start;
      gap: 0.85rem;
      margin-bottom: 1rem;
    }

    .award-icon {
      font-size: 2.2rem;
      line-height: 1;
      padding: 0.5rem;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 14px;
      border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .award-category {
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--text-dim);
    }

    .award-title {
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--text-main);
    }

    .award-winner {
      font-size: 1.25rem;
      font-weight: 800;
      color: #60a5fa;
      margin-top: 0.25rem;
    }

    .award-stat {
      font-size: 0.9rem;
      color: var(--text-muted);
      margin-top: 0.4rem;
    }

    .award-highlight {
      font-family: var(--font-mono);
      font-weight: 700;
      color: #38bdf8;
    }

    /* Syndicate Cards */
    .syndicate-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2rem;
    }

    .syndicate-card {
      background: var(--card-bg);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid var(--card-border);
      border-radius: 20px;
      padding: 1.5rem;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }

    .syndicate-card h3 {
      font-size: 1.15rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .syndicate-card p.desc {
      color: var(--text-dim);
      font-size: 0.85rem;
      margin-bottom: 1.25rem;
    }

    .syndicate-list {
      display: flex;
      flex-direction: column;
      gap: 0.65rem;
    }

    .syndicate-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: rgba(255, 255, 255, 0.03);
      padding: 0.75rem 1rem;
      border-radius: 12px;
      border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .syndicate-item .name {
      font-weight: 600;
      font-size: 0.9rem;
    }

    .syndicate-item .badge-count {
      font-family: var(--font-mono);
      font-weight: 700;
      color: #38bdf8;
      background: rgba(56, 189, 248, 0.1);
      padding: 0.2rem 0.6rem;
      border-radius: 8px;
    }

    /* Media Gallery & Vault */
    .filter-chips {
      display: flex;
      gap: 0.5rem;
      margin-bottom: 1.5rem;
      flex-wrap: wrap;
    }

    .filter-chip {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--card-border);
      color: var(--text-muted);
      padding: 0.45rem 1rem;
      border-radius: 999px;
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }

    .filter-chip:hover, .filter-chip.active {
      background: var(--accent-cyan);
      color: #000;
      font-weight: 700;
      border-color: var(--accent-cyan);
    }

    .gallery-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
      gap: 1.25rem;
    }

    .gallery-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 18px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: all 0.25s ease;
      box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.4);
    }

    .gallery-card:hover {
      transform: translateY(-4px);
      border-color: rgba(255, 255, 255, 0.25);
    }

    .gallery-media-wrapper {
      position: relative;
      width: 100%;
      background: #020617;
      min-height: 220px;
      max-height: 300px;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
    }

    .gallery-media-wrapper img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.3s;
      display: block;
    }

    .gallery-card:hover .gallery-media-wrapper img {
      transform: scale(1.03);
    }

    .gallery-info {
      padding: 1rem 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    .gallery-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .gallery-sender {
      font-weight: 700;
      font-size: 0.9rem;
      color: #60a5fa;
    }

    .gallery-time {
      font-size: 0.75rem;
      color: var(--text-dim);
    }

    .gallery-caption {
      font-size: 0.85rem;
      color: #cbd5e1;
      white-space: pre-wrap;
      word-break: break-word;
    }

    .gallery-rx-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 0.5rem;
      padding-top: 0.5rem;
      border-top: 1px solid rgba(255, 255, 255, 0.05);
    }

    .gallery-reactions {
      display: flex;
      gap: 0.25rem;
      flex-wrap: wrap;
    }

    .rx-badge {
      background: rgba(255, 255, 255, 0.08);
      padding: 0.2rem 0.45rem;
      border-radius: 6px;
      font-size: 0.8rem;
    }

    .rx-total {
      font-family: var(--font-mono);
      font-weight: 800;
      font-size: 0.95rem;
      color: #ec4899;
    }

    /* Leaderboard Table */
    .table-container {
      background: var(--card-bg);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid var(--card-border);
      border-radius: 20px;
      overflow: hidden;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }

    .table-header-controls {
      padding: 1.25rem 1.5rem;
      border-bottom: 1px solid var(--card-border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
    }

    .search-input {
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid var(--card-border);
      color: #fff;
      padding: 0.6rem 1rem;
      border-radius: 10px;
      font-family: var(--font-main);
      font-size: 0.9rem;
      width: 280px;
      outline: none;
      transition: border 0.2s;
    }

    .search-input:focus {
      border-color: var(--accent-blue);
    }

    .table-scroll {
      overflow-x: auto;
      max-height: 700px;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.9rem;
    }

    th {
      background: rgba(15, 23, 42, 0.95);
      padding: 0.85rem 1rem;
      color: var(--text-dim);
      font-weight: 700;
      text-transform: uppercase;
      font-size: 0.75rem;
      letter-spacing: 0.05em;
      position: sticky;
      top: 0;
      z-index: 10;
      cursor: pointer;
      user-select: none;
      white-space: nowrap;
      transition: color 0.15s;
    }

    th:hover {
      color: #fff;
      background: rgba(255, 255, 255, 0.05);
    }

    td {
      padding: 0.85rem 1rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
      white-space: nowrap;
    }

    .participant-row {
      cursor: pointer;
      transition: background 0.15s ease;
    }

    .participant-row:hover td {
      background: rgba(59, 130, 246, 0.08);
    }

    .user-cell {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }

    .user-avatar {
      width: 34px;
      height: 34px;
      border-radius: 10px;
      background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan));
      color: #fff;
      font-weight: 800;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.9rem;
      flex-shrink: 0;
    }

    .user-name-wrapper {
      display: flex;
      flex-direction: column;
    }

    .user-name {
      font-weight: 700;
      color: #fff;
      font-size: 0.925rem;
      transition: color 0.15s;
    }

    .participant-row:hover .user-name {
      color: #60a5fa;
      text-decoration: underline;
    }

    .user-sub {
      font-size: 0.75rem;
      color: var(--text-dim);
    }

    .rank-cell {
      font-family: var(--font-mono);
      font-weight: 700;
      color: var(--text-dim);
      width: 45px;
    }

    .rank-1 { color: #fbbf24 !important; font-weight: 800; }
    .rank-2 { color: #cbd5e1 !important; font-weight: 800; }
    .rank-3 { color: #d97706 !important; font-weight: 800; }

    .mono-cell {
      font-family: var(--font-mono);
    }

    .archetype-pill {
      font-size: 0.78rem;
      padding: 0.2rem 0.55rem;
      border-radius: 6px;
      background: rgba(139, 92, 246, 0.12);
      border: 1px solid rgba(139, 92, 246, 0.25);
      color: #c084fc;
      font-weight: 600;
      white-space: nowrap;
    }

    .emoji-pill {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.08);
      padding: 0.2rem 0.5rem;
      border-radius: 6px;
      font-size: 0.8rem;
      font-family: var(--font-mono);
    }

    .view-profile-btn {
      background: rgba(59, 130, 246, 0.12);
      border: 1px solid rgba(59, 130, 246, 0.3);
      color: #60a5fa;
      padding: 0.35rem 0.75rem;
      border-radius: 8px;
      font-size: 0.8rem;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.2s;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
    }

    .view-profile-btn:hover {
      background: var(--accent-blue);
      color: #fff;
      box-shadow: 0 4px 10px rgba(59, 130, 246, 0.4);
    }

    .sort-icon {
      color: var(--accent-cyan);
      font-size: 0.75rem;
    }

    /* Charts Grid */
    .charts-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
      gap: 1.5rem;
    }

    .chart-card {
      background: var(--card-bg);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid var(--card-border);
      border-radius: 20px;
      padding: 1.5rem;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }

    .chart-card h3 {
      font-size: 1.1rem;
      font-weight: 700;
      margin-bottom: 1.25rem;
      color: #fff;
    }

    .chart-container {
      position: relative;
      height: 260px;
      width: 100%;
    }

    /* Hall of Fame */
    .hof-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 1.25rem;
    }

    .hof-card {
      background: var(--card-bg);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid var(--card-border);
      border-radius: 18px;
      padding: 1.35rem;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 1rem;
      transition: all 0.2s;
    }

    .hof-card:hover {
      border-color: rgba(255, 255, 255, 0.2);
      transform: translateY(-3px);
    }

    .hof-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .hof-sender {
      font-weight: 700;
      font-size: 1rem;
      color: #60a5fa;
    }

    .hof-time {
      font-size: 0.75rem;
      color: var(--text-dim);
    }

    .hof-media-box {
      width: 100%;
      border-radius: 12px;
      overflow: hidden;
      background: #020617;
      margin-bottom: 0.5rem;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
    }

    .hof-media-box img {
      width: 100%;
      max-height: 260px;
      object-fit: contain;
      display: block;
    }

    .hof-content {
      background: rgba(15, 23, 42, 0.6);
      padding: 1rem;
      border-radius: 12px;
      font-size: 0.95rem;
      color: #f1f5f9;
      line-height: 1.4;
      white-space: pre-wrap;
      word-break: break-word;
    }

    .hof-bottom {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .hof-reactions {
      display: flex;
      gap: 0.35rem;
      flex-wrap: wrap;
    }

    .hof-count {
      font-family: var(--font-mono);
      font-weight: 800;
      font-size: 1.1rem;
      color: #ec4899;
      display: flex;
      align-items: center;
      gap: 0.3rem;
    }

    /* Share snippets */
    .share-box {
      background: var(--card-bg);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid var(--card-border);
      border-radius: 20px;
      padding: 1.5rem;
      margin-top: 1rem;
    }

    .snippet-pre {
      background: #090d16;
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 1.25rem;
      color: #a5f3fc;
      font-family: var(--font-mono);
      font-size: 0.85rem;
      line-height: 1.6;
      white-space: pre-wrap;
      overflow-x: auto;
      margin-bottom: 1rem;
    }

    .copy-btn {
      background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan));
      border: none;
      color: #fff;
      padding: 0.65rem 1.35rem;
      border-radius: 10px;
      font-family: var(--font-main);
      font-size: 0.9rem;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      transition: opacity 0.2s;
    }

    .copy-btn:hover {
      opacity: 0.9;
    }

    /* Profile Modal Popup */
    .modal-backdrop {
      display: none;
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(4, 7, 14, 0.85);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      z-index: 1000;
      justify-content: center;
      align-items: center;
      padding: 1.5rem 1rem;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .modal-backdrop.active {
      display: flex !important;
      opacity: 1;
      pointer-events: auto;
    }

    .modal-card {
      background: linear-gradient(145deg, rgba(17, 24, 39, 0.96), rgba(15, 23, 42, 0.98));
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 24px;
      max-width: 680px;
      width: 100%;
      max-height: 88vh;
      overflow-y: auto;
      padding: 2rem;
      position: relative;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.85), 0 0 0 1px rgba(255, 255, 255, 0.05);
      transform: scale(0.94) translateY(10px);
      transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .modal-backdrop.active .modal-card {
      transform: scale(1) translateY(0);
    }

    .close-modal {
      position: absolute;
      top: 1.25rem;
      right: 1.25rem;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.1);
      color: var(--text-muted);
      width: 36px;
      height: 36px;
      border-radius: 50%;
      font-size: 1.4rem;
      line-height: 1;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s;
      z-index: 10;
    }

    .close-modal:hover {
      background: rgba(239, 68, 68, 0.2);
      border-color: rgba(239, 68, 68, 0.4);
      color: #ef4444;
      transform: rotate(90deg);
    }

    .profile-modal-header {
      display: flex;
      align-items: center;
      gap: 1.25rem;
      padding-bottom: 1.5rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      margin-bottom: 1.25rem;
    }

    .profile-avatar-large {
      width: 64px;
      height: 64px;
      border-radius: 20px;
      background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
      color: #fff;
      font-size: 1.8rem;
      font-weight: 800;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 8px 20px -4px rgba(59, 130, 246, 0.4);
      flex-shrink: 0;
    }

    .profile-title-block {
      flex: 1;
      min-width: 0;
    }

    .profile-name {
      font-size: 1.5rem;
      font-weight: 800;
      color: #fff;
      line-height: 1.2;
      word-break: break-word;
    }

    .profile-archetype-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      background: rgba(139, 92, 246, 0.15);
      border: 1px solid rgba(139, 92, 246, 0.35);
      color: #c084fc;
      padding: 0.25rem 0.75rem;
      border-radius: 999px;
      font-size: 0.8rem;
      font-weight: 700;
      margin-top: 0.4rem;
    }

    .profile-rank-badge {
      color: var(--text-muted);
      font-size: 0.825rem;
      font-weight: 500;
      margin-top: 0.35rem;
    }

    .profile-section-heading {
      font-size: 0.85rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--text-dim);
      margin: 1.25rem 0 0.75rem 0;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }

    .profile-stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
      gap: 0.75rem;
    }

    .profile-stat-box {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 14px;
      padding: 0.85rem 1rem;
      display: flex;
      flex-direction: column;
      justify-content: center;
      transition: background 0.2s, transform 0.2s;
    }

    .profile-stat-box:hover {
      background: rgba(255, 255, 255, 0.06);
      transform: translateY(-2px);
    }

    .profile-val {
      font-family: var(--font-mono);
      font-size: 1.2rem;
      font-weight: 800;
      color: #fff;
      line-height: 1.2;
    }

    .profile-lbl {
      font-size: 0.7rem;
      font-weight: 600;
      color: var(--text-dim);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-top: 0.3rem;
    }

    .profile-detail-section {
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 16px;
      padding: 1.15rem;
      margin-top: 1rem;
    }

    .profile-detail-section h4 {
      font-size: 0.85rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--text-dim);
      margin-bottom: 0.75rem;
    }

    .profile-emoji-row {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }

    .profile-emoji-pill {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.08);
      padding: 0.35rem 0.75rem;
      border-radius: 999px;
      font-size: 0.95rem;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
    }

    .profile-pill-count {
      color: var(--text-dim);
      font-size: 0.75rem;
      font-family: var(--font-mono);
      font-weight: 700;
    }

    .profile-quote-box {
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 10px;
      padding: 0.85rem;
      font-size: 0.85rem;
      color: #cbd5e1;
      line-height: 1.5;
      word-break: break-all;
    }

    /* Lightbox Modal */
    .lightbox-modal {
      display: none;
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0, 0, 0, 0.94);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      z-index: 2000;
      justify-content: center;
      align-items: center;
      padding: 1.5rem;
      flex-direction: column;
      opacity: 0;
      transition: opacity 0.2s ease;
    }

    .lightbox-modal.active {
      display: flex !important;
      opacity: 1;
    }

    .lightbox-img {
      max-width: 90vw;
      max-height: 85vh;
      object-fit: contain;
      border-radius: 12px;
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.9);
    }

    .lightbox-close {
      position: absolute;
      top: 1.5rem;
      right: 1.5rem;
      background: rgba(255, 255, 255, 0.15);
      border: 1px solid rgba(255, 255, 255, 0.2);
      color: #fff;
      width: 44px;
      height: 44px;
      border-radius: 50%;
      font-size: 1.75rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s;
    }

    .lightbox-close:hover {
      background: rgba(239, 68, 68, 0.3);
      color: #ef4444;
    }

    /* Responsive */
    @media (max-width: 768px) {
      body { padding: 1rem 0.5rem; }
      .header { padding: 1.5rem 1.25rem; border-radius: 18px; }
      .title { font-size: 1.85rem; }
      .search-input { width: 100%; }
      .syndicate-grid { grid-template-columns: 1fr; }
      .charts-grid { grid-template-columns: 1fr; }
      .modal-card { padding: 1.25rem; }
      .profile-avatar-large { width: 50px; height: 50px; font-size: 1.4rem; }
      .profile-name { font-size: 1.25rem; }
    }

    footer {
      text-align: center;
      color: var(--text-dim);
      font-size: 0.85rem;
      margin-top: 3rem;
      padding-top: 2rem;
      border-top: 1px solid var(--card-border);
    }
  </style>
</head>
<body>

<div class="container">
  
  <!-- Header -->
  <header class="header">
    <div class="header-top">
      <div>
        <div class="badge">🔥 Group Chat Wrapped 2026</div>
        <h1 class="title">লৌহপূর্ণ খামার (কসাই-৩২💻)</h1>
        <div class="subtitle">
          <span>📅 2026-02-26 to 2026-08-12</span>
          <span>•</span>
          <span>⏳ 168 Days of Nonstop Banter</span>
          <span>•</span>
          <span>👥 55 Active Members</span>
        </div>
      </div>
    </div>

    <div class="quick-stats-bar">
      <div class="stat-box">
        <div class="stat-val">53,672</div>
        <div class="stat-lbl">Total Messages</div>
      </div>
      <div class="stat-box">
        <div class="stat-val">297,543</div>
        <div class="stat-lbl">Words Spoken</div>
      </div>
      <div class="stat-box">
        <div class="stat-val">16,713</div>
        <div class="stat-lbl">Reactions Exchanged</div>
      </div>
      <div class="stat-box">
        <div class="stat-val">2,729</div>
        <div class="stat-lbl">Photos Shared</div>
      </div>
      <div class="stat-box">
        <div class="stat-val">866</div>
        <div class="stat-lbl">Unsent Regrets</div>
      </div>
      <div class="stat-box">
        <div class="stat-val">319.5</div>
        <div class="stat-lbl">Avg Msgs / Day</div>
      </div>
    </div>
  </header>

  <!-- Navigation Tabs -->
  <nav class="tabs-nav">
    <button class="tab-btn active" onclick="switchTab('awards')">🏆 Group Superlatives</button>
    <button class="tab-btn" onclick="switchTab('court')">⚔️ CR Moumita's Ban Hammer (61 Kicks!)</button>
    <button class="tab-btn" onclick="switchTab('banter')">🍖 The Banter & Panic Syndicate</button>
    <button class="tab-btn" onclick="switchTab('gallery')">📸 Meme & Photo Vault (60 Items)</button>
    <button class="tab-btn" onclick="switchTab('leaderboard')">📊 Full Leaderboard (55 members)</button>
    <button class="tab-btn" onclick="switchTab('charts')">📈 Activity Charts</button>
    <button class="tab-btn" onclick="switchTab('halloffame')">🌟 Hall of Fame</button>
    <button class="tab-btn" onclick="switchTab('duos')">❤️ Best Hype Duos</button>
    <button class="tab-btn" onclick="switchTab('share')">📋 Copy for Messenger</button>
  </nav>

  <!-- Tab 1: Superlatives & Awards -->
  <div id="tab-awards" class="tab-pane active">
    <div class="section-title">
      <span class="icon">👑</span>
      <span>Official Group Chat Superlatives</span>
    </div>
    <div class="awards-grid" id="awards-container"></div>
  </div>

  <!-- Tab 2: CR Moumita's Ban Hammer & Court of Justice -->
  <div id="tab-court" class="tab-pane">
    <div class="section-title">
      <span class="icon">⚔️</span>
      <span>CR Moumita's Court of Justice & The Ban Hammer</span>
    </div>
    <p style="color:var(--text-muted); margin-bottom:1.5rem;">"Amr tay ulta patla jei likhuk tanvir kicked🙃" — Official Group Decree</p>
    
    <div class="syndicate-grid">
      <!-- Executioner Card -->
      <div class="syndicate-card" style="border-color: rgba(244, 63, 94, 0.3);">
        <h3 style="color:#f43f5e;">🔨 The Supreme Executioners (Kicks Performed)</h3>
        <p class="desc">Who wielded the admin power and purged defying members</p>
        <div class="syndicate-list">
          <div class='syndicate-item'><span class='name'>1. Jannatul Ferdous Moumita</span><span class='badge-count' style='color:#f43f5e; background:rgba(244,63,94,0.15);'>61 kicks</span></div><div class='syndicate-item'><span class='name'>2. Md Nabil Hasan</span><span class='badge-count' style='color:#f43f5e; background:rgba(244,63,94,0.15);'>10 kicks</span></div><div class='syndicate-item'><span class='name'>3. Anamul Haque Tanvir</span><span class='badge-count' style='color:#f43f5e; background:rgba(244,63,94,0.15);'>1 kicks</span></div>
        </div>
      </div>

      <!-- Victims Card -->
      <div class="syndicate-card" style="border-color: rgba(236, 72, 153, 0.3);">
        <h3 style="color:#ec4899;">💀 The Wall of Victims (Most Kicked Members)</h3>
        <p class="desc">Those who dared to speak up and paid the ultimate price</p>
        <div class="syndicate-list">
          <div class='syndicate-item'><span class='name'>1. Anamul Haque Tanvir</span><span class='badge-count' style='color:#ec4899; background:rgba(236,72,153,0.15);'>34 times kicked</span></div><div class='syndicate-item'><span class='name'>2. Abshary Jahin</span><span class='badge-count' style='color:#ec4899; background:rgba(236,72,153,0.15);'>18 times kicked</span></div><div class='syndicate-item'><span class='name'>3. Junayed Ahmed Saad</span><span class='badge-count' style='color:#ec4899; background:rgba(236,72,153,0.15);'>5 times kicked</span></div><div class='syndicate-item'><span class='name'>4. Taha Yasin</span><span class='badge-count' style='color:#ec4899; background:rgba(236,72,153,0.15);'>2 times kicked</span></div><div class='syndicate-item'><span class='name'>5. MD Anik Ahmed</span><span class='badge-count' style='color:#ec4899; background:rgba(236,72,153,0.15);'>2 times kicked</span></div><div class='syndicate-item'><span class='name'>6. Saiful Islam</span><span class='badge-count' style='color:#ec4899; background:rgba(236,72,153,0.15);'>1 times kicked</span></div>
        </div>
      </div>

      <!-- Rage Quitters Card -->
      <div class="syndicate-card">
        <h3>🚪 The Rage Quitters Club (Left on Their Own)</h3>
        <p class="desc">Members who dramatically left the group in protest</p>
        <div class="syndicate-list">
          <div class='syndicate-item'><span class='name'>1. Anamul Haque Tanvir</span><span class='badge-count' style='color:#a855f7; background:rgba(168,85,247,0.15);'>9 rage quits</span></div><div class='syndicate-item'><span class='name'>2. Md Nabil Hasan</span><span class='badge-count' style='color:#a855f7; background:rgba(168,85,247,0.15);'>5 rage quits</span></div><div class='syndicate-item'><span class='name'>3. Jannatul Ferdous Moumita</span><span class='badge-count' style='color:#a855f7; background:rgba(168,85,247,0.15);'>3 rage quits</span></div><div class='syndicate-item'><span class='name'>4. Purnendu Banik</span><span class='badge-count' style='color:#a855f7; background:rgba(168,85,247,0.15);'>2 rage quits</span></div><div class='syndicate-item'><span class='name'>5. MD Anik Ahmed</span><span class='badge-count' style='color:#a855f7; background:rgba(168,85,247,0.15);'>2 rage quits</span></div>
        </div>
      </div>

      <!-- Resurrectors Card -->
      <div class="syndicate-card">
        <h3>😇 The Resurrectors (Added People Back)</h3>
        <p class="desc">Who brought the banished souls back from exile</p>
        <div class="syndicate-list">
          <div class='syndicate-item'><span class='name'>1. Jannatul Ferdous Moumita</span><span class='badge-count' style='color:#10b981; background:rgba(16,185,129,0.15);'>73 adds</span></div><div class='syndicate-item'><span class='name'>2. Md Nabil Hasan</span><span class='badge-count' style='color:#10b981; background:rgba(16,185,129,0.15);'>38 adds</span></div><div class='syndicate-item'><span class='name'>3. Hamim Ashab</span><span class='badge-count' style='color:#10b981; background:rgba(16,185,129,0.15);'>3 adds</span></div><div class='syndicate-item'><span class='name'>4. Rudrojit Sarkar</span><span class='badge-count' style='color:#10b981; background:rgba(16,185,129,0.15);'>3 adds</span></div><div class='syndicate-item'><span class='name'>5. Aditi</span><span class='badge-count' style='color:#10b981; background:rgba(16,185,129,0.15);'>1 adds</span></div>
        </div>
      </div>
    </div>

    <!-- Live Execution Feed -->
    <div class="table-container" style="padding:1.5rem; margin-top:1.5rem;">
      <div class="section-title" style="margin-bottom:0.5rem;">
        <span class="icon">📜</span>
        <span>Recent Ban Hammer Execution Feed</span>
      </div>
      <div class="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Action</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            <tr><td class='mono-cell' style='color:var(--text-dim);'>2026-08-06 22:58</td><td><span class='badge' style='color:#f43f5e; background:rgba(244,63,94,0.15);'>🔨 KICK</span></td><td><strong>Jannatul Ferdous Moumita</strong> removed <span style='color:#ec4899;font-weight:700;'>MD Anik Ahmed</span> from the group</td></tr>
            <tr><td class='mono-cell' style='color:var(--text-dim);'>2026-08-06 22:58</td><td><span class='badge' style='color:#f43f5e; background:rgba(244,63,94,0.15);'>🔨 KICK</span></td><td><strong>Jannatul Ferdous Moumita</strong> removed <span style='color:#ec4899;font-weight:700;'>Abshary Jahin</span> from the group</td></tr>
            <tr><td class='mono-cell' style='color:var(--text-dim);'>2026-08-06 22:58</td><td><span class='badge' style='color:#f43f5e; background:rgba(244,63,94,0.15);'>🔨 KICK</span></td><td><strong>Jannatul Ferdous Moumita</strong> removed <span style='color:#ec4899;font-weight:700;'>Mohammed Sheikh</span> from the group</td></tr>
            <tr><td class='mono-cell' style='color:var(--text-dim);'>2026-08-02 23:55</td><td><span class='badge' style='color:#f43f5e; background:rgba(244,63,94,0.15);'>🔨 KICK</span></td><td><strong>Jannatul Ferdous Moumita</strong> removed <span style='color:#ec4899;font-weight:700;'>Abshary Jahin</span> from the group</td></tr>
            <tr><td class='mono-cell' style='color:var(--text-dim);'>2026-07-31 23:31</td><td><span class='badge' style='color:#f43f5e; background:rgba(244,63,94,0.15);'>🔨 KICK</span></td><td><strong>Jannatul Ferdous Moumita</strong> removed <span style='color:#ec4899;font-weight:700;'>Abshary Jahin</span> from the group</td></tr>
            <tr><td class='mono-cell' style='color:var(--text-dim);'>2026-07-31 23:31</td><td><span class='badge' style='color:#f43f5e; background:rgba(244,63,94,0.15);'>🔨 KICK</span></td><td><strong>Jannatul Ferdous Moumita</strong> removed <span style='color:#ec4899;font-weight:700;'>Anamul Haque Tanvir</span> from the group</td></tr>
            <tr><td class='mono-cell' style='color:var(--text-dim);'>2026-07-31 23:31</td><td><span class='badge' style='color:#f43f5e; background:rgba(244,63,94,0.15);'>🔨 KICK</span></td><td><strong>Jannatul Ferdous Moumita</strong> removed <span style='color:#ec4899;font-weight:700;'>Anamul Haque Tanvir</span> from the group</td></tr>
            <tr><td class='mono-cell' style='color:var(--text-dim);'>2026-07-31 23:31</td><td><span class='badge' style='color:#f43f5e; background:rgba(244,63,94,0.15);'>🔨 KICK</span></td><td><strong>Jannatul Ferdous Moumita</strong> removed <span style='color:#ec4899;font-weight:700;'>Abshary Jahin</span> from the group</td></tr>
            <tr><td class='mono-cell' style='color:var(--text-dim);'>2026-07-31 23:30</td><td><span class='badge' style='color:#f43f5e; background:rgba(244,63,94,0.15);'>🔨 KICK</span></td><td><strong>Jannatul Ferdous Moumita</strong> removed <span style='color:#ec4899;font-weight:700;'>Anamul Haque Tanvir</span> from the group</td></tr>
            <tr><td class='mono-cell' style='color:var(--text-dim);'>2026-07-31 23:30</td><td><span class='badge' style='color:#f43f5e; background:rgba(244,63,94,0.15);'>🔨 KICK</span></td><td><strong>Jannatul Ferdous Moumita</strong> removed <span style='color:#ec4899;font-weight:700;'>Abshary Jahin</span> from the group</td></tr>
            <tr><td class='mono-cell' style='color:var(--text-dim);'>2026-07-31 21:13</td><td><span class='badge' style='color:#f43f5e; background:rgba(244,63,94,0.15);'>🔨 KICK</span></td><td><strong>Jannatul Ferdous Moumita</strong> removed <span style='color:#ec4899;font-weight:700;'>Anamul Haque Tanvir</span> from the group</td></tr>
            <tr><td class='mono-cell' style='color:var(--text-dim);'>2026-07-31 01:28</td><td><span class='badge' style='color:#a855f7; background:rgba(168,85,247,0.15);'>🚪 LEFT</span></td><td><strong>Anamul Haque Tanvir</strong> left the group</td></tr>
            <tr><td class='mono-cell' style='color:var(--text-dim);'>2026-07-31 01:20</td><td><span class='badge' style='color:#a855f7; background:rgba(168,85,247,0.15);'>🚪 LEFT</span></td><td><strong>Anamul Haque Tanvir</strong> left the group</td></tr>
            <tr><td class='mono-cell' style='color:var(--text-dim);'>2026-07-30 22:49</td><td><span class='badge' style='color:#f43f5e; background:rgba(244,63,94,0.15);'>🔨 KICK</span></td><td><strong>Jannatul Ferdous Moumita</strong> removed <span style='color:#ec4899;font-weight:700;'>Anamul Haque Tanvir</span> from the group</td></tr>
            <tr><td class='mono-cell' style='color:var(--text-dim);'>2026-07-30 19:02</td><td><span class='badge' style='color:#f43f5e; background:rgba(244,63,94,0.15);'>🔨 KICK</span></td><td><strong>Jannatul Ferdous Moumita</strong> removed <span style='color:#ec4899;font-weight:700;'>Anamul Haque Tanvir</span> from the group</td></tr>
            <tr><td class='mono-cell' style='color:var(--text-dim);'>2026-07-30 18:40</td><td><span class='badge' style='color:#f43f5e; background:rgba(244,63,94,0.15);'>🔨 KICK</span></td><td><strong>Jannatul Ferdous Moumita</strong> removed <span style='color:#ec4899;font-weight:700;'>Anamul Haque Tanvir</span> from the group</td></tr>
            <tr><td class='mono-cell' style='color:var(--text-dim);'>2026-07-26 23:38</td><td><span class='badge' style='color:#a855f7; background:rgba(168,85,247,0.15);'>🚪 LEFT</span></td><td><strong>Anamul Haque Tanvir</strong> left the group</td></tr>
            <tr><td class='mono-cell' style='color:var(--text-dim);'>2026-07-26 14:36</td><td><span class='badge' style='color:#f43f5e; background:rgba(244,63,94,0.15);'>🔨 KICK</span></td><td><strong>Jannatul Ferdous Moumita</strong> removed <span style='color:#ec4899;font-weight:700;'>Anamul Haque Tanvir</span> from the group</td></tr>
            <tr><td class='mono-cell' style='color:var(--text-dim);'>2026-07-26 00:24</td><td><span class='badge' style='color:#f43f5e; background:rgba(244,63,94,0.15);'>🔨 KICK</span></td><td><strong>Jannatul Ferdous Moumita</strong> removed <span style='color:#ec4899;font-weight:700;'>Abshary Jahin</span> from the group</td></tr>
            <tr><td class='mono-cell' style='color:var(--text-dim);'>2026-07-26 00:24</td><td><span class='badge' style='color:#f43f5e; background:rgba(244,63,94,0.15);'>🔨 KICK</span></td><td><strong>Jannatul Ferdous Moumita</strong> removed <span style='color:#ec4899;font-weight:700;'>Abshary Jahin</span> from the group</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- Tab 3: The Banter & Panic Syndicate -->
  <div id="tab-banter" class="tab-pane">
    <div class="section-title">
      <span class="icon">🎭</span>
      <span>Group Sub-Cultures, Debts & Panic Levels</span>
    </div>
    
    <div class="syndicate-grid">
      <div class="syndicate-card">
        <h3>🍖 The Treat & Kacchi Syndicate</h3>
        <p class="desc">Who demands treats and promises kacchi the most in the group</p>
        <div class="syndicate-list">
          <div class='syndicate-item'><span class='name'>1. Anamul Haque Tanvir</span><span class='badge-count'>148 treats called</span></div>
          <div class='syndicate-item'><span class='name'>2. Purnendu Banik</span><span class='badge-count'>29 treats called</span></div>
          <div class='syndicate-item'><span class='name'>3. Shah Md Nazeef Wasit</span><span class='badge-count'>24 treats called</span></div>
          <div class='syndicate-item'><span class='name'>4. Abshary Jahin</span><span class='badge-count'>19 treats called</span></div>
          <div class='syndicate-item'><span class='name'>5. Md. Maruf Hossain</span><span class='badge-count'>14 treats called</span></div>
        </div>
      </div>

      <div class="syndicate-card">
        <h3>📚 The Academic Panic Board</h3>
        <p class="desc">Mentions of exams, quiz, assignments, labs, slides & sir</p>
        <div class="syndicate-list">
          <div class='syndicate-item'><span class='name'>1. Labib Morol</span><span class='badge-count' style='color:#f59e0b; background:rgba(245,158,11,0.1);'>750 panic triggers</span></div>
          <div class='syndicate-item'><span class='name'>2. Abshary Jahin</span><span class='badge-count' style='color:#f59e0b; background:rgba(245,158,11,0.1);'>597 panic triggers</span></div>
          <div class='syndicate-item'><span class='name'>3. Anamul Haque Tanvir</span><span class='badge-count' style='color:#f59e0b; background:rgba(245,158,11,0.1);'>498 panic triggers</span></div>
          <div class='syndicate-item'><span class='name'>4. Jannatul Ferdous Moumita</span><span class='badge-count' style='color:#f59e0b; background:rgba(245,158,11,0.1);'>375 panic triggers</span></div>
          <div class='syndicate-item'><span class='name'>5. Purnendu Banik</span><span class='badge-count' style='color:#f59e0b; background:rgba(245,158,11,0.1);'>355 panic triggers</span></div>
        </div>
      </div>

      <div class="syndicate-card">
        <h3>👻 The 3 AM – 4 AM Ghost Squad</h3>
        <p class="desc">Chatting during the bewitching hours when normal people sleep</p>
        <div class="syndicate-list">
          <div class='syndicate-item'><span class='name'>1. Junayed Ahmed Saad</span><span class='badge-count' style='color:#c084fc; background:rgba(192,132,252,0.1);'>178 3AM msgs</span></div>
          <div class='syndicate-item'><span class='name'>2. Purnendu Banik</span><span class='badge-count' style='color:#c084fc; background:rgba(192,132,252,0.1);'>111 3AM msgs</span></div>
          <div class='syndicate-item'><span class='name'>3. Labib Morol</span><span class='badge-count' style='color:#c084fc; background:rgba(192,132,252,0.1);'>110 3AM msgs</span></div>
          <div class='syndicate-item'><span class='name'>4. Anamul Haque Tanvir</span><span class='badge-count' style='color:#c084fc; background:rgba(192,132,252,0.1);'>105 3AM msgs</span></div>
          <div class='syndicate-item'><span class='name'>5. Shah Md Nazeef Wasit</span><span class='badge-count' style='color:#c084fc; background:rgba(192,132,252,0.1);'>80 3AM msgs</span></div>
        </div>
      </div>
    </div>
  </div>

  <!-- Tab 4: Media Vault & Meme Gallery -->
  <div id="tab-gallery" class="tab-pane">
    <div class="section-title">
      <span class="icon">📸</span>
      <span>Top Reacted Memes, Photos & GIFs</span>
    </div>
    
    <div class="filter-chips">
      <button class="filter-chip active" onclick="filterGallery('all', this)">All Media</button>
      <button class="filter-chip" onclick="filterGallery('photo', this)">🖼️ Photos</button>
      <button class="filter-chip" onclick="filterGallery('gif', this)">👾 GIFs</button>
    </div>

    <div class="gallery-grid" id="gallery-container"></div>
  </div>

  <!-- Tab 5: Leaderboard Table -->
  <div id="tab-leaderboard" class="tab-pane">
    <div class="table-container">
      <div class="table-header-controls">
        <div class="section-title" style="margin-bottom:0;">
          <span class="icon">📊</span>
          <span>Participant Statistics (<span id="participantCount">55</span> Members)</span>
        </div>
        <input type="text" id="tableSearch" class="search-input" placeholder="Search participant..." oninput="filterTable()">
      </div>
      <div class="table-scroll">
        <table id="statsTable">
          <thead>
            <tr>
              <th onclick="sortTable('rank')"># <span id="sort-rank" class="sort-icon">▲</span></th>
              <th onclick="sortTable('name')">Member <span id="sort-name" class="sort-icon"></span></th>
              <th onclick="sortTable('archetype')">Archetype <span id="sort-archetype" class="sort-icon"></span></th>
              <th onclick="sortTable('messages')">Messages <span id="sort-messages" class="sort-icon"></span></th>
              <th onclick="sortTable('percentage')">Share % <span id="sort-percentage" class="sort-icon"></span></th>
              <th onclick="sortTable('words')">Words <span id="sort-words" class="sort-icon"></span></th>
              <th onclick="sortTable('avg_words_per_msg')">Avg W/M <span id="sort-avg_words_per_msg" class="sort-icon"></span></th>
              <th onclick="sortTable('photos')">Photos <span id="sort-photos" class="sort-icon"></span></th>
              <th onclick="sortTable('reacts_received')">Reacts Recv (+) <span id="sort-reacts_received" class="sort-icon"></span></th>
              <th onclick="sortTable('reacts_given')">Reacts Given (-) <span id="sort-reacts_given" class="sort-icon"></span></th>
              <th onclick="sortTable('night_msgs')">Night Msgs <span id="sort-night_msgs" class="sort-icon"></span></th>
              <th>Top Emoji</th>
              <th>Profile</th>
            </tr>
          </thead>
          <tbody id="tableBody"></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- Tab 6: Charts & Trends -->
  <div id="tab-charts" class="tab-pane">
    <div class="charts-grid">
      <div class="chart-card">
        <h3>⏰ Hourly Activity (24h Bangladesh Time)</h3>
        <div class="chart-container"><canvas id="hourlyChart"></canvas></div>
      </div>
      <div class="chart-card">
        <h3>📅 Day of the Week Volume</h3>
        <div class="chart-container"><canvas id="dowChart"></canvas></div>
      </div>
      <div class="chart-card">
        <h3>📈 Monthly Chat Volume</h3>
        <div class="chart-container"><canvas id="monthlyChart"></canvas></div>
      </div>
      <div class="chart-card">
        <h3>🏆 Top 10 Senders</h3>
        <div class="chart-container"><canvas id="topSendersChart"></canvas></div>
      </div>
      <div class="chart-card">
        <h3>😂 Top Emojis Breakdown</h3>
        <div class="chart-container"><canvas id="emojisChart"></canvas></div>
      </div>
      <div class="chart-card">
        <h3>🎭 Reactions Breakdown</h3>
        <div class="chart-container"><canvas id="reactionsChart"></canvas></div>
      </div>
    </div>

    <div class="table-container" style="margin-top: 1.5rem;">
      <div class="table-header-controls">
        <div class="section-title" style="margin-bottom:0;">
          <span class="icon">🔥</span>
          <span>Top 10 Craziest Days in History</span>
        </div>
      </div>
      <div class="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Date</th>
              <th>Day</th>
              <th>Messages Sent</th>
            </tr>
          </thead>
          <tbody>
            <tr><td class='rank-cell'>1</td><td><strong>2026-05-11</strong></td><td>Monday</td><td class='mono-cell' style='color:#38bdf8;font-weight:700;'>1,379 msgs</td></tr>
            <tr><td class='rank-cell'>2</td><td><strong>2026-07-20</strong></td><td>Monday</td><td class='mono-cell' style='color:#38bdf8;font-weight:700;'>1,080 msgs</td></tr>
            <tr><td class='rank-cell'>3</td><td><strong>2026-05-21</strong></td><td>Thursday</td><td class='mono-cell' style='color:#38bdf8;font-weight:700;'>1,035 msgs</td></tr>
            <tr><td class='rank-cell'>4</td><td><strong>2026-07-30</strong></td><td>Thursday</td><td class='mono-cell' style='color:#38bdf8;font-weight:700;'>938 msgs</td></tr>
            <tr><td class='rank-cell'>5</td><td><strong>2026-07-15</strong></td><td>Wednesday</td><td class='mono-cell' style='color:#38bdf8;font-weight:700;'>929 msgs</td></tr>
            <tr><td class='rank-cell'>6</td><td><strong>2026-07-17</strong></td><td>Friday</td><td class='mono-cell' style='color:#38bdf8;font-weight:700;'>878 msgs</td></tr>
            <tr><td class='rank-cell'>7</td><td><strong>2026-07-04</strong></td><td>Saturday</td><td class='mono-cell' style='color:#38bdf8;font-weight:700;'>874 msgs</td></tr>
            <tr><td class='rank-cell'>8</td><td><strong>2026-07-19</strong></td><td>Sunday</td><td class='mono-cell' style='color:#38bdf8;font-weight:700;'>838 msgs</td></tr>
            <tr><td class='rank-cell'>9</td><td><strong>2026-07-31</strong></td><td>Friday</td><td class='mono-cell' style='color:#38bdf8;font-weight:700;'>818 msgs</td></tr>
            <tr><td class='rank-cell'>10</td><td><strong>2026-05-15</strong></td><td>Friday</td><td class='mono-cell' style='color:#38bdf8;font-weight:700;'>803 msgs</td></tr>
            <tr><td class='rank-cell'>11</td><td><strong>2026-05-20</strong></td><td>Wednesday</td><td class='mono-cell' style='color:#38bdf8;font-weight:700;'>792 msgs</td></tr>
            <tr><td class='rank-cell'>12</td><td><strong>2026-07-16</strong></td><td>Thursday</td><td class='mono-cell' style='color:#38bdf8;font-weight:700;'>768 msgs</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- Tab 7: Hall of Fame -->
  <div id="tab-halloffame" class="tab-pane">
    <div class="section-title">
      <span class="icon">🌟</span>
      <span>Most Reacted Messages & Media of All Time</span>
    </div>
    <div class="hof-grid" id="hof-container"></div>
  </div>

  <!-- Tab 8: Best Duos -->
  <div id="tab-duos" class="tab-pane">
    <div class="section-title">
      <span class="icon">❤️</span>
      <span>Top Hype Duos (Who reacts to whom the most)</span>
    </div>
    <div class="hof-grid">
      <div class='hof-card'>
        <div class='hof-top'>
          <div class='hof-sender'>#1 Duo Match</div>
          <div class='hof-count'>653 reacts ❤️</div>
        </div>
        <div class='hof-content' style='font-size:1.05rem; text-align:center;'>
          <span style='color:#38bdf8; font-weight:700;'>Abshary Jahin</span>
          <br><span style='color:var(--text-dim); font-size:0.85rem;'>hyped up</span><br>
          <span style='color:#ec4899; font-weight:700;'>Anamul Haque Tanvir</span>
        </div>
      </div>
      
      <div class='hof-card'>
        <div class='hof-top'>
          <div class='hof-sender'>#2 Duo Match</div>
          <div class='hof-count'>354 reacts ❤️</div>
        </div>
        <div class='hof-content' style='font-size:1.05rem; text-align:center;'>
          <span style='color:#38bdf8; font-weight:700;'>Rubayet Mahmud</span>
          <br><span style='color:var(--text-dim); font-size:0.85rem;'>hyped up</span><br>
          <span style='color:#ec4899; font-weight:700;'>Abshary Jahin</span>
        </div>
      </div>
      
      <div class='hof-card'>
        <div class='hof-top'>
          <div class='hof-sender'>#3 Duo Match</div>
          <div class='hof-count'>346 reacts ❤️</div>
        </div>
        <div class='hof-content' style='font-size:1.05rem; text-align:center;'>
          <span style='color:#38bdf8; font-weight:700;'>Abshary Jahin</span>
          <br><span style='color:var(--text-dim); font-size:0.85rem;'>hyped up</span><br>
          <span style='color:#ec4899; font-weight:700;'>Purnendu Banik</span>
        </div>
      </div>
      
      <div class='hof-card'>
        <div class='hof-top'>
          <div class='hof-sender'>#4 Duo Match</div>
          <div class='hof-count'>313 reacts ❤️</div>
        </div>
        <div class='hof-content' style='font-size:1.05rem; text-align:center;'>
          <span style='color:#38bdf8; font-weight:700;'>Abshary Jahin</span>
          <br><span style='color:var(--text-dim); font-size:0.85rem;'>hyped up</span><br>
          <span style='color:#ec4899; font-weight:700;'>Jannatul Ferdous Moumita</span>
        </div>
      </div>
      
      <div class='hof-card'>
        <div class='hof-top'>
          <div class='hof-sender'>#5 Duo Match</div>
          <div class='hof-count'>279 reacts ❤️</div>
        </div>
        <div class='hof-content' style='font-size:1.05rem; text-align:center;'>
          <span style='color:#38bdf8; font-weight:700;'>Abshary Jahin</span>
          <br><span style='color:var(--text-dim); font-size:0.85rem;'>hyped up</span><br>
          <span style='color:#ec4899; font-weight:700;'>Labib Morol</span>
        </div>
      </div>
      
      <div class='hof-card'>
        <div class='hof-top'>
          <div class='hof-sender'>#6 Duo Match</div>
          <div class='hof-count'>252 reacts ❤️</div>
        </div>
        <div class='hof-content' style='font-size:1.05rem; text-align:center;'>
          <span style='color:#38bdf8; font-weight:700;'>Abshary Jahin</span>
          <br><span style='color:var(--text-dim); font-size:0.85rem;'>hyped up</span><br>
          <span style='color:#ec4899; font-weight:700;'>Mohammed Sheikh</span>
        </div>
      </div>
      
      <div class='hof-card'>
        <div class='hof-top'>
          <div class='hof-sender'>#7 Duo Match</div>
          <div class='hof-count'>246 reacts ❤️</div>
        </div>
        <div class='hof-content' style='font-size:1.05rem; text-align:center;'>
          <span style='color:#38bdf8; font-weight:700;'>Anamul Haque Tanvir</span>
          <br><span style='color:var(--text-dim); font-size:0.85rem;'>hyped up</span><br>
          <span style='color:#ec4899; font-weight:700;'>Abshary Jahin</span>
        </div>
      </div>
      
      <div class='hof-card'>
        <div class='hof-top'>
          <div class='hof-sender'>#8 Duo Match</div>
          <div class='hof-count'>240 reacts ❤️</div>
        </div>
        <div class='hof-content' style='font-size:1.05rem; text-align:center;'>
          <span style='color:#38bdf8; font-weight:700;'>Rubayet Mahmud</span>
          <br><span style='color:var(--text-dim); font-size:0.85rem;'>hyped up</span><br>
          <span style='color:#ec4899; font-weight:700;'>Anamul Haque Tanvir</span>
        </div>
      </div>
      
      <div class='hof-card'>
        <div class='hof-top'>
          <div class='hof-sender'>#9 Duo Match</div>
          <div class='hof-count'>236 reacts ❤️</div>
        </div>
        <div class='hof-content' style='font-size:1.05rem; text-align:center;'>
          <span style='color:#38bdf8; font-weight:700;'>Mohammed Sheikh</span>
          <br><span style='color:var(--text-dim); font-size:0.85rem;'>hyped up</span><br>
          <span style='color:#ec4899; font-weight:700;'>Abshary Jahin</span>
        </div>
      </div>
      
      <div class='hof-card'>
        <div class='hof-top'>
          <div class='hof-sender'>#10 Duo Match</div>
          <div class='hof-count'>232 reacts ❤️</div>
        </div>
        <div class='hof-content' style='font-size:1.05rem; text-align:center;'>
          <span style='color:#38bdf8; font-weight:700;'>Anamul Haque Tanvir</span>
          <br><span style='color:var(--text-dim); font-size:0.85rem;'>hyped up</span><br>
          <span style='color:#ec4899; font-weight:700;'>Jannatul Ferdous Moumita</span>
        </div>
      </div>
      
      <div class='hof-card'>
        <div class='hof-top'>
          <div class='hof-sender'>#11 Duo Match</div>
          <div class='hof-count'>230 reacts ❤️</div>
        </div>
        <div class='hof-content' style='font-size:1.05rem; text-align:center;'>
          <span style='color:#38bdf8; font-weight:700;'>Mohammed Sheikh</span>
          <br><span style='color:var(--text-dim); font-size:0.85rem;'>hyped up</span><br>
          <span style='color:#ec4899; font-weight:700;'>Labib Morol</span>
        </div>
      </div>
      
      <div class='hof-card'>
        <div class='hof-top'>
          <div class='hof-sender'>#12 Duo Match</div>
          <div class='hof-count'>215 reacts ❤️</div>
        </div>
        <div class='hof-content' style='font-size:1.05rem; text-align:center;'>
          <span style='color:#38bdf8; font-weight:700;'>Abshary Jahin</span>
          <br><span style='color:var(--text-dim); font-size:0.85rem;'>hyped up</span><br>
          <span style='color:#ec4899; font-weight:700;'>Rubayet Mahmud</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Tab 9: Share Snippets -->
  <div id="tab-share" class="tab-pane">
    <div class="section-title">
      <span class="icon">📋</span>
      <span>Copy & Paste Cards for Group Chat</span>
    </div>
    <p style="color:var(--text-muted); margin-bottom:1.5rem;">Click the copy button and drop these directly into your Messenger group!</p>
    
    <div class="share-box">
      <h3 style="margin-bottom:0.5rem; color:#fff;">⚔️ CR Moumita's Ban Hammer & Court of Justice</h3>
      <pre id="snippet-court" class="snippet-pre"></pre>
      <button class="copy-btn" onclick="copySnippet('snippet-court', this)">📋 Copy Ban Hammer Stats</button>
    </div>

    <div class="share-box">
      <h3 style="margin-bottom:0.5rem; color:#fff;">🏆 The Official Group Superlatives</h3>
      <pre id="snippet-superlatives" class="snippet-pre"></pre>
      <button class="copy-btn" onclick="copySnippet('snippet-superlatives', this)">📋 Copy Superlatives</button>
    </div>

    <div class="share-box">
      <h3 style="margin-bottom:0.5rem; color:#fff;">🍖 The Treat & Panic Syndicate</h3>
      <pre id="snippet-banter" class="snippet-pre"></pre>
      <button class="copy-btn" onclick="copySnippet('snippet-banter', this)">📋 Copy Treat & Panic Stats</button>
    </div>

    <div class="share-box">
      <h3 style="margin-bottom:0.5rem; color:#fff;">📊 Top 10 Spammers (Message Count)</h3>
      <pre id="snippet-top10" class="snippet-pre"></pre>
      <button class="copy-btn" onclick="copySnippet('snippet-top10', this)">📋 Copy Top 10 Leaderboard</button>
    </div>

    <div class="share-box">
      <h3 style="margin-bottom:0.5rem; color:#fff;">😭 The Emoji & Reaction Awards</h3>
      <pre id="snippet-emojis" class="snippet-pre"></pre>
      <button class="copy-btn" onclick="copySnippet('snippet-emojis', this)">📋 Copy Emoji & Clout Stats</button>
    </div>
  </div>

  <!-- Profile Modal Popup -->
  <div id="profileModal" class="modal-backdrop" onclick="closeModal()">
    <div class="modal-card" onclick="event.stopPropagation()">
      <button class="close-modal" onclick="closeModal()" aria-label="Close modal">&times;</button>
      <div id="modalBody"></div>
    </div>
  </div>

  <!-- Lightbox Modal -->
  <div id="lightboxModal" class="lightbox-modal" onclick="closeLightbox()">
    <button class="lightbox-close" onclick="closeLightbox()" aria-label="Close image preview">&times;</button>
    <img id="lightboxImg" class="lightbox-img" src="" alt="Full Resolution Image" onclick="event.stopPropagation()">
  </div>

  <footer>
    <p>Generated with ❤️ for লৌহপূর্ণ খামার (কসাই-৩২💻) • 53,672 Messages Analyzed</p>
  </footer>

</div>
<script src="chart.min.js"></script>
<script src="app.js"></script>
</body>
</html>
"""

# 4. Write app.js and index.html to deploy/
with open(os.path.join(deploy_dir, "app.js"), "w", encoding="utf-8") as f:
    f.write(app_js_code)

with open(os.path.join(deploy_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_content)

# 5. Write app.js and index.html to deploy/messenger-group-chat/
if os.path.exists(sub_dir):
    with open(os.path.join(sub_dir, "app.js"), "w", encoding="utf-8") as f:
        f.write(app_js_code)

    with open(os.path.join(sub_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)

print("Build successfully generated! All files synchronized.")
