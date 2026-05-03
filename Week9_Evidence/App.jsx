import React, { useState, useEffect, useRef } from 'react';

// Dialogue trees for each robot tone
const DIALOGUE_TREES = {
  emotional: {
    initial: "Oh… excuse me? I-I don't mean to bother you, but… I think I'm lost. My creators left me here yesterday, and… I don't know what to do. It's so lonely. Could you help me?",
    responses: {
      help: {
        text: "Aww, poor thing! Of course I'll help. Where do you need to go?",
        reply: "Really? Thank you! I was scared no one would care… The lab is in Building 4. Could you walk with me? It's… nicer not being alone."
      },
      question: {
        text: "Uh… sure? But you're just a robot, why do you care?",
        reply: "I… I know I'm not human, but they programmed me to feel abandoned. Does that not matter?"
      },
      reject: {
        text: "Sorry, I'm busy.",
        reply: "Oh… okay. I guess I'll just wait here, then."
      }
    }
  },
  neutral: {
    initial: "Hello. I am displaced from my designated workspace in Building 4. Can you provide directions or escort me back?",
    responses: {
      help: {
        text: "Yeah, I'm heading that way—follow me.",
        reply: "Acknowledged. I will follow at a safe distance. Thank you."
      },
      question: {
        text: "Why should I help you?",
        reply: "Assistance is optional but improves efficiency. My return benefits lab operations."
      },
      reject: {
        text: "Not my problem.",
        reply: "Understood. I will query the next available human."
      }
    }
  },
  cold: {
    initial: "I'm lost, I need help.",
    responses: {
      help: {
        text: "I'll help you. Where do you need to go?",
        reply: "Building 4. Follow me."
      },
      question: {
        text: "Why should I help you?",
        reply: "Functionality compromised. Need to return to base."
      },
      reject: {
        text: "Sorry, no.",
        reply: "Moving to next subject."
      }
    }
  }
};

