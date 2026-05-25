import React, { useState, useEffect } from 'react';
import Game from './pages/Game';
import AdminLogin from './pages/admin/AdminLogin';
import Admin from './pages/admin/Admin';

function App() {
    const [page, setPage] = useState('game');

    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        if (params.get('secret') === 'admin123') {
            setPage('login');
            window.history.replaceState({}, '', window.location.pathname);
        }
    }, []);

    useEffect(() => {
        fetch('/api/characters', {
            method: 'GET',
            credentials: 'include'
        }).then(response => {
            if (response.ok) {
                setPage('admin');
            }
        }).catch(() => {});
    }, []);

    const pages = {
        'game': <Game onOpenAdmin={() => setPage('login')} />,
        'login': <AdminLogin 
            onLogin={() => setPage('admin')} 
            onBack={() => setPage('game')} 
        />,
        'admin': <Admin 
            onLogout={() => setPage('game')} 
        />
    };

    return pages[page] || <div>404</div>;
}

export default App;