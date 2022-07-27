import "./style/main.scss";
import {CodeBlock, dracula} from "react-code-blocks";
import {BrowserRouter, Link, Route, Routes} from "react-router-dom"

import React, {useEffect, useRef, useState} from 'react';


const createMessage = (type, data) => {
    return JSON.stringify({ 'type': type, 'data': data});
}

const debugMessage = (type, data) => {
    const date = new Date().toUTCString();
    return `${date} <> tupilaqs <> DEBUG <> ${type} - ${JSON.stringify(data)}`;
}


const LandingPage = (props) =>{
    const { webSocket } = props;
    const [user_name, set_user_name] = useState("")
    const [error, set_error] = useState("")
    const add_new_question = (e) => {
        e.preventDefault();
        if(user_name){
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


                webSocket.send(createMessage('new_question', request))
        }
        else{
            set_error("The user name field must be filled in")
        }

        clearAddQ();
    }

    const check_start_game = () => {
        let itemId = user_name
        if(user_name){
            const request = {
                user: itemId
            }
        }
        else{
            set_error("The username field must be filled in")
        }
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
                <input type="text" value={user_name} onChange={e => set_user_name(e.target.value)} className="input-base" id="itemID" placeholder="Username: "/>
                 <p className="error">{error}</p>
            </div>
            <Link to={user_name ? "/categories" : ""}><button className="bb-button start-button" onClick={check_start_game}>New Game</button></Link>
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
const Box = (props) =>{
    const { webSocket } = props;

    const getQuestion = () => {
        webSocket.send(createMessage('get_question',));
        // TODO: TO BE CONTINUED
    }

    return (
         <div className="box">
                <div className="code-snippet">
                    <MyCoolCodeBlock code={getQuestion} language={"python"}/>
                </div>
                <div className="buttons">
                    <button className="bb-button bug">
                        Bug
                    </button>
                    <button className="bb-button feature">
                        Features
                    </button>
                    <button className="bb-button upload">
                        Upload my own question!
                    </button>
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
    // Tried to define this useState at this level, and then pass the getQuestion reference down to the CodeBox function
    //const [getQuestion, setQuestion] = useState("print('hello world')");
    //FIXME:Did not work: <Route path="/categories" element={CodeBox(getQuestion)}/>

    const [socketURL, setSocketURL] = useState('ws://localhost:8000/quiz');
    const [token, setToken] = useState('');
    const [wsMessage, setWSMessage] = useState(null);
    const ws = useRef(null);

    // Only runs when connection is open and closed.
    useEffect(() => {
        ws.current = new WebSocket(socketURL);

        ws.current.onopen = () => {
            console.log('Websocket opened. URL: ', socketURL);
            ws.current?.send(JSON.stringify({'type': 'token_pls'}))
        }
        ws.current.onclose = () => {
            console.log('Websocket closed. URL: ', socketURL);
        }

        ws.current.onmessage = (event) => {
            const j_obj = JSON.parse(event.data)
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
                default:
                    console.log(debugMessage(type, data));
            }
        };

        return () => {
            ws.current.close(1000);
        };
    }, []);

    return (
	<BrowserRouter>
        <div className="App">
            <h1 className="main-title">WebSocket Quiz - Bug, Feature or Tupilaqs</h1>

            <Routes>
                <Route path="/" element={<LandingPage webSocket={ws.current}/>}/>
                <Route path="/categories" element={<Box webSocket={ws.current} wsMessage={wsMessage}/>} />
            </Routes>
	    </div>
	</BrowserRouter>
    );
}

export default App;
