import React, { useState, useEffect } from "react";
import { adminApi } from "../../api";
import ImageManager from "./ImageManager"
import "./Admin.css"

const AdminStates = Object.freeze({
    MAIN: "MAIN",
    IMAGES: "IMAGES",
    METRICS: "METRICS",
    CHARACTERS: "CHARACTERS",
    CARDS: "CARDS"
})

function MetricsScreen() 
{
    const [metrics, setMetrics] = useState([]);
    const [newName, setNewName] = useState('');
    const [newDesc, setNewDesc] = useState('');
    const [newDefault, setNewDefault] = useState(0);

    const fetchMetrics = async () => {
        const data = await adminApi.getMetrics();
        setMetrics(data);
    };

    const createMetric = async () => {
        await adminApi.createMetric({ metric_name: newName, description: newDesc, default_value: newDefault });
        await fetchMetrics();
        setNewName('');
        setNewDesc('');
        setNewDefault(0);
    };

    const deleteMetric = async (id) => {
        await adminApi.deleteMetric(id);
        await fetchMetrics();
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

function CharactersScreen() 
{
    const [chars, setChars] = useState([]);
    const [metrics, setMetrics] = useState([]);
    const [newName, setNewName] = useState('');
    const [editingChar, setEditingChar] = useState(null);
    const [stats, setStats] = useState({});
    const [selectedImage, setSelectedImage] = useState('');
    const [imageFiles, setImageFiles] = useState([]);

    const fetchChars = async () => {
        const data = await adminApi.getCharacters();
        setChars(data);
    };

    const fetchMetrics = async () => {
        const data = await adminApi.getMetrics();
        setMetrics(data);
    };

    const fetchImages = async () => {
        try {
            const data = await adminApi.getImages('characters');
            setImageFiles(data);
        } 
        catch(e) {}
    };

    const createChar = async () => {
        const defaultStats = {};
        metrics.forEach(m => {
            defaultStats[m.metric_name] = m.default_value || 0;
        });
        await adminApi.createCharacter({ name: newName, stats: defaultStats, image_path: selectedImage });
        await fetchChars();
        setNewName('');
        setSelectedImage('');
    };

    const updateChar = async () => {
        const updateData = { name: editingChar.name, stats: stats };
        if (selectedImage) updateData.image_path = selectedImage;
        await adminApi.updateCharacter(editingChar.id, updateData);
        setEditingChar(null);
        setStats({});
        setSelectedImage('');
        await fetchChars();
    };

    const deleteChar = async (id) => {
        await adminApi.deleteCharacter(id);
        await fetchChars();
    };

    const startEdit = (char) => {
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
                            <input type="number" value={stats[m.metric_name] !== undefined ? stats[m.metric_name] : (m.default_value || 0)} onChange={e => setStats({...stats, [m.metric_name]: parseInt(e.target.value) || 0})} />
                        </div>
                    ))}
                    <button onClick={updateChar}>Сохранить</button>
                    <button onClick={() => { setEditingChar(null); setStats({}); setSelectedImage(''); }}>Отмена</button>
                </div>
            )}
            
            <ul>
                {chars.map(c => (
                    <li key={c.id}>
                        {c.name} - Характеристики: {metrics.map(m => `${m.metric_name}: ${c.stats?.[m.metric_name] || 0}`).join(', ')}
                        {c.image_path && <img src={c.image_path} alt={c.name} onError={(e) => e.target.style.display = 'none'} />}
                        <button onClick={() => startEdit(c)}>Ред</button> 
                        <button onClick={() => deleteChar(c.id)}>Удалить</button>
                    </li>
                ))}
            </ul>
        </div>
    );
}

