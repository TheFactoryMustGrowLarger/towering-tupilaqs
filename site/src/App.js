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
 * - 'get_question'
 * - TODO: Needs to be implemented more
 *  - 'token_pls' - gets token for security
 * @param {String} type
 * @param {Object} data
 *
 * @returns {String}
 */
const createMessage = (type, data) => {

    return JSON.stringify({ 'type': type, 'data': data});
}

/**
 * @description Makes debug messages
 * @param {String} type
 * @param {Object} data
 *
 * @returns {`${String} <> tupilaqs <> DEBUG <> ${String} - ${String}`}
 */
const debugMessage = (type, data) => {
    const date = new Date().toUTCString();
    return `${date} <> tupilaqs <> DEBUG <> ${type} - ${JSON.stringify(data)}`;
}

/**
 * @description CHANGE ME
 *
 * @param {WebSocket} webSocket
 * @param {Function} setUserName
 * @param {String} userName
 *
 * @returns {JSX.Element}
 * @constructor
 */
const LandingPage = ({ webSocket, setUserName, userName}) => {
    const [error, setError] = useState("")

    const [NewQuestionText, SetNewQuestionText] = useState("")
    const [CorrectAnswer, SetCorrectAnswer] = useState("")
    const [NewQuestionTitle, SetNewQuestionTitle] = useState("")
    const [NewQuestionExplanation, SetNewQuestionExplanation] = useState("")


    const add_new_question = (e) => {
        e.preventDefault();
        if (userName) {
            CheckQuestionField()

        } else {
            setError("The user name field must be filled in!")
        }

        clearAddQ();
    }

    const clearAddQ = () => {
        SetNewQuestionText("")
        SetNewQuestionTitle("")
        SetCorrectAnswer("")
        SetNewQuestionExplanation("")
    }

    const CheckUsernameField = () => {
        if(userName === ""){
            setError("The username field must be filled in!")
        }

    }
    const CheckQuestionField = () => {
        if(NewQuestionText && NewQuestionTitle && CorrectAnswer && NewQuestionExplanation !== ""){
                const request = {
                    user: userName,
                    question: NewQuestionText,
                    correct_answer: CorrectAnswer,
                    new_question_title: NewQuestionTitle,
                    new_question_explanation: NewQuestionExplanation,

                };
          webSocket.send(createMessage('insert_new_question', request))
        }
        else{
            setError("The Questions field must be filled in!")
        }
    }
    return (
        <div>
            <div className="inputs registration">
                <input type="text" value={userName} onChange={e => setUserName(e.target.value)} className="input-base" id="itemID" placeholder="Username: "/>

            </div>
            <Link to={userName ? "/categories" : ""}><button onClick={CheckUsernameField} className="bb-button start-button">New Game</button></Link>
            <h1 className="main-title center">Add custom questions </h1>
            <div className="inputs">
                <input type="text" value={NewQuestionText} onChange={e => SetNewQuestionText(e.target.value)} className="input-base" id="newQuestionText" placeholder="New Question: "/>
                <input type="text" value={CorrectAnswer} onChange={e => SetCorrectAnswer((e.target.value))} className="input-base" id="correctAnswer" placeholder='"Bug" or "feature":'/>
                <input type="text" value={NewQuestionTitle} onChange={e => SetNewQuestionTitle((e.target.value))} className="input-base" id="newQuestionTitle" placeholder="Question title:"/>
                <input type="text" value={NewQuestionExplanation} onChange={e => SetNewQuestionExplanation((e.target.value))} className="input-base" id="newQuestionExplanation" placeholder="Question explanation:"/>
                <button className="bb-button small-height"  onClick={(e) => add_new_question(e)}>Send</button>

            </div>

            <div className="debug">
                <ul id='messages'>
                    <h2 className="main-title center">Current token from Server: {}</h2>
                </ul>
            </div>
            <div className="errors">
               <p >{error}</p>
            </div>

        </div>
    )
}

/**
 * Testing func
 *
 * @param {WebSocket} webSocket
 * @param {String} userName
 * @param {String} wsMessage
 * @param {Function} getExplanation
 * @param {Function} setSQuestion
 * @param {Object} singleQuestion
 * @param {String} singleQuestion.txt - The question
 * @param {String} singleQuestion.title - Title
 * @param {String} singleQuestion.expl - For cheating
 * @param {Number} singleQuestion.difficulty - How difficulty the question is
 * @param {Number} singleQuestion.votes - Amount of votes
 * @param {String} singleQuestion.ident - identifier
 *
 * @returns {JSX.Element}
 * @constructor
 */
