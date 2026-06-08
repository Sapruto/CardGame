import React, { useState } from "react";
import { adminApi } from "../../api";
import "./Admin.css"

function AdminLogin({ onLogin, onBack }) {
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        
        try {
            await adminApi.adminLogin(password);
            onLogin();
        } 
        catch (err) {
            setError(err.message || 'Неверный пароль');
        }
        
        setLoading(false);
    };

    return (
        <div style={{ padding: '20px', textAlign: 'center' }}>
            <h2>Вход в админку</h2>
            <button onClick={onBack} style={{ marginBottom: '20px' }}>
                Назад в игру
            </button>
            
            <form onSubmit={handleSubmit}>
                <div>
                    <input 
                        type="password" 
                        placeholder="Пароль" 
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        style={{ padding: '8px', width: '200px' }}
                    />
                </div>
                <button 
                    type="submit" 
                    disabled={loading}
                    style={{ marginTop: '10px', padding: '8px 20px' }}
                >
                    {loading ? 'Вход...' : 'Войти'}
                </button>
            </form>
            
            {error && (
                <p style={{ color: '#aa0f0f', marginTop: '10px' }}>
                    {error}
                </p>
            )}
        </div>
    );
}

export default AdminLogin;