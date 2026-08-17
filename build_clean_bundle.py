import os, json, re, shutil

# 1. Read clean JSON
with open('messenger-group-chat/chat_statistics.json', 'r', encoding='utf-8') as f:
    chat_data = json.load(f)

# Remove any vai_addicts or vai_calls if present in chat_data
if 'funny_details' in chat_data and 'vai_addicts' in chat_data['funny_details']:
    del chat_data['funny_details']['vai_addicts']

# 2. Read index.html
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove the HTML 'Vai / Bhai' Punctuation Club card if still present
html = re.sub(r'<div class="syndicate-card">\s*<h3>🤝 The [^\n]*Punctuation Club</h3>[\s\S]*?</div>\s*</div>', '', html)

# Cut before <script> tag that contained rawData
if '<script>' in html:
    html_base = html.split('<script>')[0]
else:
    html_base = html

# Ensure chart.min.js is in head
if 'chart.min.js' not in html_base:
    html_base = html_base.replace('https://cdn.jsdelivr.net/npm/chart.js', 'chart.min.js')

# 3. Create app.js
app_js_code = """
const rawData = """ + json.dumps(chat_data, ensure_ascii=False) + """;

let currentGalleryFilter = 'all';
let sortDirection = {};

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
  }
}

function closeLightbox() {
  const modal = document.getElementById('lightboxModal');
  if (modal) modal.classList.remove('active');
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
  if (!container) return;

  let items = rawData.media_gallery;
  if (currentGalleryFilter !== 'all') {
    items = items.filter(m => m.type === currentGalleryFilter);
  }

  container.innerHTML = items.map((m, idx) => {
    let mediaHtml = '';
    const photoSrc = resolveImgSrc(m, 'photo');
    const gifSrc = resolveImgSrc(m, 'gif');

    if (photoSrc) {
      mediaHtml = '<img src="' + photoSrc + '" loading="lazy" onerror="this.style.display=\\'none\\'" onclick="openLightbox(\\'' + photoSrc + '\\')" alt="Media">';
    } else if (gifSrc) {
      mediaHtml = '<img src="' + gifSrc + '" loading="lazy" onerror="this.style.display=\\'none\\'" onclick="openLightbox(\\'' + gifSrc + '\\')" alt="GIF">';
    }

    const rxBadges = Object.entries(m.reactions.reduce((acc, cur) => { acc[cur] = (acc[cur] || 0) + 1; return acc; }, {}))
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

  tbody.innerHTML = dataToRender.map(p => 
    '<tr>' +
      '<td class="rank-cell">#' + p.rank + '</td>' +
      '<td>' +
        '<div class="user-cell" onclick="openModal(\\'' + p.name.replace(/'/g, "\\\\'") + '\\')">' +
          '<div class="user-avatar">' + p.name.charAt(0) + '</div>' +
          '<div class="user-name-wrapper">' +
            '<span class="user-name">' + p.name + '</span>' +
            '<span class="user-sub">' + p.percentage + '% of chat</span>' +
          '</div>' +
        '</div>' +
      '</td>' +
      '<td class="mono-cell">' + p.messages.toLocaleString() + '</td>' +
      '<td class="mono-cell">' + p.words.toLocaleString() + '</td>' +
      '<td class="mono-cell">' + p.photos + '</td>' +
      '<td class="mono-cell" style="color:#f59e0b;">+' + p.reacts_received.toLocaleString() + '</td>' +
      '<td class="mono-cell" style="color:#ec4899;">-' + p.reacts_given.toLocaleString() + '</td>' +
      '<td class="mono-cell" style="color:#818cf8;">' + p.night_msgs.toLocaleString() + '</td>' +
      '<td><span class="table-badge">' + (p.top_emojis[0] ? p.top_emojis[0].emoji : '💬') + ' ' + (p.top_emojis[0] ? p.top_emojis[0].count : 0) + '</span></td>' +
    '</tr>'
  ).join('');
}

function filterTable() {
  const input = document.getElementById('tableSearch');
  const query = input ? input.value.toLowerCase() : '';
  const filtered = rawData.participants.filter(p => p.name.toLowerCase().includes(query));
  renderTable(filtered);
}

function sortTable(key) {
  const direction = sortDirection[key] === 'asc' ? 'desc' : 'asc';
  sortDirection[key] = direction;

  const sorted = [...rawData.participants].sort((a, b) => {
    let valA = a[key];
    let valB = b[key];
    if (typeof valA === 'string') {
      return direction === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA);
    }
    return direction === 'asc' ? valA - valB : valB - valA;
  });

  renderTable(sorted);
}

function buildHallOfFame() {
  const container = document.getElementById('hof-container');
  if (!container) return;

  container.innerHTML = rawData.hall_of_fame.map((m, i) => {
    let mediaBox = '';
    const photoSrc = resolveImgSrc(m, 'photo');
    const gifSrc = resolveImgSrc(m, 'gif');

    if (photoSrc) {
      mediaBox = '<div class="hof-media-box" onclick="openLightbox(\\'' + photoSrc + '\\')"><img src="' + photoSrc + '" loading="lazy" onerror="this.style.display=\\'none\\'" alt="Photo"></div>';
    } else if (gifSrc) {
      mediaBox = '<div class="hof-media-box" onclick="openLightbox(\\'' + gifSrc + '\\')"><img src="' + gifSrc + '" loading="lazy" onerror="this.style.display=\\'none\\'" alt="GIF"></div>';
    }

    const rxBadges = Object.entries(m.reactions.reduce((acc, cur) => { acc[cur] = (acc[cur] || 0) + 1; return acc; }, {}))
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

  body.innerHTML = 
    '<div class="profile-modal-header">' +
      '<div class="profile-avatar-large">' + p.name.charAt(0) + '</div>' +
      '<div class="profile-title-block">' +
        '<div class="profile-name">' + p.name + '</div>' +
        '<div class="profile-rank-badge">#' + p.rank + ' Overall • ' + p.percentage + '% of Group Volume</div>' +
      '</div>' +
    '</div>' +
    '<div class="profile-stats-grid">' +
      '<div class="profile-stat-box"><div class="profile-val">' + p.messages.toLocaleString() + '</div><div class="profile-lbl">Messages Sent</div></div>' +
      '<div class="profile-stat-box"><div class="profile-val">' + p.words.toLocaleString() + '</div><div class="profile-lbl">Words Typed</div></div>' +
      '<div class="profile-stat-box"><div class="profile-val">' + p.avg_words_per_msg + '</div><div class="profile-lbl">Avg Words / Msg</div></div>' +
      '<div class="profile-stat-box"><div class="profile-val" style="color:#f59e0b;">+' + p.reacts_received.toLocaleString() + '</div><div class="profile-lbl">Reacts Received</div></div>' +
      '<div class="profile-stat-box"><div class="profile-val" style="color:#ec4899;">-' + p.reacts_given.toLocaleString() + '</div><div class="profile-lbl">Reacts Given</div></div>' +
      '<div class="profile-stat-box"><div class="profile-val" style="color:#818cf8;">' + p.night_msgs.toLocaleString() + '</div><div class="profile-lbl">Late Night (12-5 AM)</div></div>' +
      '<div class="profile-stat-box"><div class="profile-val" style="color:#38bdf8;">' + p.photos + '</div><div class="profile-lbl">Photos Shared</div></div>' +
      '<div class="profile-stat-box"><div class="profile-val" style="color:#ef4444;">' + p.unsent + '</div><div class="profile-lbl">Unsent Messages</div></div>' +
      '<div class="profile-stat-box"><div class="profile-val" style="color:#c084fc;">' + p.max_consecutive + '</div><div class="profile-lbl">Max Streak in a Row</div></div>' +
      '<div class="profile-stat-box"><div class="profile-val" style="color:#10b981;">' + p.starters + '</div><div class="profile-lbl">Chat Starters (CPR)</div></div>' +
      '<div class="profile-stat-box"><div class="profile-val" style="color:#f43f5e;">' + p.killers + '</div><div class="profile-lbl">Chat Enders</div></div>' +
      '<div class="profile-stat-box"><div class="profile-val" style="color:#fbbf24;">' + p.treat_calls + '</div><div class="profile-lbl">Treat / Kacchi Demands</div></div>' +
    '</div>' +
    '<div class="profile-detail-section">' +
      '<h4>Top 8 Emojis Used</h4>' +
      '<div class="profile-emoji-row">' +
        p.top_emojis.map(e => '<span class="profile-emoji-pill">' + e.emoji + ' <span style="color:var(--text-dim);font-size:0.75rem;">' + e.count + '</span></span>').join('') +
      '</div>' +
    '</div>';

  modal.classList.add('active');
}

function closeModal() {
  const modal = document.getElementById('profileModal');
  if (modal) modal.classList.remove('active');
}

function closeModalDirect(event) {
  if (event && event.target && event.target.id === 'profileModal') {
    closeModal();
  }
}

function buildSnippets() {
  const p = rawData.participants;
  const court = rawData.funny_details;
  
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
  navigator.clipboard.writeText(elem.textContent).then(() => {
    const originalText = btn.textContent;
    btn.textContent = '✅ Copied to Clipboard!';
    btn.style.background = '#10b981';
    btn.style.color = '#fff';
    setTimeout(() => {
      btn.textContent = originalText;
      btn.style.background = '';
      btn.style.color = '';
    }, 2000);
  }).catch(() => {
    btn.textContent = '❌ Failed to copy';
  });
}

function initCharts() {
  if (typeof Chart === 'undefined') return;

  const ctxH = document.getElementById('hourlyChart');
  if (ctxH) {
    new Chart(ctxH, {
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
          x: { grid: { display: false } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' } }
        }
      }
    });
  }

  const ctxD = document.getElementById('dowChart');
  if (ctxD) {
    new Chart(ctxD, {
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
          x: { grid: { display: false } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' } }
        }
      }
    });
  }

  const ctxM = document.getElementById('monthlyChart');
  if (ctxM) {
    new Chart(ctxM, {
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
          x: { grid: { display: false } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' } }
        }
      }
    });
  }

  const ctxT = document.getElementById('topSendersChart');
  if (ctxT) {
    const top10 = rawData.participants.slice(0, 10);
    new Chart(ctxT, {
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
          x: { grid: { display: false } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' } }
        }
      }
    });
  }

  const ctxE = document.getElementById('emojisChart');
  if (ctxE) {
    const topEmojis = rawData.top_emojis.slice(0, 8);
    new Chart(ctxE, {
      type: 'doughnut',
      data: {
        labels: topEmojis.map(e => e.emoji),
        datasets: [{
          data: topEmojis.map(e => e.count),
          backgroundColor: ['#3b82f6', '#06b6d4', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#f43f5e', '#64748b']
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'right' } }
      }
    });
  }

  const ctxR = document.getElementById('reactionsChart');
  if (ctxR) {
    const topRx = rawData.top_reaction_types.slice(0, 6);
    new Chart(ctxR, {
      type: 'pie',
      data: {
        labels: topRx.map(r => r.emoji),
        datasets: [{
          data: topRx.map(r => r.count),
          backgroundColor: ['#f59e0b', '#ec4899', '#3b82f6', '#10b981', '#8b5cf6', '#06b6d4']
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'right' } }
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

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(app_js_code)

with open('messenger-group-chat/app.js', 'w', encoding='utf-8') as f:
    f.write(app_js_code)

# Assemble clean index.html with <script src="app.js"></script>
final_html = html_base.strip() + '\n<script src="chart.min.js"></script>\n<script src="app.js"></script>\n</body>\n</html>\n'

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

with open('messenger-group-chat/index.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

print('Build generated with external app.js and clean HTML!')
