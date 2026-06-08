import React, { useState, useEffect } from "react";
import { adminApi } from "../../api";
import "./ImageManager.css"

function ImageManager() {
    const [backgrounds, setBackgrounds] = useState([]);
    const [characters, setCharacters] = useState([]);
    const [cards, setCards] = useState([]);
    const [currentBg, setCurrentBg] = useState('');
    const [selectedFolder, setSelectedFolder] = useState('backgrounds');
    const [uploadFile, setUploadFile] = useState(null);
    const [preview, setPreview] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState(null);

    const folders = [
        { key: 'backgrounds', label: 'Фоны', description: 'Фоновые изображения для игры' },
        { key: 'characters', label: 'Персонажи', description: 'Аватары и портреты персонажей' },
        { key: 'cards', label: 'Карточки', description: 'Изображения для вопросов и карточек' }
    ];

    const imagesMap = {
        backgrounds: backgrounds,
        characters: characters,
        cards: cards
    };

    const fetchImages = async () => {
        setLoading(true);
        try {
            const data = await adminApi.getImages(selectedFolder);
            if (selectedFolder === 'backgrounds') setBackgrounds(data);
            else if (selectedFolder === 'characters') setCharacters(data);
            else if (selectedFolder === 'cards') setCards(data);
        } 
        catch (err) {
            showMessage('Ошибка загрузки', 'error');
        } 
        finally {
            setLoading(false);
        }
    };

    const fetchCurrentBg = async () => {
        try {
            const data = await adminApi.getBg();
            setCurrentBg(data.bg_path);
        } 
        catch (err) {
            console.error('Failed to fetch bg:', err);
        }
    };

    const uploadImage = async () => {
        if (!uploadFile) {
            showMessage('Выберите файл', 'error');
            return;
        }
        setLoading(true);
        try {
            await adminApi.uploadImage(selectedFolder, uploadFile);
            showMessage('Изображение загружено!', 'success');
            setUploadFile(null);
            setPreview('');
            await fetchImages();
            if (selectedFolder === 'backgrounds') {
                await fetchCurrentBg();
            }
        } 
        catch (err) {
            showMessage('Ошибка загрузки', 'error');
        } 
        finally {
            setLoading(false);
        }
    };

    const setAsBackground = async (imagePath) => {
        setLoading(true);
        try {
            await adminApi.setBg(imagePath);
            setCurrentBg(imagePath);
            showMessage('Фон установлен!', 'success');
        } 
        catch (err) {
            showMessage('Ошибка установки фона', 'error');
        } 
        finally {
            setLoading(false);
        }
    };

    const showMessage = (text, type) => {
        setMessage({ text, type });
        setTimeout(() => setMessage(null), 3000);
    };

    const handleFileSelect = (e) => {
        const file = e.target.files[0];
        if (file && file.type.startsWith('image/')) {
            setUploadFile(file);
            setPreview(URL.createObjectURL(file));
        } 
        else {
            showMessage('Выберите изображение', 'error');
        }
    };

    useEffect(() => {
        fetchImages();
        if (selectedFolder === 'backgrounds') {
            fetchCurrentBg();
        }
    }, [selectedFolder]);

    const currentImages = imagesMap[selectedFolder] || [];

    return (
        <div className="image-manager">
            {message && <div className={`toast-message ${message.type}`}>{message.text}</div>}
            {selectedFolder === 'backgrounds' && (
                <div className="current-bg-section">
                    <h3>Текущий фон игры</h3>
                    <div className="current-bg-preview">
                        {currentBg ? (
                            <>
                                <img src={currentBg} alt="Current background" />
                                <div className="bg-path">{currentBg.split('/').pop()}</div>
                            </>
                        ) : (
                            <div className="no-bg">Фон не установлен</div>
                        )}
                    </div>
                </div>
            )}
            <div className="folder-tabs">
                {folders.map(folder => (
                    <button key={folder.key} className={`folder-tab ${selectedFolder === folder.key ? 'active' : ''}`} onClick={() => setSelectedFolder(folder.key)}>
                        {folder.label}
                        <span className="folder-desc">{folder.description}</span>
                    </button>
                ))}
            </div>
            <div className="upload-section">
                <h3>Загрузить новое изображение</h3>
                <div className="upload-area">
                    <input type="file" accept="image/*" onChange={handleFileSelect} id="fileInput" style={{ display: 'none' }} />
                    <label htmlFor="fileInput" className="upload-label">
                        {preview ? <img src={preview} alt="Preview" className="upload-preview" /> : <div className="upload-placeholder">Нажмите или перетащите файл</div>}
                    </label>
                    {uploadFile && (
                        <div className="upload-info">
                            <span>{uploadFile.name}</span>
                            <button onClick={uploadImage} disabled={loading}>{loading ? 'Загрузка...' : '⬆ Загрузить'}</button>
                        </div>
                    )}
                </div>
            </div>
            <div className="gallery-section">
                <h3>Галерея ({currentImages.length})</h3>
                {loading && !currentImages.length ? <div className="loading-spinner">Загрузка...</div> : currentImages.length === 0 ? <div className="empty-gallery">Нет изображений. Загрузите первое!</div> : (
                    <div className="images-grid">
                        {currentImages.map(img => {
                            const imageUrl = `/media/uploads/${selectedFolder}/${img}`;
                            return (
                                <div key={img} className="image-card">
                                    <img src={imageUrl} alt={img} />
                                    <div className="image-name" title={img}>{img.length > 30 ? img.slice(0, 27) + '...' : img}</div>
                                    <div className="image-actions">
                                        {selectedFolder === 'backgrounds' && (
                                            <button className={`set-bg-btn ${currentBg === imageUrl ? 'active' : ''}`} onClick={() => setAsBackground(imageUrl)} disabled={currentBg === imageUrl}>
                                                {currentBg === imageUrl ? 'Текущий фон' : 'Сделать фоном'}
                                            </button>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}

export default ImageManager;