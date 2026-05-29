# crm-app
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CRM Mini App</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: system-ui; background: #f5f5f5; padding: 16px; }
        .header { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 16px; margin-bottom: 20px; text-align: center; }
        .card { background: white; border-radius: 16px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        button { background: #667eea; color: white; border: none; padding: 12px; border-radius: 12px; width: 100%; margin-bottom: 10px; cursor: pointer; }
        button.danger { background: #ef4444; }
        input, select { width: 100%; padding: 12px; margin-bottom: 12px; border: 1px solid #ddd; border-radius: 12px; }
        .status { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; }
        .status-new { background: #e0f2fe; color: #0284c7; }
        .status-work { background: #fef3c7; color: #d97706; }
        .status-deal { background: #dcfce7; color: #16a34a; }
        .status-closed { background: #f1f5f9; color: #475569; }
    </style>
</head>
<body>
    <div class="header"><h1>🤖 CRM</h1><p>Управление клиентами</p></div>
    <div class="card">
        <button onclick="showAdd()">➕ Добавить</button>
        <button onclick="showList()">📋 Список</button>
        <button onclick="showStats()">📊 Статистика</button>
    </div>
    <div id="content"></div>
    <script>
        let clients = []; let nextId = 1;
        function save() { localStorage.setItem('clients', JSON.stringify(clients)); localStorage.setItem('nextId', nextId); }
        function load() { let s = localStorage.getItem('clients'); if(s) clients = JSON.parse(s); let i = localStorage.getItem('nextId'); if(i) nextId = parseInt(i); }
        window.showAdd = function() { document.getElementById('content').innerHTML = '<div class="card"><h3>➕ Новый</h3><input type="text" id="name" placeholder="Имя"><input type="text" id="phone" placeholder="Телефон"><select id="status"><option value="Новый">🟢 Новый</option><option value="В работе">🟡 В работе</option><option value="Договор">🔵 Договор</option><option value="Закрыт">✅ Закрыт</option></select><button onclick="add()">Сохранить</button><button onclick="showList()" class="danger">Отмена</button></div>'; }
        window.add = function() { let name = document.getElementById('name').value; if(!name) { alert('Введите имя'); return; } clients.push({ id: nextId++, name: name, phone: document.getElementById('phone').value || '—', status: document.getElementById('status').value, date: new Date().toLocaleString() }); save(); showList(); }
        window.showList = function() { if(clients.length === 0) { document.getElementById('content').innerHTML = '<div class="card"><p>📭 Нет клиентов</p></div>'; return; } let html = ''; clients.forEach(c => { let cls = ''; if(c.status === 'Новый') cls = 'status-new'; else if(c.status === 'В работе') cls = 'status-work'; else if(c.status === 'Договор') cls = 'status-deal'; else cls = 'status-closed'; html += '<div class="card"><strong>'+c.name+'</strong><br>📞 '+c.phone+'<br><span class="status '+cls+'">'+c.status+'</span><br><br><button onclick="view('+c.id+')">👤 Подробнее</button></div>'; }); document.getElementById('content').innerHTML = html; }
        window.view = function(id) { let c = clients.find(x => x.id === id); let cls = ''; if(c.status === 'Новый') cls = 'status-new'; else if(c.status === 'В работе') cls = 'status-work'; else if(c.status === 'Договор') cls = 'status-deal'; else cls = 'status-closed'; document.getElementById('content').innerHTML = '<div class="card"><h3>'+c.name+'</h3><p>📞 '+c.phone+'</p><p><span class="status '+cls+'">'+c.status+'</span></p><p>📅 '+c.date+'</p><hr><select id="ns"><option value="Новый">Новый</option><option value="В работе">В работе</option><option value="Договор">Договор</option><option value="Закрыт">Закрыт</option></select><button onclick="change('+id+')">Изменить</button><button onclick="showList()" class="danger">Назад</button></div>'; }
        window.change = function(id) { let ns = document.getElementById('ns').value; let c = clients.find(x => x.id === id); if(c) { c.status = ns; save(); view(id); } }
        window.showStats = function() { let total = clients.length; let cnt = { 'Новый':0, 'В работе':0, 'Договор':0, 'Закрыт':0 }; clients.forEach(c => cnt[c.status]++); document.getElementById('content').innerHTML = '<div class="card"><h3>📊 Статистика</h3><p>Всего: '+total+'</p><p>🟢 Новые: '+cnt['Новый']+'</p><p>🟡 В работе: '+cnt['В работе']+'</p><p>🔵 Договор: '+cnt['Договор']+'</p><p>✅ Закрыты: '+cnt['Закрыт']+'</p><button onclick="showList()">Назад</button></div>'; }
        load(); showList();
    </script>
</body>
</html>
