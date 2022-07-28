import "./style/main.scss";
import {CodeBlock, dracula} from "react-code-blocks";
import {BrowserRouter, Link, Route, Routes} from "react-router-dom"

import React, {useEffect, useRef, useState} from 'react';

/**
 * @description Takes a type which correlates to the backend. Available types right now is:
 *
 * - 'get_question'
 * - 'answered_question'
 * - 'insert_new_question'
 * - TODO: Needs to be implemented more
 *  - 'token_pls' - gets token for security
 * @param {string} type
 * @param {Object} data
 * @returns {string}
 */
const createMessage = (type, data) => {

    return JSON.stringify({ 'type': type, 'data': data});
}

/**
 * @description Makes debug messages
 * @param {string} type
 * @param {Object} data
 * @returns {`${string} <> tupilaqs <> DEBUG <> ${string} - ${string}`}
 */
const debugMessage = (type, data) => {
    const date = new Date().toUTCString();
    return `${date} <> tupilaqs <> DEBUG <> ${type} - ${JSON.stringify(data)}`;
}

const LandingPage = ({ webSocket, setUserName, userName}) => {
    const [error, setError] = useState("")
    const add_new_question = (e) => {
        e.preventDefault();
        if (userName) {
               const itemId = document.getElementById("itemID").value;
               const new_question_text = document.getElementById("newQuestionText").value;
               const correct_answer = document.getElementById("correctAnswer").value;
               const new_question_title = document.getElementById("newQuestionTitle").value;
               const new_question_explanation = document.getElementById("newQuestionExplanation").value;

                const request = {
                    user: itemId,
                    question: new_question_text,
                    correct_answer: correct_answer,
                    new_question_title: new_question_title,
                    new_question_explanation: new_question_explanation,
                };


                webSocket.send(createMessage('insert_new_question', request))
        } else {
            setError("The user name field must be filled in")
        }

        clearAddQ();
    }

    const clearAddQ = () => {
        document.getElementById("newQuestionText").value = "";
        document.getElementById("correctAnswer").value = "";
        document.getElementById("newQuestionTitle").value = "";
        document.getElementById("newQuestionExplanation").value = "";
    }

    return (
        <div>
            <div className="inputs registration">
                <input type="text" value={userName} onChange={e => setUserName(e.target.value)} className="input-base" id="itemID" placeholder="Username: "/>
                 <p className="error">{error}</p>
            </div>
            <Link to={userName ? "/categories" : ""}><button className="bb-button start-button">New Game</button></Link>
            <h1 className="main-title center">Add custom questions </h1>
            <div className="inputs">
                <input type="text" className="input-base" id="newQuestionText" placeholder="New Question: "/>
                <input type="text" className="input-base" id="correctAnswer" placeholder='"Bug" or "feature":'/>
                <input type="text" className="input-base" id="newQuestionTitle" placeholder="Question title:"/>
                <input type="text" className="input-base" id="newQuestionExplanation" placeholder="Question explanation:"/>
                <button className="bb-button small-height" onClick={(e) => add_new_question(e)}>Send</button>

            </div>
            <div className="debug">
                <ul id='messages'>
                    <h2 className="main-title center">Current token from Server: {}</h2>
                </ul>
            </div>
        </div>
    )
}

