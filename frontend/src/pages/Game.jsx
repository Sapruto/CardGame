import React, { useState, useEffect } from 'react';
import { getGameData, sendResultData } from '../api';
import "./Game.css"

function ResultScreen({ result, stats, onPlayAgain }) {
    return (
        <div className="result-screen">
            <h1>Результат!</h1>
            <p>{result.message}</p>
            <p>Ты похож на: {result.matched_character?.name}</p>
            
            <h3>Твои характеристики:</h3>
            <ul>
                {Object.entries(result.your_stats || stats).map(([key, value]) => (
                    <li key={key}>{key}: {value}</li>
                ))}
            </ul>
            
            <button onClick={onPlayAgain}>Сыграть снова</button>
        </div>
    );
}

function BeforeGameScreen({ characterName, stats }) {
    return (
        <div className="settings-screen">
            <h1>Начало игры</h1>
            
            <h2>Ваш персонаж: characterName</h2>

            <div className="stats-container">
                <h3>Ваши статистики:</h3>
                <ul>
                    {Object.entries(stats).map(([key, value]) => (
                        <li key={key}>{key}: {value}</li>
                    ))}
                </ul>
            </div>
        </div>
    );
}

function QuestionScreen({ question, index, total, stats, onAnswer, onExit }) {
    return (
        <div className="question-screen">
            <button className="exit-button" onClick={onExit}>Выйти из игры</button>
            <div className="question-counter">Вопрос {index + 1} из {total}</div>
            <h2>{question.text}</h2>
            
            <div className="answers-container">
                {question.answers.map((answer, idx) => (
                    <button 
                        key={idx}
                        className="answer-button"
                        onClick={() => onAnswer(answer)}
                    >
                        {answer.text}
                    </button>
                ))}
            </div>
            
            <div className="stats-container">
                <h3>Текущие статы:</h3>
                <ul>
                    {Object.entries(stats).map(([key, value]) => (
                        <li key={key}>{key}: {value}</li>
                    ))}
                </ul>
            </div>
        </div>
    );
}

function LoadingScreen() {
    return (
        <div className="loading-screen">
            <h1>Загрузка игры...</h1>
        </div>
    );
}

function SettingsScreen({ onStart, defaultRounds = 10 }) {
    const [rounds, setRounds] = useState(defaultRounds);
    
    return (
        <div className="settings-screen">
            <h1>Настройки игры</h1>
            
            <div className="rounds-input">
                <label>Количество раундов:</label>
                <input 
                    type="number" 
                    min="1" 
                    max="50" 
                    value={rounds}
                    onChange={(e) => setRounds(Number(e.target.value))}
                />
                <p>Выбери количество вопросов (от 1 до 50)</p>
            </div>
            
            <button 
                className="start-button"
                onClick={() => onStart(rounds)}
            >
                Начать игру!
            </button>
        </div>
    );
}

function Game() {
    const GameStates = Object.freeze({
        Settings: SettingsScreen,
        BeforeGame: BeforeGameScreen,
        InGame: QuestionScreen,
        EndGame: ResultScreen
    });

    const loadSavedState = () => {
        const saved = localStorage.getItem('gameState');
        if (saved) {
            try {
                const state = JSON.parse(saved);
                if (state.timestamp && Date.now() - state.timestamp < 3600000) {
                    return state;
                }
            } 
            catch(e) {
                console.error('Error loading saved state:', e);
            }
        }
        return null;
    };

    const savedState = loadSavedState();

    const [questions, setQuestions] = useState(savedState?.questions || []);
    const [currentIndex, setCurrentIndex] = useState(savedState?.currentIndex || 0);
    const [currentStats, setCurrentStats] = useState(savedState?.currentStats || {});
    const [answers, setAnswers] = useState(savedState?.answers || []);
    const [loading, setLoading] = useState(!savedState);
    const [result, setResult] = useState(null);
    const [matchedCharacterId, setMatchedCharacterId] = useState(null);
    const [gameStarted, setGameStarted] = useState(savedState?.gameStarted || false);
    const [selectedRounds, setSelectedRounds] = useState(savedState?.selectedRounds || 10);

    const [gameState, setGameState] = useState(savedState?.gameState || GameStates.Settings);

    useEffect(() => {
        if (gameStarted && !result && questions.length > 0) {
            const stateToSave = {
                questions,
                currentIndex,
                currentStats,
                answers,
                gameStarted,
                selectedRounds,
                timestamp: Date.now()
            };
            localStorage.setItem('gameState', JSON.stringify(stateToSave));
        }
    }, [questions, currentIndex, currentStats, answers, gameStarted, selectedRounds, result]);

    const startGame = async (rounds) => {
        setSelectedRounds(rounds);
        setLoading(true);
        setGameStarted(true);
        
        localStorage.removeItem('gameState');
        
        try {
            const response = await fetch(`/api/start_game?max_rounds=${rounds}`);
            const data = await response.json();
            setQuestions(data.questions || []);
            setCurrentStats(data.character?.stats || {});
        } 
        catch (err) {
            console.error('API error:', err);
        } 
        finally {
            setLoading(false);
        }
    };

    const handleAnswer = async (selectedAnswer) => {
        const newAnswers = [...answers, selectedAnswer];
        const newStats = { ...currentStats };
        
        for (const [metric, change] of Object.entries(selectedAnswer.stats_change)) {
            newStats[metric] = (newStats[metric] || 0) + change;
        }
        
        const nextIndex = currentIndex + 1;
        
        if (nextIndex >= questions.length) {
            setLoading(true);
            try {
                const characterId = matchedCharacterId || 1;
                const resultData = await sendResultData(newStats, characterId);
                setResult(resultData);
                localStorage.removeItem('gameState');
            } 
            catch (error) {
                console.error('Error sending result:', error);
            } 
            finally {
                setLoading(false);
            }
        } 
        else {
            setAnswers(newAnswers);
            setCurrentStats(newStats);
            setCurrentIndex(nextIndex);
        }
    };

    const handlePlayAgain = () => {
        localStorage.removeItem('gameState');
        window.location.reload();
    };

    const handleExitGame = () => {
        localStorage.removeItem('gameState');
        setGameStarted(false);
        setQuestions([]);
        setCurrentIndex(0);
        setCurrentStats({});
        setAnswers([]);
        setResult(null);
        setLoading(false);
    };
    
    if (!gameStarted) {
        return <SettingsScreen onStart={startGame} defaultRounds={10} />;
    }

    if (gameState) {
        return <BeforeGameScreen />
    }

    if (loading && !result) {
        return <LoadingScreen />;
    }
    
    if (result) {
        return <ResultScreen 
            result={result} 
            stats={currentStats}
            onPlayAgain={handlePlayAgain} 
        />;
    }
    
    if (!questions.length) {
        return <div className="loading-screen">Нет вопросов</div>;
    }
    
    return <QuestionScreen 
        question={questions[currentIndex]}
        index={currentIndex}
        total={questions.length}
        stats={currentStats}
        onAnswer={handleAnswer}
        onExit={handleExitGame}
    />;
}

export default Game;