function QuestionScreen({ onSelectQuestion }) 
{
    const [questions, setQuestions] = useState([]);
    const [newText, setNewText] = useState('');
    const [imageFiles, setImageFiles] = useState([]);
    const [selectedImage, setSelectedImage] = useState('');
    const [nextQuestionUuid, setNextQuestionUuid] = useState('');
    const [isFirst, setIsFirst] = useState(false);
    const [editingQuestion, setEditingQuestion] = useState(null);
    const [editingId, setEditingId] = useState(null);

    const fetchQuestions = async () => {
        const data = await adminApi.getCards();
        setQuestions(data);
    };

    const fetchImages = async () => {
        try {
            const data = await adminApi.getImages('cards');
            setImageFiles(data);
        } 
        catch(e) {}
    };

    const createQuestion = async () => {
        if (isFirst && !nextQuestionUuid) {
            alert('Первая карточка должна иметь следующую');
            return;
        }

        await adminApi.createCard({ 
            card_text: newText, 
            image_path: selectedImage,
            next_question_uuid: nextQuestionUuid || null,
            is_first: isFirst
        });
        await fetchQuestions();
        setNewText('');
        setSelectedImage('');
        setNextQuestionUuid('');
        setIsFirst(false);
    };

    const updateQuestion = async () => {
        const updateData = {
            card_text: editingQuestion.card_text,
            image_path: editingQuestion.image_path,
            next_question_uuid: editingQuestion.next_question_uuid || null,
            is_first: editingQuestion.is_first
        };
        await adminApi.updateCard(editingQuestion.id, updateData);
        setEditingQuestion(null);
        setEditingId(null);
        await fetchQuestions();
    };

    const deleteQuestion = async (id) => {
        await adminApi.deleteCard(id);
        await fetchQuestions();
    };

    const startEdit = (question) => {
        setEditingQuestion({...question});
        setEditingId(question.id);
    };

    const cancelEdit = () => {
        setEditingQuestion(null);
        setEditingId(null);
    };

    useEffect(() => { fetchQuestions(); fetchImages(); }, []);

    const questionOptions = questions.filter(q => q.card_uuid && !q.is_first && q.id !== editingId);

    return (
        <div className="cards-screen">
            <h3>Карточки</h3>
            
            {!editingQuestion ? (
                <div className="edit-form">
                    <h4>Создать новую карточку</h4>
                    <input 
                        placeholder="Текст карточки" 
                        value={newText} 
                        onChange={e => setNewText(e.target.value)} 
                    />
                    <select value={selectedImage} onChange={e => setSelectedImage(e.target.value)}>
                        <option value="">Нет картинки</option>
                        {imageFiles.map(img => <option key={img} value={`/media/uploads/cards/${img}`}>{img}</option>)}
                    </select>
                    
                    <label style={{ display: 'block', margin: '10px 0' }}>
                        <input 
                            type="checkbox" 
                            checked={isFirst} 
                            onChange={(e) => setIsFirst(e.target.checked)} 
                        />
                        Это первая карточка (начало игры)
                    </label>
                    
                    <select value={nextQuestionUuid} onChange={e => setNextQuestionUuid(e.target.value)}>
                        <option value="">--- Нет следующей карточки (конец) ---</option>
                        {questionOptions.map(q => (
                            <option key={q.id} value={q.card_uuid}>
                                {q.card_text.length > 50 ? q.card_text.substring(0, 50) + '...' : q.card_text}
                            </option>
                        ))}
                    </select>
                    
                    <button onClick={createQuestion}>Добавить карточку</button>
                </div>
            ) : (
                <div className="edit-form">
                    <h4>Редактирование карточки</h4>
                    <input 
                        value={editingQuestion.card_text} 
                        onChange={e => setEditingQuestion({...editingQuestion, card_text: e.target.value})} 
                    />
                    <select value={editingQuestion.image_path || ""} onChange={e => setEditingQuestion({...editingQuestion, image_path: e.target.value})}>
                        <option value="">Нет картинки</option>
                        {imageFiles.map(img => <option key={img} value={`/media/uploads/cards/${img}`}>{img}</option>)}
                    </select>
                    
                    <label style={{ display: 'block', margin: '10px 0' }}>
                        <input 
                            type="checkbox" 
                            checked={editingQuestion.is_first || false} 
                            onChange={(e) => {
                                const newIsFirst = e.target.checked;
                                setEditingQuestion({
                                    ...editingQuestion, 
                                    is_first: newIsFirst
                                });
                            }} 
                        />
                        Это первая карточка
                    </label>
                    
                    <select 
                        value={editingQuestion.next_question_uuid || ""} 
                        onChange={e => setEditingQuestion({...editingQuestion, next_question_uuid: e.target.value || null})}
                    >
                        <option value="">--- Нет следующей карточки (конец) ---</option>
                        {questions.filter(q => q.id !== editingQuestion.id && !q.is_first).map(q => (
                            <option key={q.id} value={q.card_uuid}>
                                {q.card_text.length > 50 ? q.card_text.substring(0, 50) + '...' : q.card_text}
                            </option>
                        ))}
                    </select>
                    
                    <button onClick={updateQuestion}>Сохранить</button>
                    <button onClick={cancelEdit}>Отмена</button>
                </div>
            )}
            
            <h4>Список карточек</h4>
            <ul>
                {questions.map(q => (
                    <li 
                        key={q.id} 
                        style={{ 
                            background: editingId === q.id ? '#2a1f0a' : '#0a0a0a',
                            borderColor: editingId === q.id ? '#f5a623' : '#5959c5',
                            padding: '10px',
                            margin: '5px 0',
                            border: '1px solid',
                            borderRadius: '4px'
                        }}
                    >
                        <div>
                            {q.card_text}
                            {q.is_first && <span style={{ color: '#4a90e2', marginLeft: '10px' }}>[СТАРТ]</span>}
                            {!q.next_question_uuid && !q.is_first && <span style={{ color: '#e74c3c', marginLeft: '10px' }}>[КОНЕЦ]</span>}
                            {q.next_question_uuid && <span style={{ color: '#27ae60', marginLeft: '10px' }}>→ {questions.find(x => x.card_uuid === q.next_question_uuid)?.card_text || '?'}</span>}
                            {q.image_path && <img src={q.image_path} alt={q.card_text} style={{ maxWidth: '40px', marginLeft: '10px' }} onError={(e) => e.target.style.display = 'none'} />}
                        </div>
                        <div style={{ marginTop: '8px' }}>
                            <button 
                                onClick={() => startEdit(q)} 
                                style={{ 
                                    background: editingId === q.id ? '#f5a623' : '#2a2a2a',
                                    color: editingId === q.id ? '#0a0a0a' : '#a3abe8',
                                    marginRight: '5px'
                                }}
                            >
                                {editingId === q.id ? 'Редактируется' : 'Ред'}
                            </button>
                            <button onClick={() => onSelectQuestion(q)} style={{ marginRight: '5px' }}>
                                Ответы
                            </button>
                            <button onClick={() => deleteQuestion(q.id)}>Удалить</button>
                        </div>
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

    const fetchAnswers = async () => {
        const data = await adminApi.getAnswers(card.card_uuid);
        setAnswers(data);
    };

    const fetchMetrics = async () => {
        const data = await adminApi.getMetrics();
        setMetrics(data);
    };

    const createAnswer = async () => {
        const statsChangeArray = Object.entries(statsChange).map(([stat_name, delta]) => ({
            stat_name: stat_name,
            delta: delta
        }));

        await adminApi.createAnswer({ 
            card_uuid: card.card_uuid, 
            answer_text: newText, 
            stats_change: statsChangeArray, 
            order_index: orderIndex 
        });
        await fetchAnswers();
        setNewText('');
        setOrderIndex(0);
        setStatsChange({});
    };

    const updateAnswer = async () => {
        await adminApi.updateAnswer(editingAnswer.id, { 
            answer_text: editingAnswer.answer_text, 
            stats_change: editingAnswer.stats_change, 
            order_index: editingAnswer.order_index 
        });
        setEditingAnswer(null);
        await fetchAnswers();
    };

    const deleteAnswer = async (id) => {
        await adminApi.deleteAnswer(id);
        await fetchAnswers();
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

function MainScreen() {
    return (<div className="main-screen"><h1>Добро пожаловать в админ панель</h1></div>);
}

function Navbar({ setState, onExit, currentState }) {
    const menuItems = [
        { id: AdminStates.MAIN, label: 'Главная' },
        { id: AdminStates.IMAGES, label: 'Картинки' },
        { id: AdminStates.METRICS, label: 'Метрики' },
        { id: AdminStates.CHARACTERS, label: 'Персонажи' },
        { id: AdminStates.CARDS, label: 'Карточки' }
    ];

    return (
        <div className="admin-navbar">
            {menuItems.map(item => (
                <button key={item.id} className={currentState === item.id ? 'active' : ''} onClick={() => setState(item.id)}>
                    {item.label}
                </button>
            ))}
            <button onClick={onExit} className="exit-button">Выйти</button>
        </div>
    );
}

function Admin({ onLogout }) 
{
    const [selectedCard, setSelectedCard] = useState(null);
    const [currentState, setCurrentState] = useState(AdminStates.MAIN);

    const exitAdmin = async () => {
        await adminApi.adminLogout();
        onLogout();
    };

    if (selectedCard) {
        return (
            <div className="admin-container">
                <Navbar setState={setCurrentState} onExit={exitAdmin} currentState={currentState} />
                <AnswerScreen card={selectedCard} onBack={() => setSelectedCard(null)} />
            </div>
        );
    }

    const screens = {
        [AdminStates.MAIN]: <MainScreen />,
        [AdminStates.IMAGES]: <ImageManager />,
        [AdminStates.METRICS]: <MetricsScreen />,
        [AdminStates.CHARACTERS]: <CharactersScreen />,
        [AdminStates.CARDS]: <QuestionScreen onSelectQuestion={setSelectedCard} />
    };

    return (
        <div className="admin-container">
            <Navbar setState={setCurrentState} onExit={exitAdmin} currentState={currentState} />
            {screens[currentState] || screens[AdminStates.MAIN]}
        </div>
    );
}

export default Admin;