//FIXME: Did not work: function CodeBox({ getQuestion }) {
const Box = ({ webSocket, userName, wsMessage, questions, setQuestions }) => {
    const [isStarted, setStarted] = useState(false);

    useEffect(() => {
        if (isStarted) return;
        startGame();
    }, []);

    /**
     * For starting game, should probably be expanded upon.
     */
    const startGame = () => {
        const data = {
            'user_name': userName
        }
        webSocket?.send(createMessage('get_question', data));
        setStarted(true);
    }

    /**
     * @description Sends the guess of the player to backend to verify.
     * @param {Event} e
     * @param {string} guess
     */
    const handleGuess = (e, guess) => {
        e.preventDefault();
        if (!questions.answer) return;

        if (questions.answer.toString().toLowerCase() === guess) {
            console.log("You got it correct!!");
            // Now it needs to get a new question, answer
            // Add it to the users correct_answers in DB
        } else {
            console.log("THAT'S WRONG YOU NERD, HA!");
        }
    }

    return (
         <div className="box">

                <div>
                    <h1 className="main-title">{questions.title ? questions.title : 'title'}</h1>
                </div>
                <div>
                    <h4 style={{maxWidth: '550px', color: '#FFC0CB'}}>
                        {questions.expl ? questions.expl : 'explanation'}
                    </h4>
                    <br />
                    <h4 style={{color: '#FFC0CB'}}>
                        Difficulty: {questions.difficulty ? questions.difficulty : 'difficulty'}
                    </h4>
                    <h4 style={{maxWidth: '550px', color: '#FFC0CB'}}>
                        Votes: {questions.votes ? questions.votes : 'votes'}
                    </h4>
                </div>
                <div className="code-snippet">
                    <MyCoolCodeBlock code={questions.txt ? questions.txt : ''} language={"python"}/>
                </div>
                <div className="buttons">
                    <button className="bb-button bug" onClick={(e) => handleGuess(e, 'bug')}>
                        Bug
                    </button>
                    <button className="bb-button feature" onClick={(e) => handleGuess(e, 'feature')}>
                        Feature
                    </button>
                    <Link to="/">
                        <button className="bb-button upload">
                            Upload my own question!
                        </button>
                    </Link>
                </div>
          </div>

    )
}

function MyCoolCodeBlock({ code, language }) {
  return (<CodeBlock
	      text={code}
	      language={language}
	      showLineNumbers={true}
	      startingLineNumber={1}
	      theme={dracula}
	      codeBlock
	  />);
}

function App() {
    // Tried to define this useState at this level, and then pass the getQuestion reference
    // down to the CodeBox function
    // const [getQuestion, setQuestion] = useState("print('hello world')");
    //FIXME:Did not work: <Route path="/categories" element={CodeBox(getQuestion)}/>

    const socketURL = useRef('ws://localhost:8000/quiz');
    const ws = useRef(null);
    const [token, setToken] = useState('');
    const [wsMessage, setWSMessage] = useState('');
    const [questions, setQuestions] = useState([]);
    const [userName, setUserName] = useState('');

    // Only runs when connection is open and closed.
    useEffect(() => {
        ws.current = new WebSocket(socketURL.current);

        ws.current.onopen = () => {
            console.log('Websocket opened. URL: ', socketURL.current);
            ws.current?.send(JSON.stringify({'type': 'token_pls'}));
        }
        ws.current.onclose = () => {
            console.log('Websocket closed. URL: ', socketURL.current);
        }

        ws.current.onmessage = (event) => {
            const j_obj = JSON.parse(event.data);
            const type = j_obj.type;
            const data = j_obj.data;
            switch (type) {
                case 'auth':
                    setToken(data.token);
                    break;
                case 'return':
                    console.log(debugMessage(type, data));
                    setWSMessage(data);
                    break;
                case 'serve_question':
                    console.log(debugMessage(type, data));
                    setQuestions(data);
                    break;
                default:
                    console.log(debugMessage(type, data));
            }
        };

        return () => {
            ws.current.close(1000);
        };
    }, []);

    const propsPackage = {
        webSocket: ws.current,
        userName: userName,
        setUserName: setUserName,
        wsMessage: wsMessage,
        questions: questions,
        setQuestions: setQuestions,
    }

    return (
	<BrowserRouter>
        <div className="App">
            <h1 className="main-title">WebSocket Quiz - Bug, Feature or Tupilaqs</h1>
            <h1 className="main-title">{wsMessage}</h1>
            <Routes>
                <Route path="/" element={<LandingPage{...propsPackage}/>}/>
                <Route path="/categories" element={<Box {...propsPackage} />}/>
            </Routes>
	    </div>
	</BrowserRouter>
    );
}

export default App;
