import React from "react";
import "./style/main.scss";
import { CodeBlock, dracula } from "react-code-blocks";
import { BrowserRouter, Routes, Route, Link} from "react-router-dom"
import {useState, useCallback, useEffect} from "react";
import useWebSocket, { ReadyState } from 'react-use-websocket';

export const WebSocketDemo = () => {
    //Public API that will echo messages sent to it back to the client
    const [socketUrl, setSocketUrl] = useState('wss://echo.websocket.org');
    const [messageHistory, setMessageHistory] = useState([]);

    const {sendMessage, lastMessage, readyState} = useWebSocket(socketUrl);

    useEffect(() => {
        if (lastMessage !== null) {
            setMessageHistory((prev) => prev.concat(lastMessage));
        }
    }, [lastMessage, setMessageHistory]);

    const handleClickChangeSocketUrl = useCallback(
        () => setSocketUrl('wss://demos.kaazing.com/echo'),
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
      <span className="debug-color">The WebSocket is currently {connectionStatus}</span>
      {lastMessage ? <span>Last message: {lastMessage.data}</span> : null}
      <ul>
        {messageHistory.map((message, idx) => (
          <span key={idx}>{message ? message.data : null}</span>
        ))}
      </ul>
    </div>
  );
};



const Categories = () => {
    return(
        <div className="flex">
            <button>1</button>
            <button>2</button>
            <button>3</button>
        </div>
    )
}

const LandingPage = () =>{
    return (
        <div>
            <Link to="/categories"><button className="bb-buton start-button">Start game</button></Link>
        </div>


    )
}

const Box = () =>{
    return (
         <div className="box">
                    <div className="code-snippet">
                    <MyCoolCodeBlock code={`class Dog:
                          #init creates certain parameters that allow you to define information quickly.
                          def __init__(self, name):
                            self.name = name

                          def get_name(self):
                        \treturn self.name

                        if __name__ == "__main__":
                          d = Dog(str(input("name your dog: "))
                          print(d.get_name())
                          `} language={"python"} showLineNumbers={true} startingLineNumber={1} theme={dracula} />
                </div>
                <div className="buttons">
                    <button className="bb-buton bug">
                        Bug
                </button>
                    <button className="bb-buton feature">
                        Features
                    </button>
                    <button className="bb-buton upload">
                        Upload my own question
                    </button>
                </div>
          </div>

    )
}

function MyCoolCodeBlock({ code, language, showLineNumbers, startingLineNumber }) {
  return (<CodeBlock
    text={code}
    language={language}
    showLineNumbers={showLineNumbers}
    startingLineNumber={startingLineNumber}
    theme={dracula}
    codeBlock
  />);
}

function App() {
  return (
      <BrowserRouter>
          <div className="App">
              <h1 className="main-title">WebSocket Quiz - Bug, Feature or Tupilaqs</h1>
              <Routes>
                  <Route path="/categories/:category" element={<Box/>}/>
                  <Route path="/" element={<LandingPage/>}/>
                  <Route path="/categories" element={<Categories/>}/>
              </Routes>
    </div>
      </BrowserRouter>

  );
}

export default App;