const Box = ({ webSocket, userName, setUserName, singleQuestion, setSQuestion, getExplanation, getVotes }) => {

    const handleNextQuestions = () => {
        if (userName.length > 0) {
            const data = {
                'user_name': userName,
            }
            localStorage.setItem('username', userName);
            webSocket?.send(createMessage('get_question', data));
        } else {
            // use localstorage
            const data = {
                'user_name': localStorage.getItem('username'),
            }
            webSocket?.send(createMessage('get_question', data));
        }
    }

    useEffect(() => {
        if (webSocket === null) return;


        if (webSocket.readyState === 1 && (userName !== '' || userName !== undefined)) {
            console.log("startgame will be ran");
            handleNextQuestions();
        }
    }, [webSocket?.readyState]);



    /**
     * @description Sends the guess of the player to backend to verify.
     * @param {MouseEvent} e
     * @param {string} guess
     */
    const handleGuess = (e, guess) => {
        e.preventDefault();

        const data = {
            'user_name': userName,
	        'question_uuid': singleQuestion?.ident,
	        'user_answer': guess
        }
        webSocket?.send(createMessage('answered_question', data));
    }

    const handleVote = (e, vote) => {
        e.preventDefault();

        const data = {
	    'user_name': userName,
            'question_uuid': singleQuestion?.ident,
            'vote': vote
        }

        webSocket?.send(createMessage('vote_question', data));
    }

    return (
        <>
        {singleQuestion.title ?
        <div className="box">
            <div>
                <h1 className="main-title">{singleQuestion?.title}</h1>
            </div>
            <div style={
                {
                    display: singleQuestion?.title.toLowerCase().includes('you have answered all questions')
                            ? "none": ""
                }}>
                <h4 style={{maxWidth: '550px', color: '#FFC0CB'}}>
                    {getExplanation}
                </h4>
                <br />
                <h4 style={{color: '#FFC0CB'}}>
                    Difficulty: {singleQuestion?.difficulty}
                </h4>
                <h4 style={{maxWidth: '550px', color: '#FFC0CB'}}>
                    Votes: {getVotes}
                </h4>
                <span>
                    <button onClick={(e) => handleVote(e, 'add')}>
                        Upvote question
                    </button>
                </span>
            </div>
            <div className="code-snippet">
                <MyCoolCodeBlock code={String(singleQuestion.txt)} language={"python"}/>
            </div>
            <div style={{display: !getExplanation && "none"}}>
                <button onClick={(e) => handleNextQuestions(e)}>Next question</button>
            </div>
            <div style={
                {
                    display: getExplanation? "none": "flex",
                    justifyContent:
                        singleQuestion?.title.toLowerCase().includes('you have answered all questions')
                            ? "center": ""
                }
            } className="buttons">
                <div style={
                    {
                        display: singleQuestion?.title.toLowerCase().includes('you have answered all questions')
                            ? "none": "flex"
                    }
                }>
                    <button className="bb-button bug" onClick={(e) => handleGuess(e, 'bug')}>
                        Bug
                    </button>
                    <button className="bb-button feature" onClick={(e) => handleGuess(e, 'feature')}>
                        Feature
                    </button>
                </div>
                <Link to="/">
                    <button className="bb-button upload">
                        Upload my own question!
                    </button>
                </Link>
            </div>
        </div> : <div className="box">Loading...</div>}
        </>

    )
}

/**
 * @description CHANGE ME
 *
 * @param code
 * @param language
 * @returns {JSX.Element}
 *
 * @constructor
 */
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
    const socketURL = useRef('ws://localhost:8000/quiz');
    const ws = useRef(null);
    const [token, setToken] = useState('');
    const [wsMessage, setWSMessage] = useState('');
    const [questions, setQuestions] = useState([]);
    const [userName, setUserName] = useState('');
    const [getExplanation, setExplanation] = useState('');
    const [getVotes, setVotes] = useState('0');
    const [singleQuestion, setSQuestion] = useState({});

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
                    console.log(debugMessage(type, JSON.parse(data)));
                    setQuestions(oldArray => [...oldArray, data]);
                    setSQuestion(JSON.parse(data));
		    setExplanation('');
                    break;
                case 'answered_question_feedback':
                    console.log(debugMessage(type, data));
		    setExplanation(data)
                    break;
                case 'vote_feedback':
                    console.log(debugMessage(type, data));
		    setVotes(data['votes'].toString())
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
        getExplanation: getExplanation,
	getVotes: getVotes,
        setExplanation: setExplanation,
        singleQuestion: singleQuestion,
        setSQuestion: setSQuestion,
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
