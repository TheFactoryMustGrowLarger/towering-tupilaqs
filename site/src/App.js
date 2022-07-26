import "./style/main.scss";
import { CodeBlock, dracula } from "react-code-blocks";
import { BrowserRouter, Routes, Route, Link} from "react-router-dom"

import React, { useState, useCallback, useEffect } from 'react';
import useWebSocket, { ReadyState  } from 'react-use-websocket';

export const WebSocketDemo = () => {
  //Public API that will echo messages sent to it back to the client
  const [socketUrl, setSocketUrl] = useState('ws://localhost:8000/ws');
  const [messageHistory, setMessageHistory] = useState([]);

  const { sendMessage, lastMessage, readyState } = useWebSocket(socketUrl);

  useEffect(() => {
    if (lastMessage !== null) {
      setMessageHistory((prev) => prev.concat(lastMessage));
    }
  }, [lastMessage, setMessageHistory]);

  const handleClickChangeSocketUrl = useCallback(
    () => setSocketUrl('ws://localhost:8000/solve_quiz'),
    []
  );

  const handleClickSendMessage = useCallback(() => sendMessage('Hello'), []);

  const connectionStatus = {
    [ReadyState.CONNECTING]: 'Connecting',
    [ReadyState.OPEN]: 'Open',
    [ReadyState.CLOSING]: 'Closing',
    [ReadyState.CLOSED]: 'Closed',
    [ReadyState.UNINSTANTIATED]: 'Uninstantiated',
  }[readyState];

  return (
    <div>
      <button onClick={handleClickChangeSocketUrl}>
        Click Me to change Socket Url
      </button>
      <button
        onClick={handleClickSendMessage}
        disabled={readyState !== ReadyState.OPEN}
      >
        Click Me to send 'Hello'
      </button>
      <span>The WebSocket is currently {connectionStatus}</span>
      {lastMessage ? <span>Last message: {lastMessage.data}</span> : null}
      <ul>
        {messageHistory.map((message, idx) => (
          <span key={idx}>{message ? message.data : null}</span>
        ))}
      </ul>
    </div>
  );
};



const LandingPage = () =>{
    // Note: state is changed from keeping the url to keeping the ws connection object upon user pressing connect button.
    const [getSocket, setSocket] = useState('ws://localhost:8000/ws');

    const connect_event = (event) =>{
	event.preventDefault()
	console.log("connect_event")
        var itemId = document.getElementById("itemID")
        var token = document.getElementById("token")
        var ws = new WebSocket("ws://localhost:8000/new_question/" + itemId.value + "/ws?token=" + token.value);
	setSocket(ws)

        ws.onmessage = function(event) {
            console.log(event.data)
            const data_parsed = JSON.parse(event.data)
	    console.log(data_parsed)
            switch (data_parsed.type) {
            default:
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(data_parsed.data)
                message.appendChild(content)
                messages.appendChild(message)
            }
        };
    }
    const add_new_question = (event) =>{
	event.preventDefault()
	var ws = getSocket

        var new_question_text = document.getElementById("newQuestionText")
        var correct_answer = document.getElementById("correctAnswer")
        var new_question_title = document.getElementById("newQuestionTitle")
        var new_question_explanation = document.getElementById("newQuestionExplanation")
        const request = {
	    type: "new_question",
	    question: new_question_text.value,
	    correct_answer: correct_answer.value,
	    new_question_title: new_question_title.value,
	    new_question_explanation: new_question_explanation.value
	};
	console.log(request)
        ws.send(JSON.stringify(request))

        new_question_text.value = ''
    }

    return (
        <div>
            <div className="inputs registration">
                <input type="text" className="input-base" id="itemID" placeholder="Username: "/>
                <input type="text" className="input-base" id="token" placeholder="Password"/>
                <button className="bb-buton small-height" onClick={(event) => connect_event(event)}>Connect</button>
            </div>
            <Link to="/categories"><button className="bb-buton start-button">Start game</button></Link>
            <h1 className="main-title center">Add custom questions </h1>
            <div className="inputs">
                <input type="text" className="input-base" id="newQuestionText" placeholder="New Question: "/>
                <input type="text" className="input-base" id="correctAnswer" placeholder='"Bug" or "feature":'/>
                <input type="text" className="input-base" id="newQuestionTitle" placeholder="Question title:"/>
                <input type="text" className="input-base" id="newQuestionExplanation" placeholder="Question explanation:"/>
                <button className="bb-buton small-height" onClick={(event) => add_new_question(event)}>Send</button>
            </div>
	    <div className="debug">
		<ul id='messages'>
		</ul>
	    </div>
        </div>
    )
}

//FIXME: Did not work: function CodeBox({ getQuestion }) {
const Box = () =>{
    // function connect(event) {
    //     event.preventDefault()
    //     var itemId = document.getElementById("itemId")
    //     var token = document.getElementById("token")
    //     ws = new WebSocket("ws://localhost:8000/solve_quiz/" + itemId.value + "/ws?token=" + token.value);
    //     ws.onopen = function(event) {
            // const request = {
	    // 	type: "serve_new_question",
            // };
            // ws.send(JSON.stringify(request))
    // };
    // Need to share this at a higher level of the code I think?
    const [getQuestion, setQuestion] = useState("print('hello world')");
    return (
         <div className="box">
                    <div className="code-snippet">
			<MyCoolCodeBlock code={getQuestion}/>
                </div>
                <div className="buttons">
                    <button className="bb-buton bug">
                        Bug
                </button>
                    <button className="bb-buton feature">
                        Features
                    </button>
                    <button className="bb-buton upload">
                        Upload my own question!
                    </button>
                </div>
          </div>

    )
}

function MyCoolCodeBlock({ code, language }) {
  return (<CodeBlock
	      text={code}
	      language={"python"}
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

    return (
	<BrowserRouter>
            <div className="App">
		<h1 className="main-title">WebSocket Quiz - Bug, Feature or Tupilaqs</h1>
		<Routes>
		    <Route path="/categories" element={<Box/>}/>
                    <Route path="/" element={<LandingPage/>}/>
		</Routes>
	    </div>
	</BrowserRouter>
    );
}

export default App;
