import React, { useState, useEffect } from 'react';
import "./Admin.css"

function MetricsScreen() 
{
    const [metrics, setMetrics] = useState([]);
    const [newName, setNewName] = useState('');
    const [newDesc, setNewDesc] = useState('');
    const [newDefault, setNewDefault] = useState(0);

    const fetchMetrics = async () => 
    {
        const res = await fetch('/api/metrics', { credentials: 'include' });
        if (res.ok) setMetrics(await res.json());
    };

    const createMetric = async () => 
    {
        await fetch('/api/metrics', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ metric_name: newName, description: newDesc, default_value: newDefault }),
            credentials: 'include'
        });
        fetchMetrics();
        setNewName('');
        setNewDesc('');
        setNewDefault(0);
    };

    const deleteMetric = async (id) => 
    {
        await fetch(`/api/metrics/${id}`, { method: 'DELETE', credentials: 'include' });
        fetchMetrics();
    };

    useEffect(() => { fetchMetrics(); }, []);

    return (
        <div className="metrics-screen">
            <h3>Метрики</h3>
            <input placeholder="Название" value={newName} onChange={e => setNewName(e.target.value)} />
            <input placeholder="Описание" value={newDesc} onChange={e => setNewDesc(e.target.value)} />
            <input type="number" placeholder="Значение по умолчанию" value={newDefault} onChange={e => setNewDefault(parseInt(e.target.value))} />
            <button onClick={createMetric}>Добавить метрику</button>
            <ul>
                {metrics.map(m => (
                    <li key={m.id}>
                        {m.metric_name} - {m.description} (по умолч: {m.default_value}) 
                        <button onClick={() => deleteMetric(m.id)}>Удалить</button>
                    </li>
                ))}
            </ul>
        </div>
    );
}

