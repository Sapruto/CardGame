const API_BASE_URL = "http://127.0.0.1:8000";

export const gameApi = {
    async startGame(questionUuid = "") {
        const response = await fetch(`${API_BASE_URL}/api/start_game?question_uuid=${questionUuid}`);
        if (!response.ok) throw new Error('Network error');
        return await response.json();
    },

    async resumeOrEndGame(actualMetrics, question, answerId) {
        const response = await fetch(`${API_BASE_URL}/api/resume_or_end_game`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                actual_metrics: actualMetrics,
                question: question,
                answer_id: answerId
            })
        });
        if (!response.ok) throw new Error('Network error');
        return await response.json();
    }
}




export const adminApi = {
    async getMetrics() {
        const res = await fetch(`${API_BASE_URL}/api/metrics`, { credentials: 'include' });
        if (!res.ok) throw new Error('Failed to fetch metrics');
        return res.json();
    },
    
    async createMetric(data) {
        const res = await fetch(`${API_BASE_URL}/api/metrics`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
            credentials: 'include'
        });
        if (!res.ok) throw new Error('Failed to create metric');
        return res.json();
    },
    
    async deleteMetric(id) {
        const res = await fetch(`${API_BASE_URL}/api/metrics/${id}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        if (!res.ok) throw new Error('Failed to delete metric');
        return res.json();
    },
    
    async getCharacters() {
        const res = await fetch(`${API_BASE_URL}/api/characters`, { credentials: 'include' });
        if (!res.ok) throw new Error('Failed to fetch characters');
        return res.json();
    },
    
    async createCharacter(data) {
        const res = await fetch(`${API_BASE_URL}/api/characters`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
            credentials: 'include'
        });
        if (!res.ok) throw new Error('Failed to create character');
        return res.json();
    },
    
    async updateCharacter(id, data) {
        const res = await fetch(`${API_BASE_URL}/api/characters/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
            credentials: 'include'
        });
        if (!res.ok) throw new Error('Failed to update character');
        return res.json();
    },
    
    async deleteCharacter(id) {
        const res = await fetch(`${API_BASE_URL}/api/characters/${id}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        if (!res.ok) throw new Error('Failed to delete character');
        return res.json();
    },
    
    async getCards() {
        const res = await fetch(`${API_BASE_URL}/api/cards`, { credentials: 'include' });
        if (!res.ok) throw new Error('Failed to fetch cards');
        return res.json();
    },
    
    async createCard(data) {
        const res = await fetch(`${API_BASE_URL}/api/cards`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
            credentials: 'include'
        });
        if (!res.ok) throw new Error('Failed to create card');
        return res.json();
    },

    async updateCard(id, data) {
        const res = await fetch(`${API_BASE_URL}/api/cards/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
            credentials: 'include'
        });
        if (!res.ok) throw new Error('Failed to update card');
        return res.json();
    },
    
    async deleteCard(id) {
        const res = await fetch(`${API_BASE_URL}/api/cards/${id}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        if (!res.ok) throw new Error('Failed to delete card');
        return res.json();
    },
    
    async getAnswers(cardUuid) {
        const res = await fetch(`${API_BASE_URL}/api/answers?card_uuid=${cardUuid}`, { credentials: 'include' });
        if (!res.ok) throw new Error('Failed to fetch answers');
        return res.json();
    },
    
    async createAnswer(data) {
        const res = await fetch(`${API_BASE_URL}/api/answers`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
            credentials: 'include'
        });
        if (!res.ok) throw new Error('Failed to create answer');
        return res.json();
    },
    
    async updateAnswer(id, data) {
        const res = await fetch(`${API_BASE_URL}/api/answers/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
            credentials: 'include'
        });
        if (!res.ok) throw new Error('Failed to update answer');
        return res.json();
    },
    
    async deleteAnswer(id) {
        const res = await fetch(`${API_BASE_URL}/api/answers/${id}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        if (!res.ok) throw new Error('Failed to delete answer');
        return res.json();
    },
    
    async getImages(folder) {
        const res = await fetch(`${API_BASE_URL}/api/images/${folder}`, { credentials: 'include' });
        if (!res.ok) throw new Error('Failed to fetch images');
        return res.json();
    },
    
    async uploadImage(folder, file) {
        const formData = new FormData();
        formData.append('folder', folder);
        formData.append('file', file);
        
        const res = await fetch(`${API_BASE_URL}/api/upload_image`, {
            method: 'POST',
            credentials: 'include',
            body: formData
        });
        if (!res.ok) throw new Error('Failed to upload image');
        return res.json();
    },
    
    async getBg() {
        const res = await fetch(`${API_BASE_URL}/api/resources/bg`, { credentials: 'include' });
        if (!res.ok) throw new Error('Failed to fetch bg');
        return res.json();
    },
    
    async setBg(bgPath) {
        const res = await fetch(`${API_BASE_URL}/api/resources/bg`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ bg_path: bgPath }),
            credentials: 'include'
        });
        if (!res.ok) throw new Error('Failed to set bg');
        return res.json();
    },
    
    async adminLogin(password) {
        const formData = new FormData();
        formData.append('password', password);
        
        const res = await fetch(`${API_BASE_URL}/api/admin_login`, {
            method: 'POST',
            body: formData,
            credentials: 'include'
        });
        if (!res.ok) throw new Error('Invalid password');
        return res.json();
    },
    
    async adminLogout() {
        const res = await fetch(`${API_BASE_URL}/api/admin_exit`, {
            method: 'POST',
            credentials: 'include'
        });
        if (!res.ok) throw new Error('Logout failed');
        return res.json();
    }
};