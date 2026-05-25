export const getGameData = () => 
    fetch('/api/start_game?max_rounds=10')
        .then(r => {
            if (!r.ok) throw new Error('Network error');
            return r.json();
        });

export const sendResultData = (finalStats, characterId) => {
    return fetch('/api/end_game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            final_stats: finalStats,
            character_id: characterId
        })
    }).then(r => {
        if (!r.ok) throw new Error('Network error');
        return r.json();
    });
};