function ImageManager() 
{
    const [images, setImages] = useState([]);
    const [uploadFile, setUploadFile] = useState(null);
    const [selectedFolder, setSelectedFolder] = useState('backgrounds');
    const [preview, setPreview] = useState('');
    const [bgPath, setBgPath] = useState('');
    const [loading, setLoading] = useState(false);

    const folders = [
        { key: 'backgrounds', label: 'Фоны' },
        { key: 'characters', label: 'Персонажи' },
        { key: 'cards', label: 'Карточки' }
    ];

    const fetchImages = async () => 
    {
        setLoading(true);
        try 
        {
            const res = await fetch(`/api/images/${selectedFolder}`, { credentials: 'include' });
            if (res.ok) 
            {
                const data = await res.json();
                setImages(data);
            }
        } 
        catch(e) 
        {
            console.error('Error fetching images:', e);
        } 
        finally 
        {
            setLoading(false);
        }
    };

    const fetchBgPath = async () => 
    {
        try 
        {
            const res = await fetch('/api/resources/bg', { credentials: 'include' });
            if (res.ok) 
            {
                const data = await res.json();
                setBgPath(data.bg_path);
            }
        } 
        catch(e) 
        {
            console.error('Error fetching bg:', e);
        }
    };

    const uploadImage = async () => 
    {
        if (!uploadFile) return;
        setLoading(true);
        const formData = new FormData();
        formData.append('folder', selectedFolder);
        formData.append('file', uploadFile);
        
        try 
        {
            const res = await fetch('/api/upload_image', {
                method: 'POST',
                credentials: 'include',
                body: formData
            });
            
            if (res.ok) 
            {
                const data = await res.json();
                if (selectedFolder === 'backgrounds') 
                {
                    await setBackground(data.path);
                }
                setUploadFile(null);
                setPreview('');
                await fetchImages();
            }
        } 
        catch(e) 
        {
            console.error('Error uploading image:', e);
        } 
        finally 
        {
            setLoading(false);
        }
    };

    const setBackground = async (path) => 
    {
        try 
        {
            await fetch('/api/resources/bg', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ bg_path: path }),
                credentials: 'include'
            });
            await fetchBgPath();
        } 
        catch(e) 
        {
            console.error('Error setting background:', e);
        }
    };

    const handleFileSelect = (e) => 
    {
        const file = e.target.files[0];
        setUploadFile(file);
        setPreview(URL.createObjectURL(file));
    };

    useEffect(() => 
    { 
        fetchImages(); 
        fetchBgPath(); 
    }, [selectedFolder]);

    return (
        <div className="image-manager">
            <h3>Менеджер картинок</h3>
            
            <div className="bg-preview">
                <h4>Текущий фон:</h4>
                {bgPath && <img src={bgPath} alt="bg" onError={(e) => { e.target.style.display = 'none'; }} />}
                <div>{bgPath || 'Не установлен'}</div>
            </div>
            
            <div className="folder-select">
                <label>Папка: </label>
                <select value={selectedFolder} onChange={(e) => setSelectedFolder(e.target.value)}>
                    {folders.map(f => <option key={f.key} value={f.key}>{f.label}</option>)}
                </select>
            </div>
            
            <div className="upload-section">
                <h4>Загрузить новую картинку:</h4>
                <input type="file" accept="image/*" onChange={handleFileSelect} />
                {preview && <img src={preview} alt="preview" />}
                <button onClick={uploadImage} disabled={loading}>
                    {loading ? 'Загрузка...' : 'Загрузить'}
                </button>
                {selectedFolder === 'backgrounds' && preview && (
                    <button onClick={() => setBackground(preview)}>Установить как фон</button>
                )}
            </div>
            
            <h4>Существующие картинки:</h4>
            {loading ? (
                <div>Загрузка...</div>
            ) : (
                <div className="images-grid">
                    {images.map(img => (
                        <div key={img} className="image-card">
                            <img src={`/media/uploads/${selectedFolder}/${img}`} alt={img} onError={(e) => { e.target.src = ''; }} />
                            <div className="image-name">{img}</div>
                            {selectedFolder === 'backgrounds' && (
                                <button onClick={() => setBackground(`/media/uploads/backgrounds/${img}`)}>Сделать фоном</button>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

function CharactersScreen() 
{
    const [chars, setChars] = useState([]);
    const [metrics, setMetrics] = useState([]);
    const [newName, setNewName] = useState('');
    const [editingChar, setEditingChar] = useState(null);
    const [stats, setStats] = useState({});
    const [selectedImage, setSelectedImage] = useState('');
    const [imageFiles, setImageFiles] = useState([]);

    const fetchChars = async () => 
    {
        const res = await fetch('/api/characters', { credentials: 'include' });
        if (res.ok) setChars(await res.json());
    };

    const fetchMetrics = async () => 
    {
        const res = await fetch('/api/metrics', { credentials: 'include' });
        if (res.ok) setMetrics(await res.json());
    };

    const fetchImages = async () => 
    {
        try 
        {
            const res = await fetch('/api/images/characters', { credentials: 'include' });
            if (res.ok) 
            {
                const data = await res.json();
                setImageFiles(data);
            }
        } 
        catch(e) {}
    };

    const createChar = async () => 
    {
        const defaultStats = {};
        metrics.forEach(m => 
        {
            defaultStats[m.metric_name] = m.default_value || 0;
        });
        
        await fetch('/api/characters', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: newName, stats: defaultStats, image_path: selectedImage }),
            credentials: 'include'
        });
        fetchChars();
        setNewName('');
        setSelectedImage('');
    };

    const updateChar = async () => 
    {
        const updateData = { name: editingChar.name, stats: stats };
        if (selectedImage) updateData.image_path = selectedImage;
        
        await fetch(`/api/characters/${editingChar.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updateData),
            credentials: 'include'
        });
        setEditingChar(null);
        setStats({});
        setSelectedImage('');
        fetchChars();
    };

    const deleteChar = async (id) => 
    {
        await fetch(`/api/characters/${id}`, { method: 'DELETE', credentials: 'include' });
        fetchChars();
    };

    const startEdit = (char) => 
    {
        setEditingChar(char);
        setStats(char.stats || {});
        setSelectedImage(char.image_path || '');
    };

    useEffect(() => { fetchChars(); fetchMetrics(); fetchImages(); }, []);

    return (
        <div className="characters-screen">
            <h3>Персонажи</h3>
            <input placeholder="Имя персонажа" value={newName} onChange={e => setNewName(e.target.value)} />
            <select value={selectedImage} onChange={e => setSelectedImage(e.target.value)}>
                <option value="">Нет картинки</option>
                {imageFiles.map(img => <option key={img} value={`/media/uploads/characters/${img}`}>{img}</option>)}
            </select>
            <button onClick={createChar}>Добавить персонажа</button>
            
            {editingChar && (
                <div className="edit-form">
                    <h4>Редактирование: {editingChar.name}</h4>
                    <input value={editingChar.name} onChange={e => setEditingChar({...editingChar, name: e.target.value})} />
                    <select value={selectedImage} onChange={e => setSelectedImage(e.target.value)}>
                        <option value="">Нет картинки</option>
                        {imageFiles.map(img => <option key={img} value={`/media/uploads/characters/${img}`}>{img}</option>)}
                    </select>
                    <h5>Характеристики:</h5>
                    {metrics.map(m => (
                        <div key={m.id}>
                            <label>{m.metric_name}: </label>
                            <input 
                                type="number" 
                                value={stats[m.metric_name] !== undefined ? stats[m.metric_name] : (m.default_value || 0)} 
                                onChange={e => setStats({...stats, [m.metric_name]: parseInt(e.target.value) || 0})}
                            />
                        </div>
                    ))}
                    <button onClick={updateChar}>Сохранить</button>
                    <button onClick={() => { setEditingChar(null); setStats({}); setSelectedImage(''); }}>Отмена</button>
                </div>
            )}
            
            <ul>
                {chars.map(c => (
                    <li key={c.id}>
                        {c.name} - Характеристики: 
                        {metrics.map(m => `${m.metric_name}: ${c.stats?.[m.metric_name] || 0}`).join(', ')}
                        {c.image_path && <img src={c.image_path} alt={c.name} onError={(e) => e.target.style.display = 'none'} />}
                        <button onClick={() => startEdit(c)}>Ред</button> 
                        <button onClick={() => deleteChar(c.id)}>Удалить</button>
                    </li>
                ))}
            </ul>
        </div>
    );
}

function CardScreen({ onSelectCard }) 
{
    const [cards, setCards] = useState([]);
    const [newText, setNewText] = useState('');
    const [imageFiles, setImageFiles] = useState([]);
    const [selectedImage, setSelectedImage] = useState('');

    const fetchCards = async () => 
    {
        const res = await fetch('/api/cards', { credentials: 'include' });
        if (res.ok) setCards(await res.json());
    };

    const fetchImages = async () => 
    {
        try 
        {
            const res = await fetch('/api/images/cards', { credentials: 'include' });
            if (res.ok) 
            {
                const data = await res.json();
                setImageFiles(data);
            }
        } 
        catch(e) {}
    };

    const createCard = async () => 
    {
        await fetch('/api/cards', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ card_text: newText, image_path: selectedImage }),
            credentials: 'include'
        });
        fetchCards();
        setNewText('');
        setSelectedImage('');
    };

    const deleteCard = async (id) => 
    {
        await fetch(`/api/cards/${id}`, { method: 'DELETE', credentials: 'include' });
        fetchCards();
    };

    useEffect(() => { fetchCards(); fetchImages(); }, []);

    return (
        <div className="cards-screen">
            <h3>Карточки</h3>
            <input placeholder="Текст карточки" value={newText} onChange={e => setNewText(e.target.value)} />
            <select value={selectedImage} onChange={e => setSelectedImage(e.target.value)}>
                <option value="">Нет картинки</option>
                {imageFiles.map(img => <option key={img} value={`/media/uploads/cards/${img}`}>{img}</option>)}
            </select>
            <button onClick={createCard}>Добавить карточку</button>
            <ul>
                {cards.map(c => (
                    <li key={c.id} onClick={() => onSelectCard(c)} style={{ cursor: 'pointer' }}>
                        {c.card_text} 
                        {c.image_path && <img src={c.image_path} alt={c.card_text} onError={(e) => e.target.style.display = 'none'} />} 
                        <button onClick={(e) => { e.stopPropagation(); deleteCard(c.id); }}>Удалить</button>
                    </li>
                ))}
            </ul>
        </div>
    );
}

function AnswerScreen({ card, onBack }) 
{
    const [answers, setAnswers] = useState([]);
    const [metrics, setMetrics] = useState([]);
    const [newText, setNewText] = useState('');
    const [orderIndex, setOrderIndex] = useState(0);
    const [statsChange, setStatsChange] = useState({});
    const [editingAnswer, setEditingAnswer] = useState(null);

    const fetchAnswers = async () => 
    {
        const res = await fetch(`/api/answers?card_uuid=${card.card_uuid}`, { credentials: 'include' });
        if (res.ok) setAnswers(await res.json());
    };

    const fetchMetrics = async () => 
    {
        const res = await fetch('/api/metrics', { credentials: 'include' });
        if (res.ok) setMetrics(await res.json());
    };

    const createAnswer = async () => 
    {
        const response = await fetch('/api/answers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                card_uuid: card.card_uuid, 
                answer_text: newText, 
                stats_change: statsChange, 
                order_index: orderIndex 
            }),
            credentials: 'include'
        });
        
        if (response.ok) 
        {
            fetchAnswers();
            setNewText('');
            setOrderIndex(0);
            setStatsChange({});
        } 
        else 
        {
            const error = await response.json();
            console.error('Ошибка:', error);
        }
    };

    const updateAnswer = async () => 
    {
        await fetch(`/api/answers/${editingAnswer.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                answer_text: editingAnswer.answer_text, 
                stats_change: editingAnswer.stats_change, 
                order_index: editingAnswer.order_index 
            }),
            credentials: 'include'
        });
        setEditingAnswer(null);
        fetchAnswers();
    };

    const deleteAnswer = async (id) => 
    {
        await fetch(`/api/answers/${id}`, { method: 'DELETE', credentials: 'include' });
        fetchAnswers();
    };

    useEffect(() => { fetchAnswers(); fetchMetrics(); }, [card]);

    return (
        <div className="answers-screen">
            <button onClick={onBack}>Назад ко всем карточкам</button>
            <h3>Ответы для карточки: {card.card_text}</h3>
            
            <h4>Добавить ответ:</h4>
            <input placeholder="Текст ответа" value={newText} onChange={e => setNewText(e.target.value)} />
            <input type="number" placeholder="Порядок" value={orderIndex} onChange={e => setOrderIndex(parseInt(e.target.value))} />
            <h5>Изменение характеристик:</h5>
            {metrics.map(m => (
                <div key={m.id}>
                    <label>{m.metric_name}: </label>
                    <input type="number" value={statsChange[m.metric_name] || 0} onChange={e => setStatsChange({...statsChange, [m.metric_name]: parseInt(e.target.value)})} />
                </div>
            ))}
            <button onClick={createAnswer}>Добавить ответ</button>
            
            <h4>Существующие ответы:</h4>
            {answers.map(a => (
                <div key={a.id} className="answer-item">
                    {editingAnswer?.id === a.id ? (
                        <div>
                            <input value={editingAnswer.answer_text} onChange={e => setEditingAnswer({...editingAnswer, answer_text: e.target.value})} />
                            <input type="number" value={editingAnswer.order_index} onChange={e => setEditingAnswer({...editingAnswer, order_index: parseInt(e.target.value)})} />
                            {metrics.map(m => (
                                <div key={m.id}>
                                    <label>{m.metric_name}: </label>
                                    <input type="number" value={editingAnswer.stats_change?.[m.metric_name] || 0} onChange={e => setEditingAnswer({...editingAnswer, stats_change: {...editingAnswer.stats_change, [m.metric_name]: parseInt(e.target.value)}})} />
                                </div>
                            ))}
                            <button onClick={updateAnswer}>Сохранить</button>
                            <button onClick={() => setEditingAnswer(null)}>Отмена</button>
                        </div>
                    ) : (
                        <div>
                            <strong>{a.answer_text}</strong> (порядок: {a.order_index})
                            <div>Изменение статов: {JSON.stringify(a.stats_change)}</div>
                            <button onClick={() => setEditingAnswer(a)}>Ред</button>
                            <button onClick={() => deleteAnswer(a.id)}>Удалить</button>
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
}

function Admin({ onLogout }) 
{
    const [selectedCard, setSelectedCard] = useState(null);

    const exitAdmin = async () => 
    {
        await fetch(`/api/admin_exit`, {
            method: 'POST',
            credentials: 'include'
        });
        onLogout();
    };

    return (
        <div className="admin-container">
            <button onClick={exitAdmin} className="exit-button">Выйти</button>
            <h1>Админ панель</h1>
            
            <ImageManager />
            <MetricsScreen />
            <CharactersScreen />
            
            {!selectedCard ? (
                <CardScreen onSelectCard={setSelectedCard} />
            ) : (
                <AnswerScreen card={selectedCard} onBack={() => setSelectedCard(null)} />
            )}
        </div>
    );
}

export default Admin;