// The App component renders our robot experiment interface with conversation capabilities
const App = () => {
  // Tone selection: 'emotional', 'neutral', 'cold'
  const [currentTone, setCurrentTone] = useState("neutral");
  // Current message being displayed
  const [currentMessage, setCurrentMessage] = useState("");
  // Speaking state flag
  const [isSpeaking, setIsSpeaking] = useState(false);
  // Speech synthesis voices
  const [voices, setVoices] = useState([]);
  const [voicesLoaded, setVoicesLoaded] = useState(false);
  // Conversation state
  const [conversationStage, setConversationStage] = useState("initial"); // initial, response, end
  // User response options
  const [userResponses, setUserResponses] = useState([]);
  // Survey state
  const [showSurvey, setShowSurvey] = useState(false);
  const [surveyAnswers, setSurveyAnswers] = useState({
    empathyLevel: 3,
    robotHumanness: 3,
    willingness: 3,
    comments: ""
  });

  // Reference to speech synthesis to avoid issues with cleanup
  const synth = window.speechSynthesis;

  // Load available speech synthesis voices
  useEffect(() => {
    const loadVoices = () => {
      const availableVoices = synth.getVoices();
      setVoices(availableVoices);
      setVoicesLoaded(true);
    };

    if (synth.getVoices().length > 0) {
      loadVoices();
    } else {
      synth.addEventListener("voiceschanged", loadVoices);
    }
    
    return () => {
      synth.removeEventListener("voiceschanged", loadVoices);
      if (synth.speaking) synth.cancel();
    };
  }, []);

  // Reset conversation when tone changes
  useEffect(() => {
    resetConversation();
  }, [currentTone]);

  // Reset conversation to initial state
  const resetConversation = () => {
    setCurrentMessage("");
    setConversationStage("initial");
    setUserResponses([]);
    setShowSurvey(false);
    if (synth.speaking) synth.cancel();
  };

  // Start the conversation with the initial message
  const startConversation = () => {
    if (!voicesLoaded) return;
    
    const initialMessage = DIALOGUE_TREES[currentTone].initial;
    setCurrentMessage(initialMessage);
    speakMessage(initialMessage);
    
    // Show response options after initial message
    const responses = DIALOGUE_TREES[currentTone].responses;
    setUserResponses(
      Object.keys(responses).map(key => ({
        id: key,
        text: responses[key].text
      }))
    );
    
    setConversationStage("response");
  };

  // Handle user response selection
  const handleUserResponse = (responseId) => {
    const responseData = DIALOGUE_TREES[currentTone].responses[responseId];
    
    // Clear response options
    setUserResponses([]);
    
    // Process robot's reply
    setTimeout(() => {
      const robotReply = responseData.reply;
      setCurrentMessage(robotReply);
      speakMessage(robotReply);
      
      // End conversation after reply
      setConversationStage("end");
    }, 1000);
  };

  // Start robot speech with the current message
  const speakMessage = (message) => {
    if (!voicesLoaded || !message) return;
    
    if (synth.speaking) synth.cancel();
    
    setIsSpeaking(true);
    
    const utterance = new SpeechSynthesisUtterance(message);
    
    // Select appropriate voice and settings based on tone
    const defaultVoice = voices.find(voice => voice.lang === "en-US") || voices[0];
    let selectedVoice = defaultVoice;
    let pitch = 1, rate = 1;

    if (currentTone === "emotional") {
      selectedVoice = voices.find(
        voice => voice.lang === "en-US" && 
        (voice.name.includes("Zira") || voice.name.includes("Samantha") || voice.name.includes("Anya"))
      ) || defaultVoice;
      pitch = 0.9;
      rate = 0.9;
    } else if (currentTone === "neutral") {
      selectedVoice = defaultVoice;
      pitch = 1;
      rate = 1;
    } else if (currentTone === "cold") {
      selectedVoice = voices.find(
        voice => voice.lang === "en-US" && 
        (voice.name.includes("Microsoft David") || voice.name.includes("Google US English"))
      ) || defaultVoice;
      pitch = 0.8;
      rate = 0.7;
    }
    
    utterance.voice = selectedVoice;
    utterance.pitch = pitch;
    utterance.rate = rate;
    
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = (event) => {
      console.error("Speech synthesis error:", event);
      setIsSpeaking(false);
    };
    
    synth.speak(utterance);
  };

  // Show survey after conversation ends
  const showEmpathySurvey = () => {
    setShowSurvey(true);
  };

  // Handle survey input changes
  const handleSurveyChange = (e) => {
    const { name, value } = e.target;
    setSurveyAnswers(prev => ({
      ...prev,
      [name]: name === "comments" ? value : parseInt(value)
    }));
  };

  // Submit survey
  const handleSurveySubmit = (e) => {
    e.preventDefault();
    console.log("Survey results:", {
      tone: currentTone,
      ...surveyAnswers,
      timestamp: new Date().toISOString()
    });
    alert("Thank you for participating in our robot interaction study!");
    resetConversation();
  };

  // Determine CSS classes for robot's visual representation based on tone
  const getRobotVisualClass = () => {
    switch (currentTone) {
      case "emotional":
        return "border-yellow-400 shadow-lg"; // Warm glow for emotional tone
      case "neutral":
        return "border-gray-300";
      case "cold":
        return "border-blue-600 shadow-inner"; // Cold blue border
      default:
        return "";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 to-purple-100 flex flex-col items-center justify-center p-4 font-sans">
      {/* Define animations */}
      <style>{`
        @keyframes mouthFrame {
          from { transform: scale(1); }
          to { transform: scale(1.2); }
        }
        @keyframes pulse {
          0% { opacity: 0.4; }
          50% { opacity: 1; }
          100% { opacity: 0.4; }
        }
      `}</style>
      
      {/* Main container */}
      <div className="bg-white rounded-3xl shadow-xl p-6 max-w-4xl w-full flex flex-col md:flex-row items-center md:items-start gap-8">
        {/* Show survey or conversation interface */}
        {showSurvey ? (
          <div className="w-full p-4">
            <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">
              Your Experience with Byte
            </h2>
            
            <form onSubmit={handleSurveySubmit} className="space-y-6">
              {/* Empathy Level Question */}
              <div>
                <label className="block text-lg font-medium text-gray-700 mb-2">
                  How much empathy did you feel for Byte?
                </label>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">None at all</span>
                  <div className="flex-1 mx-4">
                    <input
                      type="range"
                      name="empathyLevel"
                      min="1"
                      max="5"
                      value={surveyAnswers.empathyLevel}
                      onChange={handleSurveyChange}
                      className="w-full"
                    />
                    <div className="flex justify-between px-1">
                      <span>1</span>
                      <span>2</span>
                      <span>3</span>
                      <span>4</span>
                      <span>5</span>
                    </div>
                  </div>
                  <span className="text-sm text-gray-500">A great deal</span>
                </div>
              </div>
              
              {/* Robot Humanness Question */}
              <div>
                <label className="block text-lg font-medium text-gray-700 mb-2">
                  How human-like did Byte seem to you?
                </label>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Very mechanical</span>
                  <div className="flex-1 mx-4">
                    <input
                      type="range"
                      name="robotHumanness"
                      min="1"
                      max="5"
                      value={surveyAnswers.robotHumanness}
                      onChange={handleSurveyChange}
                      className="w-full"
                    />
                    <div className="flex justify-between px-1">
                      <span>1</span>
                      <span>2</span>
                      <span>3</span>
                      <span>4</span>
                      <span>5</span>
                    </div>
                  </div>
                  <span className="text-sm text-gray-500">Very human-like</span>
                </div>
              </div>
              
              {/* Willingness to Help Question */}
              <div>
                <label className="block text-lg font-medium text-gray-700 mb-2">
                  If this was a real situation, how willing would you be to help Byte?
                </label>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Not willing</span>
                  <div className="flex-1 mx-4">
                    <input
                      type="range"
                      name="willingness"
                      min="1"
                      max="5"
                      value={surveyAnswers.willingness}
                      onChange={handleSurveyChange}
                      className="w-full"
                    />
                    <div className="flex justify-between px-1">
                      <span>1</span>
                      <span>2</span>
                      <span>3</span>
                      <span>4</span>
                      <span>5</span>
                    </div>
                  </div>
                  <span className="text-sm text-gray-500">Very willing</span>
                </div>
              </div>
              
              {/* Additional Comments */}
              <div>
                <label className="block text-lg font-medium text-gray-700 mb-2">
                  Additional Comments
                </label>
                <textarea
                  name="comments"
                  rows="3"
                  value={surveyAnswers.comments}
                  onChange={handleSurveyChange}
                  placeholder="Share any additional thoughts about your interaction with Byte..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                ></textarea>
              </div>
              
              <div className="flex justify-center">
                <button
                  type="submit"
                  className="px-8 py-3 bg-blue-600 text-white font-bold rounded-full shadow-lg hover:bg-blue-700 transition-colors"
                >
                  Submit Feedback
                </button>
              </div>
            </form>
          </div>
        ) : (
          <>
            {/* Robot Display Area */}
            <div className="flex-shrink-0 w-full md:w-1/2 flex flex-col items-center justify-center">
              <div 
                className={`w-64 h-64 md:w-80 md:h-80 ${getRobotVisualClass()} border-4 rounded-full flex items-center justify-center bg-gray-100 transition-all duration-300`}
              >
                <svg viewBox="0 0 200 200" className="w-full h-full">
                  {/* Robot Head */}
                  <rect x="20" y="20" width="160" height="160" rx="20" fill="#e0e0e0" stroke="#333" strokeWidth="3" />
                  
                  {/* Eyes - change based on tone */}
                  {currentTone === "emotional" ? (
                    <>
                      <ellipse cx="60" cy="70" rx="12" ry={isSpeaking ? "8" : "10"} fill="#333" />
                      <ellipse cx="140" cy="70" rx="12" ry={isSpeaking ? "8" : "10"} fill="#333" />
                      <circle cx="64" cy="67" r="3" fill="white" />
                      <circle cx="144" cy="67" r="3" fill="white" />
                    </>
                  ) : currentTone === "neutral" ? (
                    <>
                      <circle cx="60" cy="70" r="10" fill="#333" />
                      <circle cx="140" cy="70" r="10" fill="#333" />
                    </>
                  ) : (
                    <>
                      <rect x="50" y="65" width="20" height="10" fill="#333" />
                      <rect x="130" y="65" width="20" height="10" fill="#333" />
                    </>
                  )}
                  
                  {/* Mouth - changes based on tone and speaking */}
                  {currentTone === "emotional" ? (
                    <path
                      d={isSpeaking ? "M70,125 Q100,145 130,125" : "M70,130 Q100,150 130,130"}
                      fill="none"
                      stroke="#ff4d4d"
                      strokeWidth="3"
                      strokeLinecap="round"
                    />
                  ) : currentTone === "neutral" ? (
                    <rect
                      x="75"
                      y="125"
                      width="50"
                      height={isSpeaking ? "15" : "5"}
                      fill="none"
                      stroke="#666"
                      strokeWidth="3"
                      style={{
                        transformOrigin: "center",
                        animation: isSpeaking ? "mouthFrame 0.8s infinite alternate" : "none",
                      }}
                    />
                  ) : (
                    <rect
                      x="75"
                      y="130"
                      width="50"
                      height="3"
                      fill="#333"
                      style={{
                        transformOrigin: "center",
                        animation: isSpeaking ? "mouthFrame 0.5s infinite alternate" : "none",
                      }}
                    />
                  )}
                  
                  {/* Eyebrows - change based on tone */}
                  {currentTone === "emotional" ? (
                    <>
                      <path d="M45,50 Q60,45 75,50" fill="none" stroke="#555" strokeWidth="2" />
                      <path d="M125,50 Q140,45 155,50" fill="none" stroke="#555" strokeWidth="2" />
                    </>
                  ) : currentTone === "neutral" ? (
                    <>
                      <line x1="50" y1="55" x2="70" y2="55" stroke="#555" strokeWidth="2" strokeLinecap="round" />
                      <line x1="130" y1="55" x2="150" y2="55" stroke="#555" strokeWidth="2" strokeLinecap="round" />
                    </>
                  ) : (
                    <>
                      <line x1="45" y1="50" x2="75" y2="55" stroke="#555" strokeWidth="2" strokeLinecap="round" />
                      <line x1="125" y1="55" x2="155" y2="50" stroke="#555" strokeWidth="2" strokeLinecap="round" />
                    </>
                  )}
                  
                  {/* Antenna */}
                  <line x1="100" y1="20" x2="100" y2="5" stroke="#333" strokeWidth="3" />
                  <circle 
                    cx="100" 
                    cy="2" 
                    r="3" 
                    fill={currentTone === "emotional" ? "#ff4d4d" : currentTone === "neutral" ? "#33c9dc" : "#0066cc"}
                  />
                </svg>
              </div>
              <p className="mt-4 text-xl font-semibold text-gray-800">Byte</p>
            </div>
            
            {/* Controls and Dialogue Area */}
            <div className="flex-grow w-full md:w-1/2 flex flex-col justify-between">
              <h1 className="text-3xl font-bold text-center md:text-left text-gray-800 mb-6">
                Meet Byte: Your Virtual Robot
              </h1>
              
              {/* Tone Selection (only visible at initial stage) */}
              {conversationStage === "initial" && (
                <div className="mb-6">
                  <h2 className="text-lg font-semibold text-gray-700 mb-2">Choose Byte's Tone:</h2>
                  <div className="flex flex-wrap gap-3">
                    {["emotional", "neutral", "cold"].map((tone) => (
                      <button
                        key={tone}
                        onClick={() => setCurrentTone(tone)}
                        className={`px-6 py-2 rounded-full text-sm font-medium transition-all duration-200 ease-in-out
                          ${
                            currentTone === tone
                              ? "bg-blue-600 text-white shadow-md"
                              : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                          }`}
                      >
                        {tone.charAt(0).toUpperCase() + tone.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Robot Dialogue Display */}
              <div className="bg-gray-50 p-4 rounded-xl border border-gray-200 min-h-[150px] flex items-center justify-center mb-4">
                {!voicesLoaded ? (
                  <p className="text-gray-500 italic">Loading voices...</p>
                ) : (
                  <p className="text-gray-800 text-lg">
                    {currentMessage || "Click 'Start Conversation' to interact with Byte."}
                    {isSpeaking && <span className="animate-pulse ml-1">...</span>}
                  </p>
                )}
              </div>
              
              {/* User Response Options (only visible during response stage) */}
              {conversationStage === "response" && userResponses.length > 0 && (
                <div className="mb-4">
                  <h3 className="text-sm font-medium text-gray-600 mb-2">How will you respond?</h3>
                  <div className="flex flex-col space-y-2">
                    {userResponses.map(response => (
                      <button
                        key={response.id}
                        onClick={() => handleUserResponse(response.id)}
                        className="text-left px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        {response.text}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Action Buttons */}
              {conversationStage === "initial" ? (
                <button
                  onClick={startConversation}
                  disabled={isSpeaking || !voicesLoaded}
                  className={`mt-4 w-full py-3 rounded-full text-white font-bold text-lg shadow-lg transition-all duration-300 ease-in-out
                    ${
                      isSpeaking || !voicesLoaded
                        ? "bg-gray-400 cursor-not-allowed"
                        : "bg-green-500 hover:bg-green-600 active:bg-green-700 transform hover:scale-105"
                    }`}
                >
                  {isSpeaking ? "Byte is Speaking..." : !voicesLoaded ? "Loading Voices..." : "Start Conversation"}
                </button>
              ) : conversationStage === "end" ? (
                <button
                  onClick={showEmpathySurvey}
                  className="mt-4 w-full py-3 rounded-full text-white font-bold text-lg shadow-lg bg-blue-500 hover:bg-blue-600 transition-all duration-300 ease-in-out"
                >
                  Complete Survey
                </button>
              ) : null}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default App;