import React, { useState, useEffect } from 'react';
import { gameApi } from '../api';
import "./Game.css"

function ResultScreen({ result, stats, onPlayAgain }) {
    return (
        <div className="result-screen">
            <h1>Результат!</h1>
            <p>{result.epilogue?.text || "Игра завершена"}</p>
            
            <h3>Твои характеристики:</h3>
            <ul>
                {Object.entries(stats).map(([key, value]) => (
                    <li key={key}>{key}: {value}</li>
                ))}
            </ul>
            
            <button onClick={onPlayAgain}>Сыграть снова</button>
        </div>
    );
}

function BeforeGameScreen({ characterName, onStartGame }) {
    return (
        <div className="settings-screen">
            <h1>Начало игры</h1>
            <h2>Ваш персонаж: {characterName}</h2>
            <button onClick={onStartGame}>Начать игру!</button>
        </div>
    );
}

function QuestionScreen({ question, stats, onAnswer, onExit }) {
    return (
        <div className="question-screen">
            <button className="exit-button" onClick={onExit}>Выйти из игры</button>
            <h2>{question.text}</h2>
            
            <div className="answers-container">
                {question.answers?.map((answer, idx) => (
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

function StartScreen({ onStart }) {
    return (
        <div className="start-screen">
            <h1>Игра-тест</h1>
            <button onClick={onStart}>Начать игру</button>
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

function Game() {
    const GameStates = Object.freeze({
        SETTINGS: "Settings",
        BEFORE_GAME: "BeforeGame",
        IN_GAME: "InGame",
        END_GAME: "EndGame",
        LOADING_GAME: "LoadingGame"
    })

    const [currentState, setCurrentState] = useState(GameStates.SETTINGS)
    const [currentQuestion, setCurrentQuestion] = useState(null)
    const [currentStats, setCurrentStats] = useState({})
    const [result, setResult] = useState(null)
    const [character, setCharacter] = useState(null)
    const [bgPath, setBgPath] = useState("")

    const startPlaying = () => {
        setCurrentState(GameStates.IN_GAME)
    }

    const startNewGame = async () => {
        setCurrentState(GameStates.LOADING_GAME);
        
        try {
            const data = await gameApi.startGame();
            
            setCharacter(data.character);
            setCurrentQuestion(data.question);
            setBgPath(data.bg_path);
            
            const initialStats = {};
            (data.actual_metrics || []).forEach(metric => {
                initialStats[metric.name] = metric.value;
            });
            setCurrentStats(initialStats);
            
            setCurrentState(GameStates.BEFORE_GAME);
        } 
        catch (err) {
            console.error(err);
            setCurrentState(GameStates.SETTINGS);
        }
    };

    const handleAnswer = async (selectedAnswer) => {
        setCurrentState(GameStates.LOADING_GAME);
        
        try {
            const metrics = Object.entries(currentStats).map(([name, value]) => ({
                name: name,
                value: value
            }));
            
            const response = await gameApi.resumeOrEndGame(
                metrics,
                currentQuestion,
                selectedAnswer.id
            );
            
            if (response.epilogue) {
                setResult(response);
                setCurrentState(GameStates.END_GAME);
            } 
            else {
                const newStats = {};
                (response.actual_metrics || []).forEach(metric => {
                    newStats[metric.name] = metric.value;
                });
                
                setCurrentStats(newStats);
                setCurrentQuestion(response.question);
                setCurrentState(GameStates.IN_GAME);
            }
        } 
        catch (err) {
            console.error(err);
            setCurrentState(GameStates.IN_GAME);
        }
    };

    const handlePlayAgain = () => {
        setCurrentState(GameStates.SETTINGS);
        setCurrentQuestion(null);
        setCurrentStats({});
        setResult(null);
        setCharacter(null);
        setBgPath("");
    }

    const handleExitGame = () => {
        setCurrentState(GameStates.SETTINGS);
        setCurrentQuestion(null);
        setCurrentStats({});
        setResult(null);
        setCharacter(null);
        setBgPath("");
    }

    const screens = {
        [GameStates.SETTINGS]: <StartScreen onStart={startNewGame} />,
        [GameStates.BEFORE_GAME]: <BeforeGameScreen 
            characterName={character?.name || "Персонаж"} 
            onStartGame={startPlaying}
        />,
        [GameStates.IN_GAME]: currentQuestion && (
            <QuestionScreen 
                question={currentQuestion} 
                stats={currentStats} 
                onAnswer={handleAnswer} 
                onExit={handleExitGame} 
            />
        ),
        [GameStates.END_GAME]: result && (
            <ResultScreen 
                result={result} 
                stats={currentStats} 
                onPlayAgain={handlePlayAgain} 
            />
        ),
        [GameStates.LOADING_GAME]: <LoadingScreen />
    }

    return screens[currentState] || <StartScreen onStart={startNewGame} />;
}

export default Game;